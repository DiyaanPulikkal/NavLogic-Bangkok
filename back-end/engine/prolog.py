"""
prolog.py — pyswip wrapper.

Responsibilities (in order of importance):

  1. Goal serialization: turn the recursive-dict goal that the LLM emits
     into a Prolog term string for the rulebook to evaluate. This is the
     ONE place where the open vocabulary crosses into Prolog syntax.
  2. Logical-form queries: candidates/unknown_tags/relax/audit on top of
     rules.pl, returning JSON-shaped Python.
  3. Surface helpers: name matching, edge enumeration, symbolic route
     segmentation, vocabulary export for the LLM system prompt.

The wrapper does no reasoning of its own — it serializes, queries, and
parses results. All inference lives in the .pl files.
"""

from __future__ import annotations

import logging
import os
import re
from itertools import islice

# Homebrew SWI-Prolog may install libs outside pyswip's default search path.
if not os.environ.get("LIBSWIPL_PATH") or not os.environ.get("SWI_HOME_DIR"):
    import glob as _glob

    for _swipl_dir in _glob.glob("/opt/homebrew/Cellar/swi-prolog/*/lib/swipl"):
        _dylib = os.path.join(_swipl_dir, "lib", "arm64-darwin", "libswipl.dylib")
        if os.path.isfile(_dylib):
            os.environ.setdefault("LIBSWIPL_PATH", _dylib)
            os.environ.setdefault("SWI_HOME_DIR", _swipl_dir)
            break

from pyswip import Prolog

logger = logging.getLogger("prolog")

KB_PATH = os.path.join(os.path.dirname(__file__), "knowledge_base.pl")


class GoalShapeError(ValueError):
    """Raised when a dict goal cannot be serialized to a Prolog term."""


class TimeShapeError(ValueError):
    """Raised when a time_context dict cannot be serialized to a t/3 term."""


class BudgetShapeError(ValueError):
    """Raised when a budget_context dict is malformed."""


class FareUnknownError(RuntimeError):
    """Raised when a path segment has no fare entry in fares.pl.

    Mirrors the Prolog throw `fare_unknown(Agency, A, B)`. Propagated
    up so the orchestrator can decide whether to surface or re-route.
    """

    def __init__(self, agency: str, origin: str, destination: str):
        self.agency = agency
        self.origin = origin
        self.destination = destination
        super().__init__(f"No fare known for {agency} segment {origin} → {destination}")


_WEEKDAY_CANON = {
    "mon": "mon", "monday": "mon",
    "tue": "tue", "tues": "tue", "tuesday": "tue",
    "wed": "wed", "wednesday": "wed",
    "thu": "thu", "thur": "thu", "thurs": "thu", "thursday": "thu",
    "fri": "fri", "friday": "fri",
    "sat": "sat", "saturday": "sat",
    "sun": "sun", "sunday": "sun",
}


class PrologInterface:
    GOAL_OPS_LIST = {"and", "or"}
    GOAL_OPS_TAGLIST = {"any_tag", "all_tag", "none_tag", "prefer_tag"}
    GOAL_OPS_SINGLE = {"not"}
    GOAL_OPS_ATOM = {"route_to"}

    def __init__(self):
        self.prolog = Prolog()
        self.prolog.consult(KB_PATH)

    # ------------------------------------------------------------------
    # Name resolution (symbolic classification only; ranking in Python).
    # ------------------------------------------------------------------

    def match_station_classified(self, name: str) -> list[dict]:
        """Return [{station, match_type}, ...] via match_station/3.

        match_type ∈ {exact, prefix, substring}; deduplicated across lines.
        """
        safe_name = name.replace("'", "\\'")
        query = f"match_station('{safe_name}', Station, MatchType)"
        logger.info("Executing Prolog query: %s", query)
        seen, out = set(), []
        for r in self.prolog.query(query):
            station = str(r["Station"])
            if station in seen:
                continue
            seen.add(station)
            out.append({"station": station, "match_type": str(r["MatchType"])})
        return out

    def is_valid_station(self, name: str) -> bool:
        safe_name = name.replace("'", "\\'")
        return bool(list(islice(self.prolog.query(f"valid_station('{safe_name}')"), 1)))

    def get_all_station_names(self) -> list[str]:
        return sorted({str(r["S"]) for r in self.prolog.query("station(S, _)")})

    def get_stations_with_lines(self) -> list[dict]:
        """Return [{name, lines}, ...] grouped from station/2 facts."""
        by_station: dict[str, set[str]] = {}
        for r in self.prolog.query("station(S, L)"):
            by_station.setdefault(str(r["S"]), set()).add(str(r["L"]))
        return [
            {"name": name, "lines": sorted(lines)}
            for name, lines in sorted(by_station.items())
        ]

    def get_all_pois(self) -> list[dict]:
        """Return [{name, station, tags}, ...] joining poi/3 with tagged/2."""
        out: list[dict] = []
        seen: set[str] = set()
        for r in self.prolog.query("poi(Id, Name, Station), tagged(Id, Tags)"):
            pid = str(r["Id"])
            if pid in seen:
                continue
            seen.add(pid)
            out.append({
                "name": str(r["Name"]),
                "station": str(r["Station"]),
                "tags": [str(t) for t in r["Tags"]],
            })
        out.sort(key=lambda p: p["name"])
        return out

    # ------------------------------------------------------------------
    # Graph (consumed by Python's Dijkstra).
    # ------------------------------------------------------------------

    def get_all_edges(self) -> list[tuple[str, str, int]]:
        """Bidirectional edges (A, B, time_minutes)."""
        return [
            (str(r["A"]), str(r["B"]), int(r["T"]))
            for r in self.prolog.query("edge(A, B, T)")
        ]

    def station_agencies(self) -> dict[str, str]:
        """Station → agency atom. Drives agency-aware edge pruning in
        the budget repair loop. Queries station_agency/2 from rules.pl.
        """
        out: dict[str, str] = {}
        for r in self.prolog.query("station_agency(S, A)"):
            station = str(r["S"])
            agency = str(r["A"])
            out.setdefault(station, agency)
        return out

    # ------------------------------------------------------------------
    # Symbolic route segmentation (route_steps/2).
    # ------------------------------------------------------------------

    def build_route_steps(self, path: list[str]) -> list[dict]:
        """Group a station path into ride + transfer step dicts."""
        if len(path) < 2:
            return []
        path_term = "[" + ",".join(self._quote_atom(s) for s in path) + "]"
        query = f"route_steps({path_term}, Steps)"
        logger.info("Executing Prolog query: %s", query)
        results = list(self.prolog.query(query))
        if not results:
            return []
        return [self._step_term_to_dict(s) for s in results[0]["Steps"]]

    # ------------------------------------------------------------------
    # Vocabulary surface (fed to the LLM system prompt each call).
    # ------------------------------------------------------------------

    def active_tag_vocabulary(self) -> list[str]:
        """Canonical tags the LLM can emit.

        Union of (a) tags actually attached to POIs, (b) synonym targets,
        (c) supertypes from subtag/2. Deduplicated and sorted so the LLM
        sees a stable ordering across calls.
        """
        tags: set[str] = set()
        for r in self.prolog.query("tagged(_, Tags)"):
            tags.update(str(t) for t in r["Tags"])
        for r in self.prolog.query("synonym(_, T)"):
            tags.add(str(r["T"]))
        for r in self.prolog.query("subtag(_, T)"):
            tags.add(str(r["T"]))
        for r in self.prolog.query("subtag(T, _)"):
            tags.add(str(r["T"]))
        return sorted(tags)

    def active_synonyms(self) -> dict[str, str]:
        """Raw → canonical mapping (open-vocabulary surface for the LLM)."""
        out: dict[str, str] = {}
        for r in self.prolog.query("synonym(Raw, Canon)"):
            out[str(r["Raw"])] = str(r["Canon"])
        return out

    def active_time_specs(self) -> list[str]:
        """Closed-vocabulary temporal specs the LLM can emit.

        Mirrors active_tag_vocabulary for the time layer: returns every
        atom S for which time_matches(S, _) has a defining clause, so
        the LLM's system prompt can enumerate the legal specs without
        free-form invention.
        """
        results = list(self.prolog.query("time_spec_vocab(V)"))
        if not results:
            return []
        return sorted({str(s) for s in results[0]["V"]})

    # ------------------------------------------------------------------
    # Logical-form queries (the open-vocabulary core).
    # ------------------------------------------------------------------

    def candidates(self, goal: dict, time_ctx: dict) -> list[dict]:
        """POIs satisfying `goal` under `time_ctx`, each with its preference score.

        Inlines the findall as a direct conjunctive query so we get
        bound variables (Id, Name, Station, Score) without parsing
        Prolog list/pair terms. The time term is threaded alongside
        the goal — it lives outside the goal tree because the temporal
        context is a per-query frame, not a subgoal.
        """
        goal_term = self._goal_to_prolog(goal)
        time_term = self._time_to_prolog(time_ctx)
        query = (
            f"poi(Id, Name, Station), "
            f"satisfies(Id, {goal_term}, {time_term}), "
            f"preference_score(Id, {goal_term}, {time_term}, Score)"
        )
        logger.info("Executing Prolog query: %s", query)
        seen, out = set(), []
        for r in self.prolog.query(query):
            pid = str(r["Id"])
            if pid in seen:
                continue
            seen.add(pid)
            out.append({
                "id": pid,
                "name": str(r["Name"]),
                "station": str(r["Station"]),
                "pref_score": int(r["Score"]),
            })
        return out

    def unknown_tags(self, goal: dict) -> list[str]:
        """Tags in `goal` that bind to unknown(_) — i.e. neither a synonym
        nor a recognized canonical tag. Empty list means vocabulary is fine.
        """
        goal_term = self._goal_to_prolog(goal)
        query = f"unknown_tags({goal_term}, Unknowns)"
        logger.info("Executing Prolog query: %s", query)
        results = list(self.prolog.query(query))
        if not results:
            return []
        return [str(t) for t in results[0]["Unknowns"]]

    def relax(self, goal: dict, time_ctx: dict) -> tuple[list[str], list[dict]] | None:
        """Minimal-drop relaxation when `candidates(goal, time_ctx)` is empty.

        Returns (dropped_subgoal_strings, survivor_candidates) or None.
        Dropped subgoals come back as Prolog term strings (e.g.
        "none_tag([weather_exposed])"); the LLM narrates them in plain
        English using the system-prompt formatting instructions. The
        time term is threaded so a conjunct rejected purely because
        its spec failed under the current frame (e.g. `any_tag([night_market])`
        at 10 AM) still surfaces as the minimal drop.
        """
        goal_term = self._goal_to_prolog(goal)
        time_term = self._time_to_prolog(time_ctx)
        query = f"relax({goal_term}, {time_term}, Drop, Survivors)"
        logger.info("Executing Prolog query: %s", query)
        results = list(islice(self.prolog.query(query), 1))
        if not results:
            return None
        dropped = [str(d) for d in results[0]["Drop"]]
        survivors = self._parse_candidate_pairs(results[0]["Survivors"])
        return (dropped, survivors)

    # ------------------------------------------------------------------
    # Fiscal reasoning bridge (the symbolic-repair oracle surface).
    # ------------------------------------------------------------------

    def trip_fare(self, path: list[str]) -> tuple[list[dict], int]:
        """Return (segments, total_THB) for a station path.

        segments = [{agency, tap_in, tap_out, fare}, ...] — one entry
        per maximal same-agency run. Raises FareUnknownError when a
        run has no fare entry in the CSV-derived fares.pl.
        """
        if not path:
            return ([], 0)
        path_term = "[" + ",".join(self._quote_atom(s) for s in path) + "]"
        query = f"trip_fare({path_term}, Segments, Total)"
        logger.info("Executing Prolog query: %s", query)
        try:
            results = list(self.prolog.query(query))
        except Exception as exc:
            self._reraise_fare_unknown(exc)
            raise
        if not results:
            return ([], 0)
        raw_segments = results[0]["Segments"]
        total = int(results[0]["Total"])
        segs_out: list[dict] = []
        for seg in raw_segments:
            parsed = self._parse_segment(str(seg))
            if parsed is None:
                continue
            agency, tap_in, tap_out = parsed
            fare = self._segment_fare(agency, tap_in, tap_out)
            segs_out.append({
                "agency": agency,
                "tap_in": tap_in,
                "tap_out": tap_out,
                "fare": fare,
            })
        return (segs_out, total)

    def diagnose_budget(self, path: list[str], budget_max: int) -> dict:
        """Structural diagnosis of whether `path` fits `budget_max`.

        Returns either:
          {"kind": "within_budget", "total": int}
          {"kind": "over_budget", "total": int, "overage": int,
           "segments": [...], "boundaries": [...]}

        boundaries = [{a, b, agency_a, agency_b}, ...] enumerating the
        inter-agency crossings along the path. These are the repair
        handles — propose_repair/3 reasons over this structure.
        """
        if not path:
            return {"kind": "within_budget", "total": 0}
        path_term = "[" + ",".join(self._quote_atom(s) for s in path) + "]"
        query = (
            f"diagnose_budget({path_term}, {int(budget_max)}, D), "
            f"term_to_atom(D, DA)"
        )
        logger.info("Executing Prolog query: %s", query)
        try:
            results = list(self.prolog.query(query))
        except Exception as exc:
            self._reraise_fare_unknown(exc)
            raise
        if not results:
            return {"kind": "within_budget", "total": 0}
        return self._parse_diagnosis(str(results[0]["DA"]))

    def propose_repair(self, path: list[str], budget_max: int, tried: list[dict]) -> dict:
        """Ask Prolog for the next structural repair given the current path.

        Re-runs diagnose_budget/3 then propose_repair/3 in one query so
        the failure analysis and the repair proposal are atomically
        consistent. Returns a repair dict whose `kind` is one of:
          "avoid_specific_boundary" | "avoid_agency_pair"
          | "force_single_agency"    | "infeasible"
        """
        if not path:
            return {"kind": "infeasible", "reason": "empty_path"}
        path_term = "[" + ",".join(self._quote_atom(s) for s in path) + "]"
        tried_term = self._repairs_to_prolog_list(tried)
        query = (
            f"diagnose_budget({path_term}, {int(budget_max)}, D), "
            f"propose_repair(D, {tried_term}, R), "
            f"term_to_atom(R, RA)"
        )
        logger.info("Executing Prolog query: %s", query)
        try:
            results = list(self.prolog.query(query))
        except Exception as exc:
            self._reraise_fare_unknown(exc)
            raise
        if not results:
            return {"kind": "infeasible", "reason": "no_diagnosis"}
        return self._parse_repair(str(results[0]["RA"]))

    def explain_infeasibility(
        self,
        trail: list[dict],
        last_diagnosis: dict | str,
    ) -> dict:
        """Emit the Prolog-authored infeasibility certificate.

        `trail` is the list of repair dicts applied in order.
        `last_diagnosis` is either the last over_budget dict (for
        exhausted-hierarchy failures) or the literal string
        "graph_disconnected" (for prune-disconnected failures).
        """
        trail_term = "[" + ",".join(
            self._repair_to_prolog(self._trail_entry_repair(r)) for r in trail
        ) + "]"
        if isinstance(last_diagnosis, str) and last_diagnosis == "graph_disconnected":
            last_term = "graph_disconnected"
        else:
            total = int(last_diagnosis.get("total", 0))
            overage = int(last_diagnosis.get("overage", 0))
            last_term = f"over_budget({total},{overage},[],[])"
        query = (
            f"explain_infeasibility({trail_term}, {last_term}, C), "
            f"term_to_atom(C, CA)"
        )
        logger.info("Executing Prolog query: %s", query)
        results = list(self.prolog.query(query))
        if not results:
            return {"kind": "certificate", "raw": "unavailable"}
        return self._parse_certificate(str(results[0]["CA"]))

    def _segment_fare(self, agency: str, tap_in: str, tap_out: str) -> int:
        if tap_in == tap_out:
            return 0
        a_q = self._quote_atom(tap_in)
        b_q = self._quote_atom(tap_out)
        query = f"segment_fare(segment({agency},{a_q},{b_q}), P)"
        try:
            results = list(self.prolog.query(query))
        except Exception as exc:
            self._reraise_fare_unknown(exc)
            raise
        if not results:
            raise FareUnknownError(agency, tap_in, tap_out)
        return int(results[0]["P"])

    def audit_route_for_path(self, path: list[str], goal: dict) -> list[dict]:
        """Audit a path against `goal`'s hard constraints.

        Composes route_steps/2 + audit_route/3 in one query. Returns
        [{step, reason}, ...] — empty when the route is clean.
        """
        if len(path) < 2:
            return []
        goal_term = self._goal_to_prolog(goal)
        path_term = "[" + ",".join(self._quote_atom(s) for s in path) + "]"
        query = (
            f"route_steps({path_term}, Steps), "
            f"audit_route(Steps, {goal_term}, Violations)"
        )
        logger.info("Executing Prolog query: %s", query)
        results = list(self.prolog.query(query))
        if not results:
            return []
        out = []
        for v in results[0]["Violations"]:
            parsed = self._parse_violation(str(v))
            if parsed is not None:
                out.append(parsed)
        return out

    # ------------------------------------------------------------------
    # Goal → Prolog term serialization (the open→closed bridge).
    # ------------------------------------------------------------------

    @classmethod
    def _goal_to_prolog(cls, goal: dict) -> str:
        if not isinstance(goal, dict) or len(goal) != 1:
            raise GoalShapeError(
                f"Goal must be a single-key dict, got: {goal!r}"
            )
        op, arg = next(iter(goal.items()))
        if op in cls.GOAL_OPS_LIST:
            if not isinstance(arg, list):
                raise GoalShapeError(f"{op} requires a list of subgoals")
            sub = ",".join(cls._goal_to_prolog(g) for g in arg)
            return f"{op}([{sub}])"
        if op in cls.GOAL_OPS_SINGLE:
            return f"{op}({cls._goal_to_prolog(arg)})"
        if op in cls.GOAL_OPS_TAGLIST:
            if not isinstance(arg, list):
                raise GoalShapeError(f"{op} requires a list of tag strings")
            tags = ",".join(cls._quote_atom(t) for t in arg)
            return f"{op}([{tags}])"
        if op in cls.GOAL_OPS_ATOM:
            return f"{op}({cls._quote_atom(arg)})"
        raise GoalShapeError(f"Unknown goal operator: {op!r}")

    @staticmethod
    def _quote_atom(s) -> str:
        """Quote a Python string as a Prolog atom (single-quoted)."""
        safe = str(s).replace("\\", "\\\\").replace("'", "\\'")
        return f"'{safe}'"

    @classmethod
    def _time_to_prolog(cls, time_ctx: dict) -> str:
        """Serialize a time_context dict to a `t(Weekday, Hour, Minute)` term.

        Required keys: `weekday` (mon/tue/.../sun or the full English
        name), `hour` (0–23), `minute` (0–59). We canonicalize the
        weekday to its three-letter atom so Prolog's per-weekday
        time_matches clauses unify cleanly. Raises TimeShapeError for
        any malformed input — the orchestrator catches this and surfaces
        the error to the user rather than sending garbage to Prolog.
        """
        if not isinstance(time_ctx, dict):
            raise TimeShapeError(
                f"time_context must be a dict, got: {time_ctx!r}"
            )
        for key in ("weekday", "hour", "minute"):
            if key not in time_ctx:
                raise TimeShapeError(
                    f"time_context missing required key: {key!r}"
                )
        raw_weekday = time_ctx["weekday"]
        if not isinstance(raw_weekday, str):
            raise TimeShapeError(
                f"weekday must be a string, got: {raw_weekday!r}"
            )
        weekday = _WEEKDAY_CANON.get(raw_weekday.strip().lower())
        if weekday is None:
            raise TimeShapeError(
                f"Unknown weekday: {raw_weekday!r}"
            )
        hour = time_ctx["hour"]
        minute = time_ctx["minute"]
        if not isinstance(hour, int) or isinstance(hour, bool):
            raise TimeShapeError(f"hour must be an int, got: {hour!r}")
        if not isinstance(minute, int) or isinstance(minute, bool):
            raise TimeShapeError(f"minute must be an int, got: {minute!r}")
        if not (0 <= hour <= 23):
            raise TimeShapeError(f"hour out of range [0,23]: {hour}")
        if not (0 <= minute <= 59):
            raise TimeShapeError(f"minute out of range [0,59]: {minute}")
        return f"t({weekday},{hour},{minute})"

    @classmethod
    def _budget_to_prolog(cls, budget_ctx: dict | None) -> int | None:
        """Pull `max_thb` out of a budget_context dict as a plain int.

        Returns None when the context is absent. Raises BudgetShapeError
        on anything the Prolog side cannot consume as an integer THB
        ceiling. Kept as a classmethod to mirror `_time_to_prolog`.
        """
        if budget_ctx is None:
            return None
        if not isinstance(budget_ctx, dict):
            raise BudgetShapeError(
                f"budget_context must be a dict, got: {budget_ctx!r}"
            )
        if "max_thb" not in budget_ctx:
            raise BudgetShapeError("budget_context missing required key: 'max_thb'")
        raw = budget_ctx["max_thb"]
        if isinstance(raw, bool) or not isinstance(raw, (int, float)):
            raise BudgetShapeError(f"max_thb must be a number, got: {raw!r}")
        ceiling = int(raw)
        if ceiling <= 0:
            raise BudgetShapeError(f"max_thb must be positive, got: {ceiling}")
        return ceiling

    # ------------------------------------------------------------------
    # Repair serialization (Python ↔ Prolog terms for the repair loop).
    # ------------------------------------------------------------------

    def _repairs_to_prolog_list(self, repairs: list[dict]) -> str:
        return "[" + ",".join(self._repair_to_prolog(r) for r in repairs) + "]"

    def _repair_to_prolog(self, r: dict) -> str:
        kind = r.get("kind")
        if kind == "avoid_specific_boundary":
            return f"avoid_specific_boundary({self._quote_atom(r['a'])},{self._quote_atom(r['b'])})"
        if kind == "avoid_agency_pair":
            return f"avoid_agency_pair({r['a']},{r['b']})"
        if kind == "force_single_agency":
            return f"force_single_agency({r['agency']})"
        if kind == "infeasible":
            reason = r.get("reason", "unknown")
            return f"infeasible({reason})"
        return "none"

    @staticmethod
    def _trail_entry_repair(entry: dict) -> dict:
        """Trail entries are {diagnosis, repair_applied}; pull the repair."""
        return entry.get("repair_applied", entry)

    # ------------------------------------------------------------------
    # Result parsing helpers.
    # ------------------------------------------------------------------

    def _step_term_to_dict(self, step) -> dict:
        s = str(step)
        if s.startswith("ride("):
            return self._parse_ride_step(s)
        if s.startswith("transfer("):
            inner = s[len("transfer(") : -1]
            parts = self._split_top_level(inner)
            return {
                "type": "transfer",
                "from": parts[0].strip(),
                "to": parts[1].strip(),
            }
        return {"type": "unknown", "raw": s}

    def _parse_ride_step(self, s: str) -> dict:
        inner = s[len("ride(") : -1]
        parts = self._split_top_level(inner)
        line = parts[0].strip()
        board = parts[1].strip()
        alight = parts[2].strip()
        stations_str = parts[3].strip()
        if stations_str.startswith("[") and stations_str.endswith("]"):
            inner_stations = stations_str[1:-1]
            stations = [
                st.strip().strip("'")
                for st in self._split_top_level(inner_stations)
            ]
        else:
            stations = [stations_str.strip("'")]
        return {
            "type": "ride",
            "line": line,
            "board": board,
            "alight": alight,
            "stations": stations,
        }

    def _parse_candidate_pairs(self, raw_list) -> list[dict]:
        """Parse a Prolog list of `Name-Station-Score` (-/2) terms.

        pyswip serializes the nested -/2 chain in *prefix* operator form:
        `-(-(Name, Station), Score)`. We peel the outer compound for
        Score, then the inner for Name and Station. Names may contain
        spaces and parentheses (e.g. 'Mo Chit (N8)') so we use the
        bracket-aware splitter rather than a regex.
        """
        out, seen = [], set()
        for item in raw_list:
            parsed = self._parse_dash_pair(str(item))
            if parsed is None:
                continue
            name, station, score = parsed
            if name in seen:
                continue
            seen.add(name)
            out.append({"name": name, "station": station, "pref_score": score})
        return out

    def _parse_dash_pair(self, s: str) -> tuple[str, str, int] | None:
        """Parse `-(-(Name, Station), Score)` into (name, station, score)."""
        if not s.startswith("-(") or not s.endswith(")"):
            return None
        outer = s[2:-1]
        outer_parts = self._split_top_level(outer)
        if len(outer_parts) != 2:
            return None
        try:
            score = int(outer_parts[1].strip())
        except ValueError:
            return None
        inner = outer_parts[0].strip()
        if not inner.startswith("-(") or not inner.endswith(")"):
            return None
        inner_parts = self._split_top_level(inner[2:-1])
        if len(inner_parts) != 2:
            return None
        name = inner_parts[0].strip().strip("'")
        station = inner_parts[1].strip().strip("'")
        return (name, station, score)

    def _parse_violation(self, s: str) -> dict | None:
        """Parse `violation(Step, Reason)` into a dict.

        Step is a transfer(A, B) term (the only kind audit_route emits
        currently); Reason is an atom like `weather_exposed`.
        """
        if not s.startswith("violation("):
            return None
        inner = s[len("violation(") : -1]
        parts = self._split_top_level(inner)
        if len(parts) != 2:
            return None
        step_str = parts[0].strip()
        reason = parts[1].strip().strip("'")
        if step_str.startswith("transfer("):
            step = self._step_term_to_dict(step_str)
        else:
            step = {"type": "unknown", "raw": step_str}
        return {"step": step, "reason": reason}

    # ------------------------------------------------------------------
    # Fiscal-term parsing (segment / boundary / diagnosis / repair / cert).
    # ------------------------------------------------------------------

    def _parse_segment(self, s: str) -> tuple[str, str, str] | None:
        """Parse `segment(Agency, TapIn, TapOut)` → (agency, tap_in, tap_out)."""
        if not s.startswith("segment(") or not s.endswith(")"):
            return None
        parts = self._split_top_level(s[len("segment(") : -1])
        if len(parts) != 3:
            return None
        return (
            parts[0].strip().strip("'"),
            parts[1].strip().strip("'"),
            parts[2].strip().strip("'"),
        )

    def _parse_boundary(self, s: str) -> dict | None:
        """Parse `boundary(StA, StB, AgencyA, AgencyB)` → dict."""
        if not s.startswith("boundary(") or not s.endswith(")"):
            return None
        parts = self._split_top_level(s[len("boundary(") : -1])
        if len(parts) != 4:
            return None
        return {
            "a": parts[0].strip().strip("'"),
            "b": parts[1].strip().strip("'"),
            "agency_a": parts[2].strip().strip("'"),
            "agency_b": parts[3].strip().strip("'"),
        }

    def _parse_diagnosis(self, s: str) -> dict:
        """Parse Prolog Diagnosis term into a JSON-serializable dict.

        within_budget(Total)                       → {kind, total}
        over_budget(Total, Overage, Segs, Bounds)  → full structural dict
        """
        if s.startswith("within_budget("):
            inner = s[len("within_budget(") : -1]
            try:
                total = int(inner.strip())
            except ValueError:
                total = 0
            return {"kind": "within_budget", "total": total}
        if s.startswith("over_budget("):
            parts = self._split_top_level(s[len("over_budget(") : -1])
            if len(parts) != 4:
                return {"kind": "over_budget", "raw": s}
            total = int(parts[0].strip())
            overage = int(parts[1].strip())
            segs_str = parts[2].strip()
            bounds_str = parts[3].strip()
            segments = []
            if segs_str.startswith("[") and segs_str.endswith("]"):
                for item in self._split_top_level(segs_str[1:-1]):
                    parsed = self._parse_segment(item.strip())
                    if parsed is None:
                        continue
                    agency, tap_in, tap_out = parsed
                    segments.append({
                        "agency": agency,
                        "tap_in": tap_in,
                        "tap_out": tap_out,
                    })
            boundaries = []
            if bounds_str.startswith("[") and bounds_str.endswith("]"):
                for item in self._split_top_level(bounds_str[1:-1]):
                    parsed = self._parse_boundary(item.strip())
                    if parsed is not None:
                        boundaries.append(parsed)
            return {
                "kind": "over_budget",
                "total": total,
                "overage": overage,
                "segments": segments,
                "boundaries": boundaries,
            }
        return {"kind": "unknown", "raw": s}

    def _parse_repair(self, s: str) -> dict:
        if s.startswith("avoid_specific_boundary("):
            parts = self._split_top_level(s[len("avoid_specific_boundary(") : -1])
            if len(parts) == 2:
                return {
                    "kind": "avoid_specific_boundary",
                    "a": parts[0].strip().strip("'"),
                    "b": parts[1].strip().strip("'"),
                }
        if s.startswith("avoid_agency_pair("):
            parts = self._split_top_level(s[len("avoid_agency_pair(") : -1])
            if len(parts) == 2:
                return {
                    "kind": "avoid_agency_pair",
                    "a": parts[0].strip().strip("'"),
                    "b": parts[1].strip().strip("'"),
                }
        if s.startswith("force_single_agency("):
            inner = s[len("force_single_agency(") : -1]
            return {"kind": "force_single_agency", "agency": inner.strip().strip("'")}
        if s.startswith("infeasible("):
            inner = s[len("infeasible(") : -1].strip()
            if inner.startswith("structurally_over_budget("):
                val = inner[len("structurally_over_budget(") : -1].strip()
                try:
                    return {
                        "kind": "infeasible",
                        "reason": "structurally_over_budget",
                        "total": int(val),
                    }
                except ValueError:
                    pass
            return {"kind": "infeasible", "reason": inner.strip("'")}
        return {"kind": "unknown", "raw": s}

    def _parse_certificate(self, s: str) -> dict:
        """Parse `certificate(repairs_exhausted([...]), ...)` into a dict.

        The trail inside repairs_exhausted is kept as raw strings so the
        LLM narrator can reproduce the reasoning chain verbatim without
        the bridge layer re-interpreting it.
        """
        if not s.startswith("certificate(") or not s.endswith(")"):
            return {"kind": "certificate", "raw": s}
        parts = self._split_top_level(s[len("certificate(") : -1])
        trail_repairs: list[str] = []
        tail: dict = {}
        for p in parts:
            p = p.strip()
            if p.startswith("repairs_exhausted("):
                inner = p[len("repairs_exhausted(") : -1].strip()
                if inner.startswith("[") and inner.endswith("]"):
                    for r in self._split_top_level(inner[1:-1]):
                        trail_repairs.append(r.strip())
            elif p.startswith("final_over_by("):
                try:
                    tail["final_over_by"] = int(p[len("final_over_by(") : -1])
                except ValueError:
                    pass
            elif p.startswith("min_seen("):
                try:
                    tail["min_seen"] = int(p[len("min_seen(") : -1])
                except ValueError:
                    pass
            elif p == "graph_disconnected":
                tail["graph_disconnected"] = True
        return {
            "kind": "certificate",
            "repairs_exhausted": trail_repairs,
            **tail,
        }

    @staticmethod
    def _reraise_fare_unknown(exc: Exception) -> None:
        """If `exc` wraps a Prolog `fare_unknown/3` throw, re-raise as FareUnknownError.

        pyswip surfaces thrown Prolog terms as the exception's string form.
        We match the known payload shape loosely; anything else is left
        alone so the caller sees the original exception.
        """
        msg = str(exc)
        m = re.search(r"fare_unknown\(\s*([^,]+?)\s*,\s*'?([^,']+)'?\s*,\s*'?([^)']+)'?\s*\)", msg)
        if m:
            agency, origin, destination = m.group(1), m.group(2), m.group(3)
            raise FareUnknownError(agency.strip(), origin.strip(), destination.strip()) from exc

    @staticmethod
    def _split_top_level(s: str) -> list[str]:
        """Split on commas at bracket-depth zero."""
        parts, depth, current = [], 0, []
        for ch in s:
            if ch in "([":
                depth += 1
                current.append(ch)
            elif ch in ")]":
                depth -= 1
                current.append(ch)
            elif ch == "," and depth == 0:
                parts.append("".join(current))
                current = []
            else:
                current.append(ch)
        if current:
            parts.append("".join(current))
        return parts

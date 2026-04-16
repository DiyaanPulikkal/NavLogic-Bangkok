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

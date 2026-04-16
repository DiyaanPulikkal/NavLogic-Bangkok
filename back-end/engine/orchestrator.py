"""
orchestrator.py — the neuro-symbolic loop.

handle() routes one user input through the engine:

  user_input
    │
    ▼
  LLM.translate_to_query(user_input, history, vocab, synonyms)
    │  → ("plan", {origin, goal})
    ▼
  _handle_plan(args, history):
      0. resolve origin (Prolog match_station + Python rank + edit-dist)
      1. pure-route shortcut: goal is just route_to → Dijkstra + route_steps
      2. unknown_tags pre-flight → if anything, surface back to the user
      3. candidates(goal)
      4. empty? relax(goal) → minimal-drop survivors with relaxation_note
      5. Dijkstra cost from origin to each candidate's station
      6. rank: pref_score↓ then cost↑
      7. audit_route_for_path(path, goal) per candidate
         violation? blacklist this POI, try next-best (max MAX_REPLAN sweeps)
      8. format result + audit_trail through LLM for natural-language reply

The audit loop is the showpiece: Prolog supervises Python's numeric search
and tells it when to back off. Prolog never does Dijkstra; Python never
does logical-form evaluation. The shape of the result includes both
relaxation_note and audit_trail so the LLM can narrate "what I tried,
what I dropped, what I rejected" — failure modes are first-class.
"""

from __future__ import annotations

import heapq
import logging
from datetime import datetime
from difflib import SequenceMatcher
from zoneinfo import ZoneInfo

from engine.llm.llm import LLMInterface
from engine.prolog import GoalShapeError, PrologInterface, TimeShapeError

logger = logging.getLogger("orchestrator")

_WEEKDAY_BY_PY_INT = {
    0: "mon", 1: "tue", 2: "wed", 3: "thu",
    4: "fri", 5: "sat", 6: "sun",
}

_WEEKDAY_DISPLAY = {
    "mon": "Monday", "tue": "Tuesday", "wed": "Wednesday", "thu": "Thursday",
    "fri": "Friday", "sat": "Saturday", "sun": "Sunday",
}


class Orchestrator:
    MAX_REPLAN = 3
    _MATCH_TYPE_RANK = {"exact": 0, "prefix": 1, "substring": 2}
    _BANGKOK_TZ = ZoneInfo("Asia/Bangkok")

    def __init__(self):
        self.llm = LLMInterface()
        self.prolog = PrologInterface()
        self._vocab_cache: list[str] | None = None
        self._synonyms_cache: dict[str, str] | None = None

    # ------------------------------------------------------------------
    # Temporal context — the per-query time frame.
    # ------------------------------------------------------------------

    def _now_bangkok(self) -> dict:
        """Wall-clock `time_context` for Asia/Bangkok.

        Returned as the {weekday, hour, minute} triple the Prolog layer
        consumes. Kept as an instance method so tests can monkeypatch
        this single attachment point rather than patching zoneinfo.
        """
        now = datetime.now(self._BANGKOK_TZ)
        return {
            "weekday": _WEEKDAY_BY_PY_INT[now.weekday()],
            "hour": now.hour,
            "minute": now.minute,
        }

    def _resolve_time_context(self, args: dict) -> dict:
        """Canonicalize the LLM-supplied or wall-clock time_context.

        Raises TimeShapeError if the LLM emitted a malformed shape —
        caught in _handle_plan and surfaced as an error response.
        The returned dict carries a `display` field for the frontend
        badge ("Saturday 20:00"); the {weekday, hour, minute} subset is
        what PrologInterface.{candidates,relax} actually serialize.
        """
        tc_raw = args.get("time_context") if isinstance(args, dict) else None
        tc = tc_raw if isinstance(tc_raw, dict) else self._now_bangkok()
        PrologInterface._time_to_prolog(tc)
        wd = str(tc["weekday"]).strip().lower()
        from engine.prolog import _WEEKDAY_CANON
        canonical = _WEEKDAY_CANON[wd]
        hour = int(tc["hour"])
        minute = int(tc["minute"])
        display = f"{_WEEKDAY_DISPLAY[canonical]} {hour:02d}:{minute:02d}"
        return {
            "weekday": canonical,
            "hour": hour,
            "minute": minute,
            "display": display,
        }

    # ------------------------------------------------------------------
    # Top-level dispatch.
    # ------------------------------------------------------------------

    def handle(self, user_input: str, history: list | None = None) -> tuple[dict, list]:
        if history is None:
            history = []

        time_hint = self._now_bangkok()
        result, history = self.llm.translate_to_query(
            user_input, history, self._vocab(), self._synonyms(),
            time_hint=time_hint,
        )
        if result is None:
            return self._error("Sorry, I couldn't process your request."), history
        if isinstance(result, str):
            return self._answer(result), history

        function_name, args = result
        logger.info("Dispatching: %s", function_name)

        if function_name != "plan":
            return self._error(f"Unknown function: {function_name}"), history
        return self._handle_plan(args, history)

    def handle_text(self, user_input: str) -> str:
        """CLI helper: returns just the natural-language answer."""
        result, _ = self.handle(user_input)
        if result["type"] == "error":
            return result["data"]["message"]
        return result["data"].get("answer") or str(result["data"])

    def handle_pure_route(self, origin_raw: str, dest_raw: str) -> dict:
        """Public no-LLM entry for /api/route. Resolves names and runs the
        pure-route pipeline (Dijkstra + symbolic step segmentation). Does
        not touch the LLM — safe to call without GOOGLE_API_KEY."""
        if not origin_raw or not dest_raw:
            return self._error("Both start and end are required.")
        origin = self._resolve_location(origin_raw)
        if origin is None:
            return self._error(f"I don't recognize '{origin_raw}' as a station or POI.")
        dest = self._resolve_location(dest_raw)
        if dest is None:
            return self._error(f"I don't recognize '{dest_raw}' as a station or POI.")

        edges = self.prolog.get_all_edges()
        graph = self._build_graph(edges)
        path, cost = self._dijkstra(graph, origin, dest)
        if path is None:
            return self._error(f"No route found from '{origin}' to '{dest}'.")

        return {
            "type": "plan",
            "data": {
                "origin": origin,
                "destination": dest,
                "total_time": cost,
                "steps": self.prolog.build_route_steps(path),
            },
        }

    # ------------------------------------------------------------------
    # The plan handler — the audit/relax loop.
    # ------------------------------------------------------------------

    def _handle_plan(self, args: dict, history: list) -> tuple[dict, list]:
        origin_raw = args.get("origin")
        goal = args.get("goal")
        if not origin_raw or not goal:
            return self._error("I need both an origin and a goal to plan a trip."), history

        origin = self._resolve_location(origin_raw)
        if origin is None:
            return self._error(f"I don't recognize '{origin_raw}' as a station or POI."), history

        try:
            time_ctx = self._resolve_time_context(args)
        except TimeShapeError as e:
            return self._error(f"Malformed time_context: {e}"), history

        if self._is_pure_route(goal):
            dest_raw = self._extract_route_to(goal)
            return self._handle_pure_route(origin, dest_raw, history)

        try:
            unknowns = self.prolog.unknown_tags(goal)
        except GoalShapeError as e:
            return self._error(f"Malformed goal: {e}"), history

        if unknowns:
            return self._handle_unknown_tags(origin, unknowns, history, time_ctx)

        cands = self.prolog.candidates(goal, time_ctx)
        relaxation_note: list[str] | None = None
        if not cands:
            relaxed = self.prolog.relax(goal, time_ctx)
            if relaxed is None:
                return self._answer(
                    "I couldn't find anything matching, even after relaxing your constraints."
                ), history
            dropped, cands = relaxed
            relaxation_note = dropped
            logger.info("Relaxed by dropping: %s", dropped)

        edges = self.prolog.get_all_edges()
        graph = self._build_graph(edges)
        ranked: list[dict] = []
        for c in cands:
            path, cost = self._dijkstra(graph, origin, c["station"])
            if path is None:
                continue
            ranked.append({**c, "path": path, "cost": cost})
        if not ranked:
            return self._answer(
                "I found matching places but none are reachable from your origin in the network."
            ), history

        ranked.sort(key=lambda r: (-r["pref_score"], r["cost"]))

        chosen, audit_trail = self._select_via_audit(ranked, goal)

        if chosen is None:
            data = {
                "origin": origin,
                "time_context": time_ctx,
                "relaxation_note": relaxation_note,
                "audit_trail": audit_trail,
                "alternatives": [r["name"] for r in ranked[:5]],
                "note": "Every candidate route violated one of your hard constraints.",
            }
            return self._format({"type": "plan", "data": data}, history)

        data = {
            "origin": origin,
            "destination": chosen["station"],
            "poi": chosen["name"],
            "total_time": chosen["cost"],
            "steps": chosen["steps"],
            "preference_score": chosen["pref_score"],
            "time_context": time_ctx,
            "relaxation_note": relaxation_note,
            "audit_trail": audit_trail,
            "alternatives": [
                r["name"] for r in ranked[:5] if r["name"] != chosen["name"]
            ],
        }
        return self._format({"type": "plan", "data": data}, history)

    def _select_via_audit(
        self, ranked: list[dict], goal: dict
    ) -> tuple[dict | None, list[dict]]:
        """Walk the ranked candidates, auditing each route. Blacklist on
        violation and try the next. Bounded at MAX_REPLAN sweeps."""
        audit_trail: list[dict] = []
        blacklist: set[str] = set()
        for _sweep in range(self.MAX_REPLAN):
            for r in ranked:
                if r["name"] in blacklist:
                    continue
                violations = self.prolog.audit_route_for_path(r["path"], goal)
                if not violations:
                    return (
                        {**r, "steps": self.prolog.build_route_steps(r["path"])},
                        audit_trail,
                    )
                audit_trail.append({"candidate": r["name"], "violations": violations})
                blacklist.add(r["name"])
                logger.info("Audit failed for %s: %s", r["name"], violations)
            if len(blacklist) >= len(ranked):
                break
        return None, audit_trail

    # ------------------------------------------------------------------
    # Pure-route shortcut.
    # ------------------------------------------------------------------

    def _handle_pure_route(
        self, origin: str, dest_raw: str, history: list
    ) -> tuple[dict, list]:
        dest = self._resolve_location(dest_raw)
        if dest is None:
            return self._error(f"I don't recognize '{dest_raw}' as a destination."), history

        edges = self.prolog.get_all_edges()
        graph = self._build_graph(edges)
        path, cost = self._dijkstra(graph, origin, dest)
        if path is None:
            return self._error(f"No route found from '{origin}' to '{dest}'."), history

        steps = self.prolog.build_route_steps(path)
        data = {
            "origin": origin,
            "destination": dest,
            "total_time": cost,
            "steps": steps,
        }
        return self._format({"type": "plan", "data": data}, history)

    # ------------------------------------------------------------------
    # Goal-shape predicates.
    # ------------------------------------------------------------------

    @staticmethod
    def _is_pure_route(goal: dict) -> bool:
        """True when goal is `route_to` alone (or wrapped in a singleton and/or)."""
        if not isinstance(goal, dict) or len(goal) != 1:
            return False
        op, arg = next(iter(goal.items()))
        if op == "route_to":
            return True
        if op in ("and", "or") and isinstance(arg, list) and len(arg) == 1:
            return Orchestrator._is_pure_route(arg[0])
        return False

    @staticmethod
    def _extract_route_to(goal: dict) -> str | None:
        if not isinstance(goal, dict) or len(goal) != 1:
            return None
        op, arg = next(iter(goal.items()))
        if op == "route_to":
            return arg
        if op in ("and", "or") and isinstance(arg, list):
            for sub in arg:
                found = Orchestrator._extract_route_to(sub)
                if found is not None:
                    return found
        return None

    # ------------------------------------------------------------------
    # Unknown-tag handling — surface back to the user.
    # ------------------------------------------------------------------

    def _handle_unknown_tags(
        self, origin: str, unknowns: list[str], history: list,
        time_ctx: dict | None = None,
    ) -> tuple[dict, list]:
        sample = ", ".join(self._vocab()[:8])
        note = (
            f"I don't recognize {', '.join(repr(u) for u in unknowns)}. "
            f"Try terms like: {sample}..."
        )
        data = {
            "origin": origin,
            "unknown_tags": unknowns,
            "note": note,
        }
        if time_ctx is not None:
            data["time_context"] = time_ctx
        result = {"type": "plan", "data": data}
        return self._format(result, history)

    # ------------------------------------------------------------------
    # Vocabulary cache (one query per process; KB facts don't change).
    # ------------------------------------------------------------------

    def _vocab(self) -> list[str]:
        if self._vocab_cache is None:
            self._vocab_cache = self.prolog.active_tag_vocabulary()
        return self._vocab_cache

    def _synonyms(self) -> dict[str, str]:
        if self._synonyms_cache is None:
            self._synonyms_cache = self.prolog.active_synonyms()
        return self._synonyms_cache

    # ------------------------------------------------------------------
    # Result formatting + simple shapes.
    # ------------------------------------------------------------------

    def _format(self, result: dict, history: list) -> tuple[dict, list]:
        return self.llm.format_result(result, history, self._vocab(), self._synonyms())

    @staticmethod
    def _answer(text: str) -> dict:
        return {"type": "answer", "data": {"answer": text}}

    @staticmethod
    def _error(message: str) -> dict:
        return {"type": "error", "data": {"message": message}}

    # ------------------------------------------------------------------
    # Name resolution: Prolog classifies, Python ranks + edit-distance fallback.
    # ------------------------------------------------------------------

    def _resolve_location(self, raw_name: str) -> str | None:
        if not raw_name:
            return None

        if self.prolog.is_valid_station(raw_name):
            return raw_name

        candidates = self.prolog.match_station_classified(raw_name)
        if candidates:
            best = self._rank_candidates(raw_name, candidates)
            if best:
                logger.info("Resolved '%s' → '%s'", raw_name, best)
                return best

        poi_station = self._poi_display_to_station(raw_name)
        if poi_station:
            logger.info("Resolved POI '%s' → '%s'", raw_name, poi_station)
            return poi_station

        return self._best_edit_distance_match(raw_name)

    def _poi_display_to_station(self, raw_name: str) -> str | None:
        """Look up a POI by display name (case-insensitive, prefix/substring).

        This lets users say "Grand Palace" and have the engine route to
        the POI's nearest station. We do this in Prolog (it owns the
        name normalization) but let Python decide between equally good
        candidates.
        """
        safe = raw_name.replace("\\", "\\\\").replace("'", "\\'")
        query = (
            f"poi(_, Display, Station), "
            f"downcase_atom(Display, DL), "
            f"downcase_atom('{safe}', RL), "
            f"(DL = RL ; sub_atom(DL, 0, _, _, RL) ; sub_atom(DL, _, _, _, RL))"
        )
        try:
            for r in self.prolog.prolog.query(query):
                return str(r["Station"])
        except Exception as e:
            logger.warning("POI lookup failed for '%s': %s", raw_name, e)
        return None

    def _rank_candidates(self, raw_name: str, candidates: list[dict]) -> str | None:
        if not candidates:
            return None
        raw_lower = raw_name.lower()

        def score(c):
            type_rank = self._MATCH_TYPE_RANK.get(c["match_type"], 9)
            sim = SequenceMatcher(None, raw_lower, c["station"].lower()).ratio()
            return (type_rank, -sim)

        best = sorted(candidates, key=score)[0]
        if best["match_type"] == "substring":
            sim = SequenceMatcher(None, raw_lower, best["station"].lower()).ratio()
            if sim < 0.4:
                return None
        return best["station"]

    def _best_edit_distance_match(
        self, raw_name: str, threshold: float = 0.75
    ) -> str | None:
        raw_lower = raw_name.lower()
        best_station, best_score = None, 0.0
        for station in self.prolog.get_all_station_names():
            base = station.split(" (")[0].lower()
            if abs(len(raw_lower) - len(base)) > 1:
                continue
            sim = SequenceMatcher(None, raw_lower, base).ratio()
            if sim > best_score:
                best_score = sim
                best_station = station
        if best_score >= threshold:
            logger.info(
                "Edit-distance matched '%s' → '%s' (%.2f)",
                raw_name, best_station, best_score,
            )
            return best_station
        return None

    # ------------------------------------------------------------------
    # Dijkstra (Python — Prolog has no business here).
    # ------------------------------------------------------------------

    @staticmethod
    def _build_graph(edges: list[tuple[str, str, int]]) -> dict[str, list[tuple[str, int]]]:
        graph: dict[str, list[tuple[str, int]]] = {}
        for a, b, t in edges:
            graph.setdefault(a, []).append((b, t))
        return graph

    @staticmethod
    def _dijkstra(graph, start, end):
        if start == end:
            return [start], 0
        heap = [(0, start, [start])]
        visited: set[str] = set()
        while heap:
            cost, node, path = heapq.heappop(heap)
            if node in visited:
                continue
            visited.add(node)
            if node == end:
                return path, cost
            for neighbor, weight in graph.get(node, []):
                if neighbor not in visited:
                    heapq.heappush(heap, (cost + weight, neighbor, path + [neighbor]))
        return None, None

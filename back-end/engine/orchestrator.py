import heapq
import logging
from difflib import SequenceMatcher

from engine.llm.llm import LLMInterface
from engine.prolog import PrologInterface

logger = logging.getLogger("orchestrator")


# Prolog query builders for each knowledge-base function
PROLOG_QUERY_MAP = {
    'line_of':               lambda args: f"line_of('{args['station_name']}', Line).",
    'same_line':             lambda args: f"same_line('{args['station_a']}', '{args['station_b']}').",
    'is_transfer_station':   lambda args: f"is_transfer_station('{args['station_name']}').",
    'needs_transfer':        lambda args: f"needs_transfer('{args['station_a']}', '{args['station_b']}').",
    'attraction_near_station': lambda args: f"attraction_near_station('{args['attraction_name']}', Station).",
}

# Keys in each function's arguments that hold station/location names needing resolution
STATION_ARG_KEYS = {
    'line_of':             ['station_name'],
    'same_line':           ['station_a', 'station_b'],
    'is_transfer_station': ['station_name'],
    'needs_transfer':      ['station_a', 'station_b'],
}


class Orchestrator:
    def __init__(self):
        self.llm = LLMInterface()
        self.prolog = PrologInterface()

    def handle(self, user_input: str, history: list | None = None) -> tuple[dict, list]:
        if history is None:
            history = []

        result, history = self.llm.translate_to_query(user_input, history)
        if result is None:
            return {"type": "error", "data": {"message": "Sorry, I couldn't process your request."}}, history

        # If the LLM returned plain text instead of a function call
        if isinstance(result, str):
            return {"type": "answer", "data": {"answer": result}}, history

        function_name, arguments = result
        logger.info("Dispatching: %s", function_name)

        # Route finding
        if function_name == 'find_route':
            return self._handle_find_route(arguments), history

        # Schedule-based trip planning
        if function_name == 'plan_trip':
            return self._handle_plan_trip(arguments, history)

        # Day planning with multiple stops + attractions
        if function_name == 'plan_day':
            return self._handle_plan_day(arguments, history)

        # Explore trip planning (auto-discover attractions & nightlife)
        if function_name == 'plan_explore':
            return self._handle_plan_explore(arguments, history)

        # Knowledge-base queries
        if function_name in STATION_ARG_KEYS:
            for key in STATION_ARG_KEYS[function_name]:
                raw = arguments[key]
                resolved = self._resolve_location(raw)
                if resolved is None:
                    return {"type": "error", "data": {"message": f"Unknown location: '{raw}'."}}, history
                arguments[key] = resolved

        query_builder = PROLOG_QUERY_MAP.get(function_name)
        if query_builder is None:
            return {"type": "error", "data": {"message": f"Unknown function: {function_name}"}}, history

        prolog_query = query_builder(arguments)
        logger.info("Prolog query: %s", prolog_query)
        prolog_result = self.prolog.query(prolog_query)
        logger.info("Prolog result: %s", prolog_result)
        formatted, history = self.llm.format_prolog_result(
            function_name,
            result={"type": "answer", "data": {"answer": self._format_prolog_result(prolog_result)}},
            history=history,
        )
        return formatted, history

    def handle_text(self, user_input: str) -> str:
        """Legacy text-based interface for CLI usage."""
        result, _ = self.handle(user_input)
        if result["type"] == "error":
            return result["data"]["message"]
        if result["type"] == "route":
            return self._format_route_text(result["data"])
        return result["data"].get("answer", str(result["data"]))

    # ------------------------------------------------------------------
    # Schedule / Trip Planning
    # ------------------------------------------------------------------

    def _handle_plan_trip(self, arguments: dict, history: list) -> tuple[dict, list]:
        origin_raw = arguments['origin']
        destination_raw = arguments['destination']
        deadline_str = arguments.get('deadline', '09:00')

        # Resolve station names
        origin = self._resolve_location(origin_raw)
        if origin is None:
            return {"type": "error", "data": {"message": f"Unknown location: '{origin_raw}'."}}, history
        destination = self._resolve_location(destination_raw)
        if destination is None:
            return {"type": "error", "data": {"message": f"Unknown location: '{destination_raw}'."}}, history

        # Parse deadline from HH:MM to HHMM integer
        deadline = self._parse_time(deadline_str)
        if deadline is None:
            return {"type": "error", "data": {"message": f"Invalid time format: '{deadline_str}'. Use HH:MM."}}, history

        logger.info("Planning trip: %s → %s by %d", origin, destination, deadline)
        itineraries = self.prolog.plan_trip(origin, destination, deadline)

        if not itineraries:
            result = {
                "type": "answer",
                "data": {"answer": f"No scheduled trips found from {origin} to {destination} arriving by {deadline_str}."}
            }
            return result, history

        result = {
            "type": "schedule",
            "data": {
                "origin": origin,
                "destination": destination,
                "deadline": deadline_str,
                "itineraries": itineraries,
            }
        }

        formatted, history = self.llm.format_prolog_result(
            "plan_trip",
            result=result,
            history=history,
        )
        return formatted, history

    def _handle_plan_day(self, arguments: dict, history: list) -> tuple[dict, list]:
        origin_raw = arguments.get('origin', '')
        stops = arguments.get('stops', [])

        if not stops:
            return {"type": "error", "data": {"message": "Please provide at least one stop."}}, history

        # Resolve origin
        origin = self._resolve_location(origin_raw)
        if origin is None:
            return {"type": "error", "data": {"message": f"Unknown location: '{origin_raw}'."}}, history

        # Resolve all stop locations
        resolved_stops = []
        for stop in stops:
            loc_raw = stop['location']
            resolved = self._resolve_location(loc_raw)
            if resolved is None:
                return {"type": "error", "data": {"message": f"Unknown location: '{loc_raw}'."}}, history
            deadline = self._parse_time(stop['arrive_by'])
            if deadline is None:
                return {"type": "error", "data": {"message": f"Invalid time: '{stop['arrive_by']}'."}}, history
            resolved_stops.append({
                "location": resolved,
                "arrive_by": stop['arrive_by'],
                "deadline_int": deadline,
            })

        # Build day plan: for each leg, plan trip + find attractions at destination
        legs = []
        current_origin = origin
        for stop in resolved_stops:
            dest = stop['location']
            deadline_int = stop['deadline_int']

            # Plan the transit leg
            itineraries = self.prolog.plan_trip(current_origin, dest, deadline_int)

            # Find attractions near the destination station
            attractions = self.prolog.attractions_near(dest)

            legs.append({
                "from": current_origin,
                "to": dest,
                "arrive_by": stop['arrive_by'],
                "itineraries": itineraries,
                "attractions": attractions,
            })

            current_origin = dest

        result = {
            "type": "day_plan",
            "data": {
                "origin": origin,
                "stops": [s['location'] for s in resolved_stops],
                "legs": legs,
            }
        }

        formatted, history = self.llm.format_prolog_result(
            "plan_day",
            result=result,
            history=history,
        )
        return formatted, history

    def _handle_plan_explore(self, arguments: dict, history: list) -> tuple[dict, list]:
        """Unified explore planner:
        - Python Dijkstra for fast cross-line routing
        - Prolog KB for attraction and nightlife venue inference
        Auto-discovers the best areas with points of interest reachable by transit,
        combining both attractions and nightlife venues into a single trip plan.
        """
        origin_raw = arguments['origin']
        start_time_str = arguments.get('start_time', '09:00')
        end_time_str = arguments.get('end_time', '17:00')

        # Resolve origin
        origin = self._resolve_location(origin_raw)
        if origin is None:
            return {"type": "error", "data": {"message": f"Unknown location: '{origin_raw}'."}}, history

        start_time = self._parse_time(start_time_str)
        if start_time is None:
            return {"type": "error", "data": {"message": f"Invalid time format: '{start_time_str}'."}}, history
        end_time = self._parse_time(end_time_str)
        if end_time is None:
            return {"type": "error", "data": {"message": f"Invalid time format: '{end_time_str}'."}}, history

        # --- Prolog KB: get all attractions (including nightlife) grouped by station ---
        attractions_by_station = self.prolog.get_attractions_by_station()

        if not attractions_by_station:
            return {"type": "answer", "data": {"answer": "No points of interest found in the knowledge base."}}, history

        # --- Python Dijkstra: find reachable areas ---
        edges = self.prolog.get_all_edges()
        graph = self._build_graph(edges)

        reachable = []
        for station, attractions in attractions_by_station.items():
            path, cost = self._dijkstra(graph, origin, station)
            if path is not None:
                reachable.append({
                    "station": station,
                    "cost": cost,
                    "attractions": attractions,
                    "path": path,
                })

        if not reachable:
            return {"type": "answer", "data": {"answer": "No areas with points of interest reachable from your location via transit."}}, history

        # Sort by travel time and select up to 4 diverse stops
        reachable.sort(key=lambda x: x['cost'])
        selected = self._select_explore_stops(reachable, max_stops=4)

        # Calculate suggested arrival times spread across the time window
        start_min = (start_time // 100) * 60 + (start_time % 100)
        end_min = (end_time // 100) * 60 + (end_time % 100)
        # Handle past-midnight end times (e.g. 02:00 when start is 19:00)
        if end_min <= start_min:
            end_min += 24 * 60
        total_min = end_min - start_min
        slot_min = max(60, total_min // (len(selected) + 1))

        # --- Build legs using Dijkstra route ---
        legs = []
        current_origin = origin
        for i, stop in enumerate(selected):
            arrive_min = start_min + (i + 1) * slot_min
            arrive_h, arrive_m = divmod(arrive_min % (24 * 60), 60)
            arrive_str = f"{arrive_h:02d}:{arrive_m:02d}"

            route_data = self._find_and_format_route(current_origin, stop['station'])

            legs.append({
                "from": current_origin,
                "to": stop['station'],
                "arrive_by": arrive_str,
                "route": route_data.get("data") if route_data["type"] == "route" else None,
                "attractions": stop['attractions'],
            })

            current_origin = stop['station']

        # Determine if end time is past midnight or very late
        past_midnight = end_time < start_time
        last_train_note = (
            "Bangkok's rail transit operates until approximately midnight. "
            "For your return trip after midnight, use Grab or a taxi."
        ) if past_midnight or end_time > 2330 else None

        result = {
            "type": "explore",
            "data": {
                "origin": origin,
                "stops": [s['station'] for s in selected],
                "legs": legs,
                "start_time": start_time_str,
                "end_time": end_time_str,
                "last_train_note": last_train_note,
            }
        }

        formatted, history = self.llm.format_prolog_result("plan_explore", result, history)
        return formatted, history

    @staticmethod
    def _select_explore_stops(reachable: list[dict], max_stops: int = 4) -> list[dict]:
        """Pick up to max_stops areas, skipping stations too close together."""
        if len(reachable) <= max_stops:
            return reachable
        selected = [reachable[0]]
        for candidate in reachable[1:]:
            if len(selected) >= max_stops:
                break
            too_close = any(abs(candidate['cost'] - s['cost']) < 5 for s in selected)
            if not too_close:
                selected.append(candidate)
        if len(selected) < max_stops:
            for candidate in reachable:
                if len(selected) >= max_stops:
                    break
                if candidate not in selected:
                    selected.append(candidate)
        return selected

    @staticmethod
    def _parse_time(time_str: str) -> int | None:
        """Parse 'HH:MM' or 'HHMM' into integer HHMM."""
        time_str = time_str.strip()
        if ':' in time_str:
            parts = time_str.split(':')
            if len(parts) == 2:
                try:
                    h, m = int(parts[0]), int(parts[1])
                    if 0 <= h <= 23 and 0 <= m <= 59:
                        return h * 100 + m
                except ValueError:
                    return None
        else:
            try:
                val = int(time_str)
                if 0 <= val <= 2359:
                    return val
            except ValueError:
                return None
        return None

    # ------------------------------------------------------------------
    # Schedule direct query (bypass LLM, used by API)
    # ------------------------------------------------------------------

    def plan_trip(self, origin: str, destination: str, deadline: str) -> dict:
        """Direct schedule query without LLM — used by the /api/schedule endpoint."""
        origin_resolved = self._resolve_location(origin)
        if origin_resolved is None:
            return {"type": "error", "data": {"message": f"Unknown location: '{origin}'."}}
        destination_resolved = self._resolve_location(destination)
        if destination_resolved is None:
            return {"type": "error", "data": {"message": f"Unknown location: '{destination}'."}}

        deadline_int = self._parse_time(deadline)
        if deadline_int is None:
            return {"type": "error", "data": {"message": f"Invalid time format: '{deadline}'. Use HH:MM."}}

        itineraries = self.prolog.plan_trip(origin_resolved, destination_resolved, deadline_int)
        if not itineraries:
            return {
                "type": "error",
                "data": {"message": f"No scheduled trips found from {origin_resolved} to {destination_resolved} arriving by {deadline}."}
            }

        return {
            "type": "schedule",
            "data": {
                "origin": origin_resolved,
                "destination": destination_resolved,
                "deadline": deadline,
                "itineraries": itineraries,
            }
        }

    # ------------------------------------------------------------------
    # Route handling
    # ------------------------------------------------------------------

    def _handle_find_route(self, arguments: dict) -> dict:
        start_raw = arguments['start']
        end_raw = arguments['end']

        start = self._resolve_location(start_raw)
        if start is None:
            return {"type": "error", "data": {"message": f"Unknown location: '{start_raw}'."}}
        end = self._resolve_location(end_raw)
        if end is None:
            return {"type": "error", "data": {"message": f"Unknown location: '{end_raw}'."}}

        logger.info("Running Dijkstra from '%s' to '%s'", start, end)
        return self._find_and_format_route(start, end)

    # ------------------------------------------------------------------
    # Name resolution
    # ------------------------------------------------------------------

    def _resolve_location(self, raw_name: str) -> str | None:
        # 1. Exact match via Prolog resolve_location (attraction or station)
        resolved = self.prolog.resolve_location(raw_name)
        if resolved:
            return resolved

        # 2. Classified fuzzy match — Prolog infers candidates and classifies
        #    them as exact/prefix/substring; Python ranks and selects.
        candidates = self.prolog.match_station_classified(raw_name)
        if not candidates:
            # 3. No Prolog match — try edit-distance against all stations
            #    (handles typos like "Saim" → "Siam")
            return self._best_edit_distance_match(raw_name)

        best = self._rank_candidates(raw_name, candidates)
        if best:
            logger.info("Resolved '%s' → '%s'", raw_name, best)
            return best

        logger.info("Could not resolve location: '%s'", raw_name)
        return None

    # ------------------------------------------------------------------
    # Hybrid ranking: Prolog classifies, Python scores
    # ------------------------------------------------------------------

    # Priority order for match types (lower = better)
    _MATCH_TYPE_RANK = {"exact": 0, "prefix": 1, "substring": 2}

    def _rank_candidates(self, raw_name: str, candidates: list[dict]) -> str | None:
        """Pick the best candidate using Prolog's match classification
        and difflib similarity for tie-breaking."""
        if not candidates:
            return None

        raw_lower = raw_name.lower()

        def score(c):
            type_rank = self._MATCH_TYPE_RANK.get(c["match_type"], 9)
            similarity = SequenceMatcher(None, raw_lower, c["station"].lower()).ratio()
            # Sort by: type rank ascending, then similarity descending
            return (type_rank, -similarity)

        candidates_sorted = sorted(candidates, key=score)
        best = candidates_sorted[0]

        # Only accept substring matches if similarity is high enough
        if best["match_type"] == "substring":
            sim = SequenceMatcher(None, raw_lower, best["station"].lower()).ratio()
            if sim < 0.4:
                return None

        return best["station"]

    @staticmethod
    def _station_base_name(station: str) -> str:
        """Extract the station name without the code suffix, e.g. 'Siam (CEN)' → 'Siam'."""
        idx = station.find(" (")
        return station[:idx] if idx != -1 else station

    def _best_edit_distance_match(self, raw_name: str, threshold: float = 0.75) -> str | None:
        """Fallback: find the closest station by edit distance (handles typos).
        Compares against the base name (without station code) for better matching.
        Uses a high threshold (0.75) to avoid false positives on unrelated words."""
        all_stations = self.prolog.get_all_station_names()
        raw_lower = raw_name.lower()
        best_station = None
        best_score = 0.0
        for station in all_stations:
            base = self._station_base_name(station).lower()
            # Require similar length to avoid false positives on unrelated words
            if abs(len(raw_lower) - len(base)) > 1:
                continue
            sim = SequenceMatcher(None, raw_lower, base).ratio()
            if sim > best_score:
                best_score = sim
                best_station = station
        if best_score >= threshold:
            logger.info("Edit-distance matched '%s' → '%s' (score=%.2f)", raw_name, best_station, best_score)
            return best_station
        return None

    # ------------------------------------------------------------------
    # Route finding (Python Dijkstra, graph data pulled from Prolog)
    # ------------------------------------------------------------------

    def _find_and_format_route(self, start: str, end: str) -> dict:
        edges = self.prolog.get_all_edges()
        graph = self._build_graph(edges)
        path, cost = self._dijkstra(graph, start, end)

        if path is None:
            return {"type": "error", "data": {"message": f"No route found from '{start}' to '{end}'."}}

        # Delegate route step building to Prolog inference
        steps = self.prolog.build_route_steps(path)

        return {
            "type": "route",
            "data": {
                "from": path[0],
                "to": path[-1],
                "total_time": cost,
                "steps": steps,
            }
        }

    def _build_graph(self, edges):
        graph = {}
        for a, b, t in edges:
            graph.setdefault(a, []).append((b, t))
        return graph

    def _dijkstra(self, graph, start, end):
        heap = [(0, start, [start])]
        visited = set()
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

    def _format_route_text(self, data: dict) -> str:
        output = [
            f"Route: {data['from']}  →  {data['to']}",
            f"Estimated travel time: ~{data['total_time']} minutes\n",
        ]
        step_num = 1
        for step in data['steps']:
            if step['type'] == 'transfer':
                output.append(f"  [Transfer] Walk from {step['from']}  →  {step['to']}")
            else:
                output.append(f"  Step {step_num}: {step['line']}")
                output.append(f"    Board at : {step['board']}")
                output.append(f"    Alight at: {step['alight']}")
                step_num += 1
        return "\n".join(output)

    # ------------------------------------------------------------------
    # Prolog result formatting
    # ------------------------------------------------------------------

    def _format_prolog_result(self, result) -> str:
        if isinstance(result, str):
            return result
        if result is None:
            return "No results found."
        if not result:
            return "No."
        if all(b == {} for b in result):
            return "Yes."

        lines = []
        for binding in result:
            pairs = ",  ".join(f"{k} = {v}" for k, v in binding.items())
            lines.append(f"  {pairs}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Direct query methods (bypass LLM, used by API)
    # ------------------------------------------------------------------

    def find_route(self, start: str, end: str) -> dict:
        return self._handle_find_route({"start": start, "end": end})

    def get_all_stations_with_lines(self) -> list[dict]:
        station_lines = self.prolog.get_station_lines()
        return [
            {"name": name, "lines": lines}
            for name, lines in sorted(station_lines.items())
        ]

    def get_all_attractions(self) -> list[dict]:
        results = list(self.prolog.prolog.query("near_station(Attraction, Station)"))
        return [
            {"name": str(r["Attraction"]), "station": str(r["Station"])}
            for r in results
        ]

import heapq
import logging

from engine.llm.llm import LLMInterface
from engine.prolog import PrologInterface

logger = logging.getLogger("orchestrator")


LINE_DISPLAY_NAMES = {
    'bts_sukhumvit': 'BTS Sukhumvit Line',
    'bts_silom':     'BTS Silom Line',
    'gold':          'BTS Gold Line',
    'mrt_blue':      'MRT Blue Line',
    'airport_rail_link': 'Airport Rail Link',
}

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
        self._station_lines_cache = None
        self._all_stations_cache = None

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
        resolved = self.prolog.resolve_location(raw_name)
        if resolved:
            return resolved

        all_stations = self._get_all_stations()
        raw_lower = raw_name.lower()

        matches = [s for s in all_stations if raw_lower in s.lower()]
        if len(matches) == 1:
            logger.info("Fuzzy matched '%s' → '%s'", raw_name, matches[0])
            return matches[0]

        if len(matches) > 1:
            exact = [s for s in matches if s.lower().startswith(raw_lower)]
            if len(exact) == 1:
                logger.info("Fuzzy matched '%s' → '%s'", raw_name, exact[0])
                return exact[0]

        logger.info("Could not resolve location: '%s'", raw_name)
        return None

    def _get_all_stations(self):
        if self._all_stations_cache is None:
            self._all_stations_cache = self.prolog.get_all_station_names()
        return self._all_stations_cache

    # ------------------------------------------------------------------
    # Route finding (Python Dijkstra, graph data pulled from Prolog)
    # ------------------------------------------------------------------

    def _find_and_format_route(self, start: str, end: str) -> dict:
        edges = self.prolog.get_all_edges()
        graph = self._build_graph(edges)
        path, cost = self._dijkstra(graph, start, end)

        if path is None:
            return {"type": "error", "data": {"message": f"No route found from '{start}' to '{end}'."}}

        station_lines = self._get_station_lines()
        steps = self._build_route_steps(path, station_lines)

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

    def _get_station_lines(self):
        if self._station_lines_cache is None:
            self._station_lines_cache = self.prolog.get_station_lines()
        return self._station_lines_cache

    def _build_route_steps(self, path: list, station_lines: dict) -> list:
        steps = []
        i = 0
        while i < len(path) - 1:
            a = path[i]
            b = path[i + 1]
            a_lines = set(station_lines.get(a, []))
            b_lines = set(station_lines.get(b, []))
            shared = a_lines & b_lines

            if not shared:
                steps.append({
                    "type": "transfer",
                    "from": a,
                    "to": b,
                })
                i += 1
                continue

            seg_line = next(iter(shared))
            seg_start = a

            j = i + 1
            while j < len(path) - 1:
                c = path[j]
                d = path[j + 1]
                c_lines = set(station_lines.get(c, []))
                d_lines = set(station_lines.get(d, []))
                if seg_line in (c_lines & d_lines):
                    j += 1
                else:
                    break

            seg_end = path[j]
            stations_in_segment = path[i:j + 1]
            display = LINE_DISPLAY_NAMES.get(seg_line, seg_line)
            steps.append({
                "type": "ride",
                "line": display,
                "board": seg_start,
                "alight": seg_end,
                "stations": stations_in_segment,
            })
            i = j

        return steps

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
        station_lines = self._get_station_lines()
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

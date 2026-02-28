import heapq
import logging

from llms.llm import LLMInterface
from prolog import PrologInterface

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

    def handle(self, user_input: str) -> str:
        result = self.llm.translate_to_query(user_input)
        if not result:
            return "Sorry, I couldn't process your request."

        function_name, arguments = result
        logger.info("Dispatching: %s", function_name)

        # Route finding → resolve names then Python Dijkstra
        if function_name == 'find_route':
            start_raw = arguments['start']
            end_raw = arguments['end']

            start = self._resolve_location(start_raw)
            if start is None:
                return f"Unknown location: '{start_raw}'."
            end = self._resolve_location(end_raw)
            if end is None:
                return f"Unknown location: '{end_raw}'."

            logger.info("Running Dijkstra from '%s' to '%s'", start, end)
            return self._find_and_format_route(start, end)

        # Knowledge-base queries → resolve station names, then Prolog
        if function_name in STATION_ARG_KEYS:
            for key in STATION_ARG_KEYS[function_name]:
                raw = arguments[key]
                resolved = self._resolve_location(raw)
                if resolved is None:
                    return f"Unknown location: '{raw}'."
                arguments[key] = resolved

        query_builder = PROLOG_QUERY_MAP.get(function_name)
        if query_builder is None:
            return f"Unknown function: {function_name}"

        prolog_query = query_builder(arguments)
        logger.info("Prolog query: %s", prolog_query)
        prolog_result = self.prolog.query(prolog_query)
        logger.info("Prolog result: %s", prolog_result)
        return self._format_prolog_result(prolog_result)

    # ------------------------------------------------------------------
    # Name resolution
    # ------------------------------------------------------------------

    def _resolve_location(self, raw_name: str) -> str | None:
        """Resolve a raw user-provided name to an exact station name.

        1. Try Prolog resolve_location (handles attractions and exact station names)
        2. Fallback: case-insensitive substring match against all station names
        """
        # Try Prolog first (exact attraction or station match)
        resolved = self.prolog.resolve_location(raw_name)
        if resolved:
            return resolved

        # Fallback: fuzzy substring match
        all_stations = self._get_all_stations()
        raw_lower = raw_name.lower()

        # Try substring match (e.g. "Siam" matches "Siam (CEN)")
        matches = [s for s in all_stations if raw_lower in s.lower()]
        if len(matches) == 1:
            logger.info("Fuzzy matched '%s' → '%s'", raw_name, matches[0])
            return matches[0]

        # If multiple matches, try matching just the name part before the code
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

    def _find_and_format_route(self, start: str, end: str) -> str:
        edges = self.prolog.get_all_edges()
        graph = self._build_graph(edges)
        path, cost = self._dijkstra(graph, start, end)

        if path is None:
            return f"No route found from '{start}' to '{end}'."

        station_lines = self._get_station_lines()
        return self._format_route(path, cost, station_lines)

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

    def _format_route(self, path: list, cost: int, station_lines: dict) -> str:
        output = [
            f"Route: {path[0]}  →  {path[-1]}",
            f"Estimated travel time: ~{cost} minutes\n",
        ]

        step = 1
        i = 0
        while i < len(path) - 1:
            a = path[i]
            b = path[i + 1]
            a_lines = set(station_lines.get(a, []))
            b_lines = set(station_lines.get(b, []))
            shared = a_lines & b_lines

            if not shared:
                # No common line → inter-line transfer (walking connection)
                output.append(f"  [Transfer] Walk from {a}  →  {b}")
                i += 1
                continue

            # Ride this line as far as possible before the line changes
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
            display = LINE_DISPLAY_NAMES.get(seg_line, seg_line)
            output.append(f"  Step {step}: {display}")
            output.append(f"    Board at : {seg_start}")
            output.append(f"    Alight at: {seg_end}")
            step += 1
            i = j

        return "\n".join(output)

    # ------------------------------------------------------------------
    # Prolog result formatting
    # ------------------------------------------------------------------

    def _format_prolog_result(self, result) -> str:
        if isinstance(result, str):
            # Error message returned by PrologInterface.query
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

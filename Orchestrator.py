import heapq
import re

from llm import LLMInterface
from prolog import PrologInterface


LINE_DISPLAY_NAMES = {
    'bts_sukhumvit': 'BTS Sukhumvit Line',
    'bts_silom':     'BTS Silom Line',
    'gold':          'BTS Gold Line',
    'mrt_blue':      'MRT Blue Line',
    'airport_rail_link': 'Airport Rail Link',
}

FIND_ROUTE_PATTERN = re.compile(r"^find_route\('([^']+)',\s*'([^']+)'\)\.$")


class Orchestrator:
    def __init__(self):
        self.llm = LLMInterface()
        self.prolog = PrologInterface()
        self._station_lines_cache = None

    def handle(self, user_input: str) -> str:
        query = self.llm.translate_to_query(user_input)
        if not query:
            return "Sorry, I couldn't process your request."

        query = query.strip()

        # Detect find_route sentinel → delegate to Python path-finding
        match = FIND_ROUTE_PATTERN.match(query)
        if match:
            start, end = match.group(1), match.group(2)
            return self._find_and_format_route(start, end)

        # Otherwise forward to Prolog reasoning engine
        result = self.prolog.query(query)
        return self._format_prolog_result(result)

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
        if result == [{}]:
            return "Yes."

        lines = []
        for binding in result:
            pairs = ",  ".join(f"{k} = {v}" for k, v in binding.items())
            lines.append(f"  {pairs}")
        return "\n".join(lines)

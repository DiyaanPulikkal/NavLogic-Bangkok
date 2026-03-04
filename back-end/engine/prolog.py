import logging
import os
import re
from pyswip import Prolog

logger = logging.getLogger("prolog")

KB_PATH = os.path.join(os.path.dirname(__file__), "knowledge_base.pl")


class PrologInterface:
    def __init__(self):
        self.prolog = Prolog()
        self.prolog.consult(KB_PATH)

    def is_valid_query(self, query):
        pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*\((.*)\)\.$'
        return re.match(pattern, query) is not None

    def query(self, query):
        if self.is_valid_query(query):
            try:
                logger.info("Executing Prolog query: %s", query)
                result = list(self.prolog.query(query[:-1]))
                logger.info("Prolog returned %d result(s)", len(result))
                return result
            except Exception as e:
                logger.error("Error executing query: %s", e)
                return f"Error executing query: {e}"

    def get_all_edges(self):
        """Return all bidirectional edges as (station_a, station_b, time) tuples."""
        logger.info("Executing Prolog query: edge(A, B, T)")
        edges = [
            (str(r['A']), str(r['B']), int(r['T']))
            for r in self.prolog.query("edge(A, B, T)")
        ]
        logger.info("Prolog returned %d result(s)", len(edges))
        return edges

    def get_station_lines(self):
        """Return a dict mapping each station name to its list of lines."""
        logger.info("Executing Prolog query: station(S, L)")
        mapping = {}
        count = 0
        for r in self.prolog.query("station(S, L)"):
            mapping.setdefault(str(r['S']), []).append(str(r['L']))
            count += 1
        logger.info("Prolog returned %d result(s)", count)
        return mapping

    def resolve_location(self, name):
        """Resolve a location name (attraction or station) to a station name via Prolog."""
        logger.info("Resolving location: %s", name)
        results = list(self.prolog.query(f"resolve_location('{name}', Station)"))
        if results:
            station = str(results[0]['Station'])
            logger.info("Resolved '%s' → '%s'", name, station)
            return station
        logger.info("Could not resolve location: %s", name)
        return None

    def is_valid_station(self, name):
        """Check if a station name exists in the network."""
        results = list(self.prolog.query(f"valid_station('{name}')"))
        return len(results) > 0

    def get_all_station_names(self):
        """Return a list of all station names in the network."""
        return list({str(r['S']) for r in self.prolog.query("station(S, _)")})

    # ------------------------------------------------------------------
    # New methods delegating reasoning to Prolog rules (rules.pl)
    # ------------------------------------------------------------------

    def build_route_steps(self, path_list: list) -> list:
        """Call route_steps/2 in Prolog and parse the result into Python dicts."""
        if len(path_list) < 2:
            return []

        prolog_list = "[" + ", ".join(f"'{s}'" for s in path_list) + "]"
        query = f"route_steps({prolog_list}, Steps)"
        logger.info("Executing Prolog query: %s", query)

        results = list(self.prolog.query(query))
        if not results:
            return []

        raw_steps = results[0]['Steps']
        return self._parse_route_steps(raw_steps)

    def _parse_route_steps(self, steps_term) -> list:
        """Convert Prolog step terms (serialized as strings by pyswip) into Python dicts."""
        parsed = []
        for step in steps_term:
            s = str(step)
            if s.startswith('ride('):
                parsed.append(self._parse_ride_step(s))
            elif s.startswith('transfer('):
                inner = s[len('transfer('):-1]
                parts = self._split_top_level(inner)
                parsed.append({
                    "type": "transfer",
                    "from": parts[0].strip(),
                    "to": parts[1].strip(),
                })
        return parsed

    def _parse_ride_step(self, s: str) -> dict:
        """Parse a ride(...) string from Prolog."""
        inner = s[len('ride('):-1]
        parts = self._split_top_level(inner)
        line = parts[0].strip()
        board = parts[1].strip()
        alight = parts[2].strip()
        stations_str = parts[3].strip()
        # Parse the stations list: ['Station A', 'Station B', ...]
        if stations_str.startswith('[') and stations_str.endswith(']'):
            stations_inner = stations_str[1:-1]
            stations = [st.strip().strip("'") for st in self._split_top_level(stations_inner)]
        else:
            stations = [stations_str]
        return {
            "type": "ride",
            "line": line,
            "board": board,
            "alight": alight,
            "stations": stations,
        }

    @staticmethod
    def _split_top_level(s: str) -> list:
        """Split a string by commas, respecting parentheses and brackets."""
        parts = []
        depth = 0
        current = []
        for ch in s:
            if ch in ('(', '['):
                depth += 1
                current.append(ch)
            elif ch in (')', ']'):
                depth -= 1
                current.append(ch)
            elif ch == ',' and depth == 0:
                parts.append(''.join(current))
                current = []
            else:
                current.append(ch)
        if current:
            parts.append(''.join(current))
        return parts

    def fuzzy_match_station(self, name: str) -> list:
        """Call fuzzy_match_station/2 in Prolog to find matching stations."""
        safe_name = name.replace("'", "\\'")
        query = f"fuzzy_match_station('{safe_name}', Station)"
        logger.info("Executing Prolog query: %s", query)
        results = list(self.prolog.query(query))
        return list({str(r['Station']) for r in results})

    def match_station_classified(self, name: str) -> list[dict]:
        """Call match_station/3 in Prolog to get candidates with match type.

        Returns a list of dicts: [{"station": str, "match_type": str}, ...]
        where match_type is one of: "exact", "prefix", "substring".
        Prolog handles the classification logic; Python handles ranking.
        """
        safe_name = name.replace("'", "\\'")
        query = f"match_station('{safe_name}', Station, MatchType)"
        logger.info("Executing Prolog query: %s", query)
        results = list(self.prolog.query(query))
        # Deduplicate (a station on multiple lines produces duplicate rows)
        seen = set()
        candidates = []
        for r in results:
            station = str(r['Station'])
            if station not in seen:
                seen.add(station)
                candidates.append({
                    "station": station,
                    "match_type": str(r['MatchType']),
                })
        return candidates

    def suggest_transfer_station(self, line_a: str, line_b: str) -> list:
        """Find interchange stations connecting two lines."""
        query = f"suggest_transfer_station({line_a}, {line_b}, Transfer)"
        logger.info("Executing Prolog query: %s", query)
        results = list(self.prolog.query(query))
        transfers = []
        for r in results:
            t = r['Transfer']
            if isinstance(t, str):
                transfers.append({"type": "same_station", "station": t})
            else:
                transfers.append({
                    "type": "walk",
                    "from": str(t.args[0]),
                    "to": str(t.args[1]),
                })
        return transfers

    def get_line_display_name(self, line_id: str) -> str:
        """Look up the display name for a line via Prolog."""
        results = list(self.prolog.query(f"line_display_name({line_id}, Name)"))
        if results:
            return str(results[0]['Name'])
        return line_id
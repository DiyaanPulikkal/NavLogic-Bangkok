import logging
import re
from pyswip import Prolog

logger = logging.getLogger("prolog")


class PrologInterface:
    def __init__(self):
        self.prolog = Prolog()
        self.prolog.consult("knowledge_base.pl")

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
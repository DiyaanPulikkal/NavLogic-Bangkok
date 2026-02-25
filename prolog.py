import re
from pyswip import Prolog

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
                result = list(self.prolog.query(query[:-1]))
                return result
            except Exception as e:
                return f"Error executing query: {e}"

    def get_all_edges(self):
        """Return all bidirectional edges as (station_a, station_b, time) tuples."""
        return [
            (str(r['A']), str(r['B']), int(r['T']))
            for r in self.prolog.query("edge(A, B, T)")
        ]

    def get_station_lines(self):
        """Return a dict mapping each station name to its list of lines."""
        mapping = {}
        for r in self.prolog.query("station(S, L)"):
            mapping.setdefault(str(r['S']), []).append(str(r['L']))
        return mapping
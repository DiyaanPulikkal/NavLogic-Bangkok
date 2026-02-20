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
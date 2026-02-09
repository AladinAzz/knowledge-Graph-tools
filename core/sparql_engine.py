from rdflib.plugins.sparql import prepareQuery
from rdflib.query import Result

class SPARQLEngine:
    def __init__(self, rdf_manager):
        self.rdf_manager = rdf_manager

    def execute_query(self, query_str):
        """Executes a SPARQL query on the loaded graph."""
        graph = self.rdf_manager.get_graph()
        try:
            # Prepare query to catch syntax errors early
            # query = prepareQuery(query_str) 
            # Direct execution handles it too
            results = graph.query(query_str)
            return results
        except Exception as e:
            raise Exception(f"Query execution failed: {e}")

    def format_results(self, results):
        """Formats the query results into a dictionary."""
        if results.type == 'SELECT':
            return {
                "type": "SELECT",
                "vars": results.vars,
                "bindings": [
                    {str(var): str(row[var]) for var in results.vars}
                    for row in results
                ]
            }
        elif results.type == 'ASK':
            return {
                "type": "ASK",
                "boolean": results.askAnswer
            }
        elif results.type == 'CONSTRUCT' or results.type == 'DESCRIBE':
            # Returns a graph
            return {
                "type": results.type,
                "graph": results.graph
            }
        return {"type": "UNKNOWN", "data": results}

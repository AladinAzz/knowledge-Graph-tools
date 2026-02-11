"""
SPARQL Engine Module

This module executes SPARQL queries against an RDF graph.
It wraps rdflib's query processor and processes the results into a standardized dictionary format
suitable for the GUI. It supports SELECT, ASK, CONSTRUCT, and DESCRIBE queries.
"""

from rdflib.plugins.sparql import prepareQuery
from rdflib.query import Result

class SPARQLEngine:
    """
    Handles execution of SPARQL queries on an RDFManager's graph.
    """
    def __init__(self, rdf_manager):
        """
        Initializes the SPARQLEngine.
        
        Args:
            rdf_manager (RDFManager): The instance managing the RDF graph to query.
        """
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
            # Binding results are row-based.
            # We return raw rdflib terms to allow graph reconstruction in UI if needed.
            # Serialization (str conversion) can happen at display time.
            return {
                "type": "SELECT",
                "vars": results.vars,
                "bindings": [
                    {str(var): row[var] for var in results.vars}
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

"""
SPARQL Engine Module

This module executes SPARQL queries (SELECT, CONSTRUCT, ASK, DESCRIBE)
and SPARQL UPDATE operations (INSERT, DELETE) against an RDF graph.
It wraps rdflib's query/update processor and processes the results into a standardized
dictionary format suitable for the GUI.
"""

from rdflib.plugins.sparql import prepareQuery
from rdflib.query import Result
import re
import time

class SPARQLEngine:
    """
    Handles execution of SPARQL queries and updates on an RDFManager's graph.
    """
    def __init__(self, rdf_manager):
        """
        Initializes the SPARQLEngine.
        
        Args:
            rdf_manager (RDFManager): The instance managing the RDF graph to query.
        """
        self.rdf_manager = rdf_manager

    def execute_query(self, query_str):
        """Executes a SPARQL query on the loaded graph. Returns (results, elapsed_seconds)."""
        graph = self.rdf_manager.get_graph()
        start_time = time.perf_counter()
        try:
            results = graph.query(query_str)
            elapsed = time.perf_counter() - start_time
            return results, elapsed
        except Exception as e:
            raise Exception(f"Query execution failed: {e}")
    
    def execute_update(self, query_str):
        """Executes a SPARQL UPDATE (INSERT/DELETE) on the loaded graph. Returns (info_dict, elapsed_seconds)."""
        graph = self.rdf_manager.get_graph()
        initial_count = len(graph)
        start_time = time.perf_counter()
        try:
            graph.update(query_str)
            elapsed = time.perf_counter() - start_time
            final_count = len(graph)
            return {
                "type": "UPDATE",
                "success": True,
                "triples_before": initial_count,
                "triples_after": final_count,
                "delta": final_count - initial_count,
            }, elapsed
        except Exception as e:
            raise Exception(f"UPDATE execution failed: {e}")
    
    def is_update_query(self, query_str):
        """Detects if a query is a SPARQL UPDATE (INSERT/DELETE) vs a standard query."""
        # Strip comments and prefixes to find the actual operation keyword
        cleaned = re.sub(r'#[^\n]*', '', query_str)  # Remove comments
        cleaned = re.sub(r'PREFIX\s+\S+\s+<[^>]+>', '', cleaned, flags=re.IGNORECASE)  # Remove PREFIX
        cleaned = re.sub(r'BASE\s+<[^>]+>', '', cleaned, flags=re.IGNORECASE)  # Remove BASE
        cleaned = cleaned.strip()
        
        update_keywords = ['INSERT', 'DELETE', 'LOAD', 'CLEAR', 'DROP', 'CREATE', 'COPY', 'MOVE', 'ADD']
        first_word = cleaned.split()[0].upper() if cleaned.split() else ""
        return first_word in update_keywords

    def format_results(self, results):
        """Formats the query results into a dictionary."""
        if results.type == 'SELECT':
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

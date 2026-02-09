from rdflib import Graph, URIRef, Literal
from rdflib.exceptions import ParserError
import os

class RDFManager:
    def __init__(self):
        self.graph = Graph()

    def load_file(self, file_path):
        """Loads an RDF file into the graph."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Determine format from extension if possible, otherwise let rdflib guess
        file_ext = os.path.splitext(file_path)[1].lower()
        fmt = None
        if file_ext == '.ttl':
            fmt = 'turtle'
        elif file_ext == '.xml' or file_ext == '.rdf':
            fmt = 'xml'
        elif file_ext == '.nt':
            fmt = 'nt'
            
        try:
            self.graph.parse(file_path, format=fmt)
        except Exception as e:
            raise ParserError(f"Failed to parse file: {e}")

    def save_file(self, file_path, fmt):
        """Saves the graph to a file in the specified format."""
        try:
            self.graph.serialize(destination=file_path, format=fmt)
        except Exception as e:
            raise Exception(f"Failed to save file: {e}")

    def get_statistics(self):
        """Returns basic statistics about the graph."""
        return {
            "num_triples": len(self.graph),
            "num_subjects": len(set(self.graph.subjects())),
            "num_predicates": len(set(self.graph.predicates())),
            "num_objects": len(set(self.graph.objects())),
        }

    def get_graph(self):
        return self.graph

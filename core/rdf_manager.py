"""
RDF Manager Module

This module handles the loading, saving, and basic management of RDF graphs using rdflib.
It provides a wrapper around the rdflib.Graph object to simplify common operations
such as parsing different file formats (Turtle, RDF/XML, N-Triples) and extracting statistics.
"""

from rdflib import Graph, URIRef, Literal
from rdflib.exceptions import ParserError
import os

class RDFManager:
    """
    Manages an RDF graph, providing methods to load, save, and inspect it.
    """
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

    def get_namespaces(self):
        """Returns a list of (prefix, uri) tuples."""
        return list(self.graph.namespaces())

    def bind_namespace(self, prefix, uri):
        """Binds a prefix to a URI."""
        self.graph.bind(prefix, uri)

    def remove_namespace(self, prefix):
        """Removes a namespace binding (requires rdflib graph bind with override or unbind logic)."""
        # rdflib Graph.bind(override=True) might be needed if replacing.
        # To remove, we might need to access the store's namespace manager directly.
        # self.graph.namespace_manager.bind(prefix, uri, override=True)
        # But to delete?
        # self.graph.namespace_manager.remove((prefix, None)) # remove by prefix?
        # Let's check rdflib docs or implementation logic.
        # NamespaceManager has remove((prefix, namespace)).
        # We need the URI to remove it safely? Or just iterate.
        
        ns_manager = self.graph.namespace_manager
        # Find uri for prefix
        uri = None
        for p, u in ns_manager.namespaces():
            if p == prefix:
                uri = u
                break
        
        if uri:
            ns_manager.remove((prefix, uri))

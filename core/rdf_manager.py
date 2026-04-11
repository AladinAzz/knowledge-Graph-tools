"""
RDF Manager Module

This module handles the loading, saving, and basic management of RDF graphs using rdflib.
It provides a wrapper around the rdflib.Graph object to simplify common operations
such as parsing different file formats (Turtle, RDF/XML, N-Triples, Turtle-star, N-Triples-star)
and extracting statistics.
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
        elif file_ext == '.trig':
            fmt = 'trig'
        elif file_ext == '.xml' or file_ext == '.rdf' or file_ext == '.owl':
            fmt = 'xml'
        elif file_ext == '.nt':
            fmt = 'nt'
        elif file_ext == '.nq':
            fmt = 'nquads'
        elif file_ext == '.jsonld':
            fmt = 'json-ld'
            
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
        subjects = set(self.graph.subjects())
        predicates = set(self.graph.predicates())
        objects = set(self.graph.objects())
        
        # Count classes and properties
        from rdflib import RDF, OWL, RDFS
        classes = set()
        for s, p, o in self.graph.triples((None, RDF.type, None)):
            classes.add(o)
        
        return {
            "num_triples": len(self.graph),
            "num_subjects": len(subjects),
            "num_predicates": len(predicates),
            "num_objects": len(objects),
            "num_classes": len(classes),
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
        """Removes a namespace binding. Compatible with rdflib 6.x and 7.x."""
        ns_manager = self.graph.namespace_manager
        
        # Find uri for prefix
        uri = None
        for p, u in ns_manager.namespaces():
            if p == prefix:
                uri = u
                break
        
        if uri is None:
            return
        
        # Try multiple approaches for compatibility
        try:
            # rdflib 6.x approach
            if hasattr(ns_manager, 'remove'):
                ns_manager.remove((prefix, uri))
                return
        except (AttributeError, TypeError):
            pass
        
        try:
            # rdflib 7.x: rebind all namespaces except the one to remove
            existing = [(p, u) for p, u in ns_manager.namespaces() if p != prefix]
            # Reset namespace bindings by rebinding all except target
            for p, u in existing:
                self.graph.bind(p, u, override=True, replace=True)
        except Exception as e:
            print(f"Warning: Could not remove namespace '{prefix}': {e}")

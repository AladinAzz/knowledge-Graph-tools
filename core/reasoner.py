"""
Reasoning Engine Module

This module performs reasoning logic on ontologies using owlready2.
It integrates with reasoners like HermiT and Pellet to infer new facts (triples)
from the existing ontology and data. The inferred triples are then converted
back to a format compatible with the rest of the application (rdflib graph).
"""

from owlready2 import sync_reasoner_pellet, sync_reasoner, World, Ontology
import rdflib
import os
import pathlib
import time

class ReasoningEngine:
    """
    Manages the reasoning process using owlready2's sync_reasoner.
    """
    def __init__(self):
        # We might need a dedicated World for isolation if handling multiple
        self.world = World()

    def run_reasoner(self, ontology_path, reasoner_type='hermit'):
        """
        Runs the reasoner on the given ontology.
        Returns a tuple of (inferred_graph, elapsed_seconds).
        """
        start_time = time.perf_counter()
        try:
            # Load ontology into the isolated world
            # owlready2 handles paths natively — avoid pathlib.as_uri() which
            # produces /C:/... on Windows after owlready2 strips the scheme.
            if ontology_path.startswith('http'):
                iri = ontology_path
            else:
                abs_path = str(pathlib.Path(ontology_path).resolve())
                iri = "file://" + abs_path.replace("\\", "/")
                
            onto = self.world.get_ontology(iri).load()
            
            with onto:
                if reasoner_type == 'pellet':
                    sync_reasoner_pellet(self.world, infer_property_values=True, infer_data_property_values=True)
                else:
                    sync_reasoner(self.world, infer_property_values=True)
            
            # After reasoning, save the ontology to a temporary format to capture inferences
            # owlready2 modifies the ontology in-memory.
            # We can save it to an RDF/XML string/file and parse it with rdflib.
            import tempfile
            
            with tempfile.NamedTemporaryFile(suffix=".owl", delete=False) as tmp:
                temp_path = tmp.name
                
            try:
                onto.save(file=temp_path, format="rdfxml")
                
                g = rdflib.Graph()
                g.parse(temp_path, format="xml")
                elapsed = time.perf_counter() - start_time
                return g, elapsed
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        except Exception as e:
            raise Exception(f"Reasoning failed: {e}")
            
    def apply_inference_to_graph(self, original_graph: rdflib.Graph, inferred_graph: rdflib.Graph):
        """
        Calculates the difference to find actual inferred triples.
        Uses structural fragment matching to brutally ignore any URI Prefix changes 
        caused by temp files or Pyinstaller environment differences.
        """
        from rdflib import Graph
        new_triples = Graph()
        
        def get_frag(uri):
            s = str(uri)
            if '#' in s: return s.split('#')[-1]
            if '/' in s: return s.split('/')[-1]
            return s
            
        orig_signatures = {(get_frag(s), get_frag(p), get_frag(o)) for s, p, o in original_graph}
        
        for s, p, o in inferred_graph:
            sig = (get_frag(s), get_frag(p), get_frag(o))
            if sig not in orig_signatures:
                new_triples.add((s, p, o))
                
        return new_triples

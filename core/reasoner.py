from owlready2 import sync_reasoner_pellet, sync_reasoner, World, Ontology
import rdflib
import os

class ReasoningEngine:
    def __init__(self):
        # We might need a dedicated World for isolation if handling multiple
        self.world = World()

    def run_reasoner(self, ontology_path, reasoner_type='hermit'):
        """
        Runs the reasoner on the given ontology.
        Returns a list of inferred triples (this is tricky with owlready2 directly, 
        usually it updates the ontology in place).
        """
        try:
            # Load ontology into the isolated world
            if not ontology_path.startswith('file://') and not ontology_path.startswith('http'):
                iri = f"file://{ontology_path}"
            else:
                iri = ontology_path
                
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
                return g
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        except Exception as e:
            raise Exception(f"Reasoning failed: {e}")
            
    def apply_inference_to_graph(self, original_graph: rdflib.Graph, inferred_graph: rdflib.Graph):
        """
        Calculates the difference to find actual inferred triples.
        """
        inferred_triples = inferred_graph - original_graph
        return inferred_triples

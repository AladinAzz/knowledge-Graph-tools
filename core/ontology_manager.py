from owlready2 import get_ontology, Thing, ObjectProperty, DataProperty
import types

class OntologyManager:
    def __init__(self):
        self.ontology = None

    def load_ontology(self, file_path):
        """Loads an ontology from a file."""
        try:
            # owlready2 prefers file:// for local paths
            if not file_path.startswith('http') and not file_path.startswith('file://'):
                iri = f"file://{file_path}"
            else:
                iri = file_path
                
            self.ontology = get_ontology(iri).load()
        except Exception as e:
            raise Exception(f"Failed to load ontology: {e}")

    def get_classes(self):
        """Returns a list of classes in the ontology."""
        if not self.ontology:
            return []
        return list(self.ontology.classes())

    def get_properties(self):
        """Returns a list of properties in the ontology."""
        if not self.ontology:
            return []
        return list(self.ontology.properties())

    def get_hierarchy(self):
        """
        Returns a nested dictionary representing the class hierarchy.
        Foundational Root: Thing
        """
        if not self.ontology:
            return {}

        def build_hierarchy(cls):
            children = []
            # owlready2 subclasses() returns a generator
            try:
                for sub in cls.subclasses():
                    children.append(build_hierarchy(sub))
            except AttributeError:
                # Some entities might not have subclasses method working as expected in all cases
                pass
            
            return {
                "name": cls.name,
                "iri": cls.iri,
                "children": children
            }

        # Start from Thing
        return build_hierarchy(Thing)

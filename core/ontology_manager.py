"""
Ontology Manager Module

This module is responsible for loading and inspecting OWL/RDFS ontologies using owlready2.
It allows loading ontology files and extracting the class hierarchy and properties for visualization.
Note: owlready2 is used for ontology-specific features (classes, properties, reasoning compatibility),
while rdflib is used for general graph operations in other modules.
"""

from owlready2 import get_ontology, Thing, ObjectProperty, DataProperty
import pathlib
import types

class OntologyManager:
    """
    Manages ontology loading and inspection using owlready2.
    """
    def __init__(self):
        self.ontology = None

    def load_ontology(self, file_path):
        """Loads an ontology from a file."""
        try:
            # owlready2 handles absolute paths natively — avoid manual file:// URI
            # construction which produces /C:/... on Windows (invalid path).
            if file_path.startswith('http'):
                iri = file_path
            else:
                # Resolve to absolute path and convert to a proper owlready2 IRI
                abs_path = str(pathlib.Path(file_path).resolve())
                iri = "file://" + abs_path.replace("\\", "/")
                
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
    
    def get_object_properties(self):
        """Returns a list of object properties in the ontology."""
        if not self.ontology:
            return []
        return list(self.ontology.object_properties())
    
    def get_data_properties(self):
        """Returns a list of data properties in the ontology."""
        if not self.ontology:
            return []
        return list(self.ontology.data_properties())

    def get_hierarchy(self):
        """
        Returns a nested dictionary representing the class hierarchy.
        Foundational Root: Thing
        """
        if not self.ontology:
            return {}

        def build_hierarchy(cls, classes_set):
            children = []
            try:
                for sub in cls.subclasses():
                    if sub in classes_set:
                        children.append(build_hierarchy(sub, classes_set))
            except AttributeError:
                pass
            
            return {
                "name": getattr(cls, 'name', str(cls)),
                "iri": getattr(cls, 'iri', ''),
                "children": children
            }

        # Identify root classes in the ontology
        classes = list(self.ontology.classes())
        classes_set = set(classes)
        
        root_classes = []
        for cls in classes:
            is_root = True
            try:
                for p in cls.is_a:
                    if p != Thing and p in classes_set:
                        is_root = False
                        break
            except Exception:
                pass
                
            if is_root:
                root_classes.append(cls)

        # Build hierarchy starting from the identified root classes
        roots_hierarchy = [build_hierarchy(rc, classes_set) for rc in root_classes]
        
        return {
            "name": "Thing",
            "iri": "http://www.w3.org/2002/07/owl#Thing",
            "children": roots_hierarchy
        }
    
    def get_properties_info(self):
        """Returns structured info about properties for display."""
        if not self.ontology:
            return []
        
        props_info = []
        for prop in self.ontology.properties():
            info = {
                "name": prop.name,
                "iri": prop.iri,
                "type": "ObjectProperty" if isinstance(prop, ObjectProperty) else "DataProperty",
                "domain": [str(d.name) if hasattr(d, 'name') else str(d) for d in prop.domain] if hasattr(prop, 'domain') else [],
                "range": [str(r.name) if hasattr(r, 'name') else str(r) for r in prop.range] if hasattr(prop, 'range') else [],
            }
            props_info.append(info)
        
        return props_info

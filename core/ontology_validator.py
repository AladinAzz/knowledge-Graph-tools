"""
Ontology Validator Module

This module provides ontology validation using owlready2's consistency checking.
It reports inconsistent classes, unsatisfiable classes, and structural issues.
"""

from owlready2 import get_ontology, sync_reasoner, World, Thing, Nothing
import pathlib


class OntologyValidator:
    """Validates OWL ontologies for consistency and structural issues."""
    
    def __init__(self):
        self.world = World()
    
    def validate(self, ontology_path):
        """
        Validates an ontology file and returns a list of validation results.
        Each result is a dict: {"severity": "error"|"warning"|"info", "message": str}
        """
        results = []
        
        try:
            # Load ontology
            # owlready2 handles paths natively — avoid pathlib.as_uri() which
            # produces /C:/... on Windows after owlready2 strips the scheme.
            if ontology_path.startswith('http'):
                iri = ontology_path
            else:
                abs_path = str(pathlib.Path(ontology_path).resolve())
                iri = "file://" + abs_path.replace("\\", "/")
            
            onto = self.world.get_ontology(iri).load()
            
            # 1. Check for classes
            classes = list(onto.classes())
            if not classes:
                results.append({
                    "severity": "warning",
                    "message": "No classes defined in the ontology."
                })
            else:
                results.append({
                    "severity": "info",
                    "message": f"Found {len(classes)} class(es): {', '.join(c.name for c in classes[:10])}"
                    + ("..." if len(classes) > 10 else "")
                })
            
            # 2. Check for properties
            props = list(onto.properties())
            if not props:
                results.append({
                    "severity": "warning",
                    "message": "No properties defined in the ontology."
                })
            else:
                results.append({
                    "severity": "info",
                    "message": f"Found {len(props)} property(ies)."
                })
            
            # 3. Check for individuals
            individuals = list(onto.individuals())
            results.append({
                "severity": "info",
                "message": f"Found {len(individuals)} individual(s)."
            })
            
            # 4. Check properties with missing domain/range
            for prop in props:
                if not prop.domain:
                    results.append({
                        "severity": "warning",
                        "message": f"Property '{prop.name}' has no domain defined."
                    })
                if not prop.range:
                    results.append({
                        "severity": "warning",
                        "message": f"Property '{prop.name}' has no range defined."
                    })
            
            # 5. Run consistency check via reasoner
            try:
                with onto:
                    sync_reasoner(self.world, infer_property_values=False)
                
                # Check for unsatisfiable classes (equivalent to Nothing)
                unsatisfiable = list(onto.inconsistent_classes()) if hasattr(onto, 'inconsistent_classes') else []
                
                if unsatisfiable:
                    for cls in unsatisfiable:
                        results.append({
                            "severity": "error",
                            "message": f"Unsatisfiable class: '{cls.name}' — cannot have any instances."
                        })
                else:
                    results.append({
                        "severity": "info",
                        "message": "Consistency check passed: No unsatisfiable classes found."
                    })
                    
            except Exception as e:
                error_str = str(e)
                if "inconsistent" in error_str.lower():
                    results.append({
                        "severity": "error",
                        "message": f"Ontology is INCONSISTENT: {e}"
                    })
                else:
                    results.append({
                        "severity": "warning",
                        "message": f"Could not run consistency check (reasoner error): {e}"
                    })
            
            # 6. Check for orphan classes (no parent other than Thing)
            for cls in classes:
                parents = [p for p in cls.is_a if p is not Thing and hasattr(p, 'name')]
                children = list(cls.subclasses())
                if not parents and not children and cls is not Thing:
                    results.append({
                        "severity": "info",
                        "message": f"Class '{cls.name}' is isolated (no parent other than Thing, no children)."
                    })
            
        except Exception as e:
            results.append({
                "severity": "error",
                "message": f"Failed to load ontology for validation: {e}"
            })
        
        return results

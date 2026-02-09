import pytest
from core.ontology_manager import OntologyManager
from owlready2 import get_ontology
import os

SAMPLE_OWL = """<?xml version="1.0"?>
<rdf:RDF xmlns="http://example.org/onto.owl#"
     xml:base="http://example.org/onto.owl"
     xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
     xmlns:owl="http://www.w3.org/2002/07/owl#"
     xmlns:xml="http://www.w3.org/XML/1998/namespace"
     xmlns:xsd="http://www.w3.org/2001/XMLSchema#"
     xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">
    <owl:Ontology rdf:about="http://example.org/onto.owl"/>
    
    <owl:Class rdf:about="http://example.org/onto.owl#Animal"/>
    <owl:Class rdf:about="http://example.org/onto.owl#Cat">
        <rdfs:subClassOf rdf:resource="http://example.org/onto.owl#Animal"/>
    </owl:Class>
</rdf:RDF>
"""

def test_load_ontology(tmp_path):
    d = tmp_path / "subdir"
    d.mkdir()
    p = d / "test.owl"
    p.write_text(SAMPLE_OWL, encoding='utf-8')
    
    manager = OntologyManager()
    manager.load_ontology(str(p))
    
    assert manager.ontology is not None
    classes = [c.name for c in manager.get_classes()]
    assert "Animal" in classes
    assert "Cat" in classes

def test_hierarchy(tmp_path):
    d = tmp_path / "subdir"
    d.mkdir()
    p = d / "test.owl"
    p.write_text(SAMPLE_OWL, encoding='utf-8')
    
    manager = OntologyManager()
    manager.load_ontology(str(p))
    
    # Simple check if hierarchy extraction runs without error
    # and returns a dictionary structure
    hierarchy = manager.get_hierarchy()
    assert isinstance(hierarchy, dict)

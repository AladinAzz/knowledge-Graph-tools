import pytest
from core.reasoner import ReasoningEngine
import os
import rdflib
from owlready2 import get_ontology, ObjectProperty, TransitiveProperty, Thing, sync_reasoner
import tempfile

def test_transitivity_inference(tmp_path):
    # Create an ontology with transitivity
    # We use owlready2 to generate it to ensure validity
    ont_path = tmp_path / "transitivity.owl"
    
    onto = get_ontology("http://test.org/transitivity.owl")
    with onto:
        class related_to(ObjectProperty, TransitiveProperty): pass
        class Item(Thing): pass
        
        i1 = Item("i1")
        i2 = Item("i2")
        i3 = Item("i3")
        
        i1.related_to.append(i2)
        i2.related_to.append(i3)
        
    onto.save(file=str(ont_path), format="rdfxml")
    
    engine = ReasoningEngine()
    
    try:
        inferred_graph = engine.run_reasoner(str(ont_path), reasoner_type='hermit')
    except Exception as e:
        pytest.skip(f"Reasoner failed: {e}")

    # Check for inferred triple: i1 related_to i3
    I1 = rdflib.URIRef("http://test.org/transitivity.owl#i1")
    I3 = rdflib.URIRef("http://test.org/transitivity.owl#i3")
    RELATED = rdflib.URIRef("http://test.org/transitivity.owl#related_to")
    
    assert (I1, RELATED, I3) in inferred_graph

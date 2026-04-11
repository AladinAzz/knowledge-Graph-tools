"""
Debug Reasoner Script

This script is used to debug the reasoning engine.
It tests ontology loading, transitivity reasoning, and triple inference 
using both owlready2 directly and the application's ReasoningEngine.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.reasoner import ReasoningEngine
import rdflib

SAMPLE_OWL_REASONING = """<?xml version="1.0"?>
<rdf:RDF xmlns="http://example.org/reasoning.owl#"
     xml:base="http://example.org/reasoning.owl"
     xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
     xmlns:owl="http://www.w3.org/2002/07/owl#"
     xmlns:xml="http://www.w3.org/XML/1998/namespace"
     xmlns:xsd="http://www.w3.org/2001/XMLSchema#"
     xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">
    <owl:Ontology rdf:about="http://example.org/reasoning.owl"/>
    
    <owl:Class rdf:about="http://example.org/reasoning.owl#Animal"/>
    <owl:Class rdf:about="http://example.org/reasoning.owl#Dog">
        <rdfs:subClassOf rdf:resource="http://example.org/reasoning.owl#Animal"/>
    </owl:Class>
    
    <owl:NamedIndividual rdf:about="http://example.org/reasoning.owl#Rex">
        <rdf:type rdf:resource="http://example.org/reasoning.owl#Dog"/>
    </owl:NamedIndividual>
</rdf:RDF>
"""

with open("debug_reasoning.owl", "w", encoding="utf-8") as f:
    f.write(SAMPLE_OWL_REASONING)

# Test 3: Transitivity (In-memory)
print("\n--- Test 3: Transitivity (In-memory) ---")
from owlready2 import *
onto2 = get_ontology("http://test.org/onto2.owl")
with onto2:
    class related_to(ObjectProperty, TransitiveProperty): pass
    class Item(Thing): pass
    
    i1 = Item("i1")
    i2 = Item("i2")
    i3 = Item("i3")
    
# Test 4: Transitivity via Engine (File -> Reason -> Graph)
print("\n--- Test 4: Transitivity via Engine ---")
onto2.save(file="debug_transitivity.owl", format="rdfxml")

engine = ReasoningEngine()
try:
    inferred_graph = engine.run_reasoner(os.path.abspath("debug_transitivity.owl"), reasoner_type='hermit')
    print(f"Graph size: {len(inferred_graph)}")
    
    I1 = rdflib.URIRef("http://test.org/onto2.owl#i1")
    I3 = rdflib.URIRef("http://test.org/onto2.owl#i3")
    RELATED = rdflib.URIRef("http://test.org/onto2.owl#related_to")
    
    if (I1, RELATED, I3) in inferred_graph:
        print("SUCCESS: Inferred triple found in graph")
    else:
        print("FAILURE: Inferred triple NOT found in graph")
        # Debug prints
        print("Triples with i1 as subject:")
        for s, p, o in inferred_graph.triples((I1, None, None)):
            print(f"{s} {p} {o}")

except Exception as e:
    print(f"Error in Test 4: {e}")


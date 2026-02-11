
import pytest
from core.knowledge_extractor import KnowledgeExtractor
from rdflib import Graph, URIRef, Literal, Namespace

class TestKnowledgeExtractor:
    @pytest.fixture
    def extractor(self):
        return KnowledgeExtractor()

    def test_initialization(self, extractor):
        assert extractor.nlp is not None
        assert extractor.ns is not None

    def test_extract_triples_simple(self, extractor):
        text = "Albert Einstein was born in Ulm."
        graph = extractor.extract_triples(text)
        
        assert isinstance(graph, Graph)
        assert len(graph) > 0
        
        # Check for presence of expected entities (normalized)
        # s: albert_einstein, p: be (lemma of was), o: ulm
        
        ns = extractor.ns
        s = ns.albert_einstein
        o = ns.ulm
        
        # Predicate might be 'be' or similar depending on lemma
        # We can iterate to find it or check loosely
        triples = list(graph)
        assert len(triples) >= 1
        
        # Print triples for debugging if needed
        for s, p, o in triples:
            print(f"Triple: {s} {p} {o}")

    def test_extract_triples_no_entities(self, extractor):
        text = "Running fast."
        graph = extractor.extract_triples(text)
        # Should be empty or very few triples if no clear s-p-o structure
        # The logic requires nsubj, ROOT, and object
        # "Running fast" might have ROOT 'running' but no subject.
        assert len(graph) == 0

    def test_extract_multiple_sentences(self, extractor):
        text = "Paris is in France. London is in England."
        graph = extractor.extract_triples(text)
        
        # Should have at least 2 triples (one for each sentence)
        assert len(graph) >= 2

    def test_owl_compatibility(self, extractor):
        text = "Socrates is human."
        graph = extractor.extract_triples(text)
        
        # Check for OWL types
        from rdflib import RDF, OWL
        
        # Find the subject URI
        triples = list(graph.triples((None, RDF.type, OWL.NamedIndividual)))
        assert len(triples) >= 2 # s and o should both be individuals
        
        # Find the predicate URI
        prop_triples = list(graph.triples((None, RDF.type, OWL.ObjectProperty)))
        assert len(prop_triples) >= 1

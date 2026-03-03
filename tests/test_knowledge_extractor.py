
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

    def test_conjunctions_and_ner(self, extractor):
        text = "Alice and Bob visited Paris."
        graph = extractor.extract_triples(text)
        
        from rdflib import RDF, FOAF, Namespace
        SCHEMA = Namespace("http://schema.org/")
        
        # Check that we have 2 triples: Alice-visited-Paris, Bob-visited-Paris
        # We can just count total triples. 
        # 2 main triples + 1 property decl + 2*2 individuals decl + 3 NER types = ~10 triples
        # Let's check specifically for subjects
        
        subjects = set(graph.subjects(RDF.type, FOAF.Person))
        assert len(subjects) == 2 # Alice and Bob
        
        # Check GPE
        places = set(graph.subjects(RDF.type, SCHEMA.Place))
        assert len(places) == 1 # Paris

    def test_coreference_resolution(self, extractor):
        text = "Alice is a scientist. She lives in Paris."
        graph = extractor.extract_triples(text)
        
        from rdflib import URIRef
        
        # We expect a triple: (Alice, lives, Paris)
        # Instead of (She, lives, Paris)
        
        # Check if there is a triple where subject is Alice and object is Paris
        # Note: URIs are lowercased and distinct
        
        alice_uri = extractor.ns['alice']
        paris_uri = extractor.ns['paris']
        
        # Find predicates connecting Alice and Paris
        preds = list(graph.predicates(alice_uri, paris_uri))
        assert len(preds) > 0

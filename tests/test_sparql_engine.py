import pytest
from core.rdf_manager import RDFManager
from core.sparql_engine import SPARQLEngine
from rdflib import Graph

SAMPLE_TTL = """
@prefix ex: <http://example.org/> .
ex:Alice ex:knows ex:Bob .
ex:Bob ex:knows ex:Charlie .
ex:Alice ex:age 30 .
"""

@pytest.fixture
def engine():
    manager = RDFManager()
    manager.graph.parse(data=SAMPLE_TTL, format='turtle')
    return SPARQLEngine(manager)

def test_select_query(engine):
    query = "SELECT ?s ?o WHERE { ?s <http://example.org/knows> ?o }"
    results = engine.execute_query(query)
    formatted = engine.format_results(results)
    
    assert formatted['type'] == 'SELECT'
    assert len(formatted['bindings']) == 2
    
def test_ask_query(engine):
    query = "ASK { <http://example.org/Alice> <http://example.org/knows> <http://example.org/Bob> }"
    results = engine.execute_query(query)
    formatted = engine.format_results(results)
    
    assert formatted['type'] == 'ASK'
    assert formatted['boolean'] is True

def test_construct_query(engine):
    query = "CONSTRUCT { ?s <http://example.org/friend> ?o } WHERE { ?s <http://example.org/knows> ?o }"
    results = engine.execute_query(query)
    formatted = engine.format_results(results)
    
    assert formatted['type'] == 'CONSTRUCT' or formatted['type'] == 'DESCRIBE'
    assert isinstance(formatted['graph'], Graph)
    assert len(formatted['graph']) == 2

def test_invalid_query(engine):
    with pytest.raises(Exception):
        engine.execute_query("SELECT * WHERE { INVALID SYNTAX }")

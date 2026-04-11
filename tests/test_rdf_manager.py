"""
Unit Tests for RDFManager

This module contains unit tests for the RDFManager class, verifying 
graph loading, statistics extraction, and namespace management.
"""

import pytest
import os
from core.rdf_manager import RDFManager
from rdflib import Graph

# Sample Turtle data for testing
SAMPLE_TTL = """
@prefix ex: <http://example.org/> .
ex:Subject ex:Predicate ex:Object .
"""

def test_initialization():
    manager = RDFManager()
    assert isinstance(manager.graph, Graph)
    assert len(manager.graph) == 0

def test_load_file(tmp_path):
    # Create a temporary TTL file
    d = tmp_path / "subdir"
    d.mkdir()
    p = d / "test.ttl"
    p.write_text(SAMPLE_TTL, encoding='utf-8')
    
    manager = RDFManager()
    manager.load_file(str(p))
    
    assert len(manager.graph) == 1
    stats = manager.get_statistics()
    assert stats['num_triples'] == 1

def test_save_file(tmp_path):
    manager = RDFManager()
    manager.graph.parse(data=SAMPLE_TTL, format='turtle')
    
    p = tmp_path / "output.xml"
    manager.save_file(str(p), 'xml')
    
    assert p.exists()
    # verify content
    g2 = Graph()
    g2.parse(str(p), format='xml')
    assert len(g2) == 1

def test_load_nonexistent_file():
    manager = RDFManager()
    with pytest.raises(FileNotFoundError):
        manager.load_file("nonexistent.ttl")

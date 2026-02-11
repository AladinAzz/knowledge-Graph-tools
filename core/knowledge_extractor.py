"""
Knowledge Extractor Module

This module uses Natural Language Processing (spacy) to extract knowledge (triples)
from unstructured text. It identifies subjects, predicates, and objects and converts
them into an RDF graph.
"""

import spacy
from rdflib import Graph, URIRef, Literal, RDF, Namespace, OWL

class KnowledgeExtractor:
    """
    Extracts RDF triples from text using spacy.
    """
    def __init__(self, model="en_core_web_sm"):
        """
        Initializes the extractor with a spacy model.
        """
        try:
            self.nlp = spacy.load(model)
        except OSError:
            # Fallback or re-download if missing
            from spacy.cli import download
            download(model)
            self.nlp = spacy.load(model)
            
        self.ns = Namespace("http://example.org/kb/")

    def extract_triples(self, text):
        """
        Parses text and returns an RDF graph containing extracted triples.
        """
        doc = self.nlp(text)
        g = Graph()
        g.bind("kb", self.ns)
        g.bind("owl", OWL)
        
        for sent in doc.sents:
            # Enhanced extraction logic
            subj = None
            pred = None
            obj = None
            
            # Find ROOT verb first
            for token in sent:
                if token.dep_ == "ROOT":
                    pred = token
                    break
            
            if not pred:
                continue
                
            # Find subject and object related to this predicate
            for token in sent:
                if token.head == pred:
                    if token.dep_ in ("nsubj", "nsubjpass"):
                        subj = token
                    elif token.dep_ in ("dobj", "attr", "acomp"):
                        obj = token
                    elif token.dep_ == "prep":
                        # If obj is connected via preposition (e.g. born IN Ulm)
                        # We take the pobj of this prep
                        for child in token.children:
                            if child.dep_ == "pobj":
                                obj = child
                                break
            
            if subj and pred and obj:
                # Create labels with compounds
                s_label = self._get_compound(subj)
                o_label = self._get_compound(obj)
                p_label = pred.lemma_
                
                # URIs
                s_uri = self.ns[self._clean_text(s_label)]
                p_uri = self.ns[self._clean_text(p_label)]
                o_uri = self.ns[self._clean_text(o_label)]
                
                # Add main triple
                g.add((s_uri, p_uri, o_uri))
                
                # Add OWL Semantics for Reasoner Compatibility
                # 1. Declare properties as ObjectProperty
                g.add((p_uri, RDF.type, OWL.ObjectProperty))
                
                # 2. Declare individuals as NamedIndividual
                g.add((s_uri, RDF.type, OWL.NamedIndividual))
                g.add((o_uri, RDF.type, OWL.NamedIndividual))
                
        return g

    def _get_compound(self, token):
        """Recursively builds the full compound noun phrase."""
        # Check children for 'compound' dependency
        compounds = [child for child in token.children if child.dep_ == "compound"]
        # Sort by position in text (though usually compound comes before)
        compounds.append(token)
        compounds.sort(key=lambda x: x.i)
        
        return " ".join([t.text for t in compounds])
                


    def _clean_text(self, text):
        """Normalizes text for URI generation."""
        return text.lower().replace(" ", "_").strip()

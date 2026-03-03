"""
Knowledge Extractor Module

This module uses Natural Language Processing (spacy) to extract knowledge (triples)
from unstructured text. It identifies subjects, predicates, and objects and converts
them into an RDF graph.
"""

import spacy
from rdflib import Graph, URIRef, Literal, RDF, Namespace, OWL, FOAF

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
        self.schema = Namespace("http://schema.org/")

    def extract_triples(self, text):
        """
        Parses text and returns an RDF graph containing extracted triples.
        """
        doc = self.nlp(text)
        g = Graph()
        g.bind("kb", self.ns)
        g.bind("owl", OWL)
        g.bind("foaf", FOAF)
        g.bind("schema", self.schema)
        
        # Build Entity Map for quick lookup (token index -> entity label)
        entity_map = {}
        for ent in doc.ents:
            for token in ent:
                entity_map[token.i] = ent.label_
        
        last_subject_label = None

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
                # Expand conjunctions (Alice and Bob -> [Alice, Bob])
                subjects = [subj] + [child for child in subj.children if child.dep_ == "conj"]
                objects = [obj] + [child for child in obj.children if child.dep_ == "conj"]
                
                p_label = pred.lemma_
                p_uri = self.ns[self._clean_text(p_label)]
                
                # Add property declaration once
                g.add((p_uri, RDF.type, OWL.ObjectProperty))

                for s in subjects:
                    # Coreference Resolution
                    s_text = self._get_compound(s)
                    
                    # If pronoun, try to resolve
                    if s.pos_ == "PRON" and last_subject_label:
                        s_text = last_subject_label
                    
                    # Update last subject if it's a candidate (PROPN or Entity)
                    # Exclude GPE, LOC, DATE, TIME, CARDINAL from being 'actors' usually
                    ent_type = entity_map.get(s.i)
                    if s.pos_ == "PROPN" and ent_type not in ['GPE', 'LOC', 'DATE', 'TIME', 'CARDINAL', 'QUANTITY']:
                         last_subject_label = s_text
                        
                    for o in objects:
                        o_text = self._get_compound(o)
                        # Resolve object pronoun too? Rare for simple S-P-O but possible "Alice saw Bob. She called him."
                        if o.pos_ == "PRON" and last_subject_label: # This might be risky if we want obj coreference to obj. But simple approach: resolve to subject.
                             # Actually, 'him' referring to last subject? Ambiguous. 
                             # Task said "He/She -> Last Entity". Usually imply Subject.
                             # Let's simple resolve if it's he/she/it
                             if o.text.lower() in ["he", "she", "it", "they"]:
                                 o_text = last_subject_label

                        # Update last subject candidates from object? "I saw Alice." -> Next "She" is Alice.
                        # Yes, object can be antecedent.
                        ent_type_o = entity_map.get(o.i)
                        if o.pos_ == "PROPN" and ent_type_o not in ['GPE', 'LOC', 'DATE', 'TIME', 'CARDINAL', 'QUANTITY']:
                             last_subject_label = o_text

                        s_uri = self.ns[self._clean_text(s_text)]
                        o_uri = self.ns[self._clean_text(o_text)]
                        
                        # Add triple
                        g.add((s_uri, p_uri, o_uri))
                        
                        # Add OWL Semantics
                        g.add((s_uri, RDF.type, OWL.NamedIndividual))
                        g.add((o_uri, RDF.type, OWL.NamedIndividual))
                        
                        # Add NER Types
                        # Check subject type
                        if entity_map.get(s.i) == 'PERSON' or (s_text == last_subject_label and last_subject_label):
                             # If we resolved to a label that WAS a person, maybe we should track type? 
                             # Simplification: If resolved, assume Person if ambiguous.
                             # But sticking to explicit map is safer unless we track type history.
                             if entity_map.get(s.i) == 'PERSON': g.add((s_uri, RDF.type, FOAF.Person))
                             # Note: We lost type tracking if we just track string label. 
                             # Re-typing based on label match is hard without a registry.
                             # But wait, later logic handles explicit NER.
                             pass
                        
                        if entity_map.get(s.i) == 'PERSON': g.add((s_uri, RDF.type, FOAF.Person))
                        elif entity_map.get(s.i) == 'ORG': g.add((s_uri, RDF.type, FOAF.Organization))
                        elif entity_map.get(s.i) == 'GPE': g.add((s_uri, RDF.type, self.schema.Place))

                        # Check object type
                        if entity_map.get(o.i) == 'PERSON': g.add((o_uri, RDF.type, FOAF.Person))
                        elif entity_map.get(o.i) == 'ORG': g.add((o_uri, RDF.type, FOAF.Organization))
                        elif entity_map.get(o.i) == 'GPE': g.add((o_uri, RDF.type, self.schema.Place))
                
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

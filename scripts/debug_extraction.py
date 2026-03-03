import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import spacy
from core.knowledge_extractor import KnowledgeExtractor

def debug():
    text = "Alice is a scientist. She lives in Paris."
    
    with open("debug_output.txt", "w", encoding="utf-8") as f:
        f.write(f"--- Processing: '{text}' ---\n")
        
        # 1. Check raw Spacy NER
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)
        f.write("Entities found by Spacy:\n")
        for ent in doc.ents:
            f.write(f" - {ent.text} ({ent.label_})\n")
            
        f.write("\n--- Running KnowledgeExtractor ---\n")
        extractor = KnowledgeExtractor()
        graph = extractor.extract_triples(text)
        
        f.write(f"Extracted {len(graph)} triples:\n")
        for s, p, o in graph:
            f.write(f"({s}, {p}, {o})\n")
            
    print("Debug output written to debug_output.txt")

if __name__ == "__main__":
    debug()

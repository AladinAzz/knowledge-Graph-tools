"""
Gemini Extractor Module

This module uses Google's Gemini API to extract RDF triples from text.
It sends a prompt to the model and parses the response into an rdflib Graph.
"""

import google.generativeai as genai
from rdflib import Graph, URIRef, Literal, RDF, RDFS, OWL, Namespace
import io
import re

class GeminiExtractor:
    def __init__(self, api_key=None, model_name="gemini-pro"):
        self.api_key = api_key
        self.model_name = model_name
        self.ns = Namespace("http://example.org/kb/")
        
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model_name)
        else:
            self.model = None

    def set_api_key(self, api_key):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        # Re-initialize model to be safe? usually configure is global but good to be sure
        self.model = genai.GenerativeModel(self.model_name)

    def set_model(self, model_name):
        self.model_name = model_name
        if self.api_key:
             self.model = genai.GenerativeModel(model_name)

    def extract_triples(self, text):
        if not self.api_key or not self.model:
            raise ValueError("API Key not set. Please configure the Gemini API key.")

        prompt = f"""
        You are an expert Knowledge Graph engineer. Your task is to extract RDF triples from the following text.
        
        Rules:
        1. Output ONLY a valid list of RDF triples in Turtle (.ttl) format.
        2. Use the namespace prefix `kb:` for entities derived from the text (http://example.org/kb/).
        3. Use standard vocabularies like `rdf:`, `rdfs:`, `owl:`, `foaf:`, `schema:` where appropriate.
        4. Do not include any markdown formatting (like ```turtle ... ```), just the raw Turtle code.
        5. If the text implies a class hierarchy or specific types, include `rdf:type` triples.
        6. Normalized entity names (CamelCase for Classes, snake_case for properties/individuals if possible, or just consistent URI friendly format).
        
        Text:
        "{text}"
        
        Turtle Output:
        """
        
        try:
            response = self.model.generate_content(prompt)
            turtle_code = response.text
            
            # Clean up potential markdown formatting code blocks if the model ignores the rule
            turtle_code = re.sub(r'```turtle', '', turtle_code)
            turtle_code = re.sub(r'```', '', turtle_code)
            turtle_code = turtle_code.strip()
            
            # Wrap in prefixes if missing (rdflib can handle some but good to match)
            # Actually, let's just let rdflib parse it.
            
            g = Graph()
            # Bind common prefixes
            g.bind("kb", self.ns)
            g.bind("owl", OWL)
            g.bind("foaf", Namespace("http://xmlns.com/foaf/0.1/"))
            g.bind("schema", Namespace("http://schema.org/"))
            
            # We might need to prepend prefixes if the model didn't output them
            # But usually models are good at full valid ttl if asked.
            # Let's verify by try-parse
            
            g.parse(data=turtle_code, format="turtle")
            
            return g
            
        except Exception as e:
            raise Exception(f"Gemini Extraction Failed: {e}")

    def list_models(self):
        """
        Lists available models that support content generation.
        Returns a list of model names (e.g., 'models/gemini-pro').
        """
        if not self.api_key:
             raise ValueError("API Key not set.")
             
        try:
            # genai.configure must be called before this if not already
            # It is called in set_api_key
            models = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    # Clean up name: 'models/gemini-pro' -> 'gemini-pro' if preferred, 
                    # but usually the full name is needed for instantiation, 
                    # except the SDK handles both. passing 'gemini-pro' works.
                    # Let's keep the name as returned or strip 'models/' for display?
                    # The user manual edit used "gemini-1.5-pro".
                    # list_models returns 'models/gemini-1.5-pro'. 
                    # simple replacement for display.
                    name = m.name
                    if name.startswith("models/"):
                        name = name.replace("models/", "")
                    models.append(name)
            return sorted(models)
        except Exception as e:
            raise Exception(f"Failed to list models: {e}")
            

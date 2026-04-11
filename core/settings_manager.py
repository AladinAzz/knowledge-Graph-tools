
import xml.etree.ElementTree as ET
import os
from dotenv import load_dotenv

class SettingsManager:
    """
    Manages application settings and history storage.
    - API Key: loaded from .env file (GEMINI_API_KEY)
    - Other settings: stored in settings.xml
    """
    def __init__(self, settings_file="settings.xml"):
        self.settings_file = settings_file
        self.data = {
            "api_key": "",
            "gemini_model": "gemini-2.0-flash",
            "dark_theme": False,
            "reasoning_enabled": False,
            "reasoning_profile": "hermit",
            "query_history": []
        }
        # Load API key from .env
        load_dotenv()
        env_key = os.getenv("GEMINI_API_KEY", "")
        if env_key:
            self.data["api_key"] = env_key
        
        self.load_settings()

    def load_settings(self):
        """Loads settings from the XML file."""
        if not os.path.exists(self.settings_file):
            return

        try:
            tree = ET.parse(self.settings_file)
            root = tree.getroot()
            
            # API Key fallback from XML (legacy support)
            if not self.data["api_key"]:
                api_key_elem = root.find("Gemini/ApiKey")
                if api_key_elem is not None and api_key_elem.text:
                    self.data["api_key"] = api_key_elem.text
                
            # Model
            model_elem = root.find("Gemini/Model")
            if model_elem is not None:
                self.data["gemini_model"] = model_elem.text or "gemini-2.0-flash"
                
            # Theme
            theme_elem = root.find("Appearance/DarkTheme")
            if theme_elem is not None:
                self.data["dark_theme"] = (theme_elem.text == "True")
            
            # Reasoning
            reasoning_enabled_elem = root.find("Reasoning/Enabled")
            if reasoning_enabled_elem is not None:
                self.data["reasoning_enabled"] = (reasoning_enabled_elem.text == "True")
                
            reasoning_profile_elem = root.find("Reasoning/Profile")
            if reasoning_profile_elem is not None:
                self.data["reasoning_profile"] = reasoning_profile_elem.text or "hermit"
                
            # History
            history_elem = root.find("History/SPARQL")
            if history_elem is not None:
                self.data["query_history"] = [
                    query.text for query in history_elem.findall("Query") if query.text
                ]
                
        except Exception as e:
            print(f"Error loading settings: {e}")

    def save_settings(self):
        """Saves current settings to the XML file. API key is saved to .env instead."""
        root = ET.Element("Settings")
        
        # Gemini Section (no API key — that's in .env)
        gemini_sec = ET.SubElement(root, "Gemini")
        ET.SubElement(gemini_sec, "Model").text = self.data["gemini_model"]
        
        # Appearance Section
        app_sec = ET.SubElement(root, "Appearance")
        ET.SubElement(app_sec, "DarkTheme").text = str(self.data["dark_theme"])
        
        # Reasoning Section
        reasoning_sec = ET.SubElement(root, "Reasoning")
        ET.SubElement(reasoning_sec, "Enabled").text = str(self.data["reasoning_enabled"])
        ET.SubElement(reasoning_sec, "Profile").text = self.data["reasoning_profile"]
        
        # History Section
        hist_sec = ET.SubElement(root, "History")
        sparql_sec = ET.SubElement(hist_sec, "SPARQL")
        for q_text in self.data["query_history"]:
            ET.SubElement(sparql_sec, "Query").text = q_text
            
        tree = ET.ElementTree(root)
        try:
            # Indent for readability (Python 3.9+)
            if hasattr(ET, "indent"):
                 ET.indent(tree, space="  ", level=0)
            tree.write(self.settings_file, encoding="utf-8", xml_declaration=True)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def save_api_key_to_env(self, key):
        """Saves the API key to the .env file."""
        env_path = os.path.join(os.path.dirname(os.path.abspath(self.settings_file)), ".env")
        lines = []
        key_found = False
        
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("GEMINI_API_KEY"):
                        lines.append(f"GEMINI_API_KEY={key}\n")
                        key_found = True
                    else:
                        lines.append(line)
        
        if not key_found:
            lines.append(f"GEMINI_API_KEY={key}\n")
        
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        
        self.data["api_key"] = key

    # Getters/Setters
    def get_api_key(self): return self.data["api_key"]
    def set_api_key(self, key): 
        self.data["api_key"] = key
        self.save_api_key_to_env(key)
    
    def get_model(self): return self.data["gemini_model"]
    def set_model(self, model): self.data["gemini_model"] = model
    
    def get_dark_theme(self): return self.data["dark_theme"]
    def set_dark_theme(self, enabled): self.data["dark_theme"] = enabled
    
    def get_reasoning_enabled(self): return self.data["reasoning_enabled"]
    def set_reasoning_enabled(self, enabled): self.data["reasoning_enabled"] = enabled
    
    def get_reasoning_profile(self): return self.data["reasoning_profile"]
    def set_reasoning_profile(self, profile): self.data["reasoning_profile"] = profile
    
    def get_query_history(self): return self.data["query_history"]
    def add_to_history(self, query):
        if query and query not in self.data["query_history"]:
            self.data["query_history"].insert(0, query)
            # Limit history size
            if len(self.data["query_history"]) > 50:
                self.data["query_history"].pop()

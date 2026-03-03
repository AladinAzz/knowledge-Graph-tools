
import xml.etree.ElementTree as ET
import os

class SettingsManager:
    """
    Manages application settings and history storage in an XML file.
    Stores:
    - Gemini API Key
    - Selected Gemini Model
    - Theme Preference (Dark/Light)
    - SPARQL Query History
    """
    def __init__(self, settings_file="settings.xml"):
        self.settings_file = settings_file
        self.data = {
            "api_key": "",
            "gemini_model": "gemini-2.0-flash",
            "dark_theme": False,
            "query_history": []
        }
        self.load_settings()

    def load_settings(self):
        """Loads settings from the XML file."""
        if not os.path.exists(self.settings_file):
            return

        try:
            tree = ET.parse(self.settings_file)
            root = tree.getroot()
            
            # API Key
            api_key_elem = root.find("Gemini/ApiKey")
            if api_key_elem is not None:
                self.data["api_key"] = api_key_elem.text or ""
                
            # Model
            model_elem = root.find("Gemini/Model")
            if model_elem is not None:
                self.data["gemini_model"] = model_elem.text or "gemini-2.0-flash"
                
            # Theme
            theme_elem = root.find("Appearance/DarkTheme")
            if theme_elem is not None:
                self.data["dark_theme"] = (theme_elem.text == "True")
                
            # History
            history_elem = root.find("History/SPARQL")
            if history_elem is not None:
                self.data["query_history"] = [
                    query.text for query in history_elem.findall("Query") if query.text
                ]
                
        except Exception as e:
            print(f"Error loading settings: {e}")

    def save_settings(self):
        """Saves current settings to the XML file."""
        root = ET.Element("Settings")
        
        # Gemini Section
        gemini_sec = ET.SubElement(root, "Gemini")
        ET.SubElement(gemini_sec, "ApiKey").text = self.data["api_key"]
        ET.SubElement(gemini_sec, "Model").text = self.data["gemini_model"]
        
        # Appearance Section
        app_sec = ET.SubElement(root, "Appearance")
        ET.SubElement(app_sec, "DarkTheme").text = str(self.data["dark_theme"])
        
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

    # Getters/Setters
    def get_api_key(self): return self.data["api_key"]
    def set_api_key(self, key): self.data["api_key"] = key
    
    def get_model(self): return self.data["gemini_model"]
    def set_model(self, model): self.data["gemini_model"] = model
    
    def get_dark_theme(self): return self.data["dark_theme"]
    def set_dark_theme(self, enabled): self.data["dark_theme"] = enabled
    
    def get_query_history(self): return self.data["query_history"]
    def add_to_history(self, query):
        if query and query not in self.data["query_history"]:
            self.data["query_history"].insert(0, query)
            # Limit history size?
            if len(self.data["query_history"]) > 50:
                self.data["query_history"].pop()

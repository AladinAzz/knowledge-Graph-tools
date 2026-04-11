
import sys
import os
"""
UI Tests for Gemini Extractor

This module contains integration tests for the GeminiExtractor UI components, 
verifying API key handling, model selection, and extraction workflows.
"""

import pytest
from unittest.mock import MagicMock, patch

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt6.QtWidgets import QApplication

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app

# Mock heavy modules
sys.modules["google"] = MagicMock()
sys.modules["google.generativeai"] = MagicMock()
sys.modules["spacy"] = MagicMock()
sys.modules["pyvis"] = MagicMock()
sys.modules["pyvis.network"] = MagicMock()
sys.modules["PyQt6.QtWebEngineWidgets"] = MagicMock()

def test_gemini_ui_layout(qapp):
    from gui.widgets.text_kg_widget import TextKGWidget
    
    # Mock dependencies
    rdf_manager = MagicMock()
    
    # Mock dependencies
    rdf_manager = MagicMock()
    
    with patch("core.gemini_extractor.genai") as mock_genai, \
         patch("gui.widgets.text_kg_widget.GraphViewer") as MockViewerCls, \
         patch("gui.widgets.text_kg_widget.QTabWidget"), \
         patch("gui.widgets.text_kg_widget.QVBoxLayout"), \
         patch("gui.widgets.text_kg_widget.QHBoxLayout"):
         
        widget = TextKGWidget(rdf_manager)
        
        # Verify UI Elements
        assert widget.api_key_input is not None
        assert widget.model_selector is not None
        assert widget.generate_btn.text() == "Generate RDF (Gemini)"
        
        # Verify Model Options
        assert widget.model_selector.count() >= 3
        assert "gemini-2.0-flash" in [widget.model_selector.itemText(i) for i in range(widget.model_selector.count())]

def test_gemini_interaction(qapp):
    from gui.widgets.text_kg_widget import TextKGWidget
    
    rdf_manager = MagicMock()
    
    # Patch the extractor inside the widget or the class usage
    # Since TextKGWidget instantiates GeminiExtractor inside __init__, we need to patch the class
    
    with patch("gui.widgets.text_kg_widget.GeminiExtractor") as MockExtractorCls, \
         patch("gui.widgets.text_kg_widget.GraphViewer"), \
         patch("gui.widgets.text_kg_widget.QTabWidget"), \
         patch("gui.widgets.text_kg_widget.QVBoxLayout"), \
         patch("gui.widgets.text_kg_widget.QHBoxLayout"):
         
        mock_extractor_instance = MockExtractorCls.return_value
        mock_extractor_instance.extract_triples.return_value = [("s", "p", "o")]
        
        widget = TextKGWidget(rdf_manager)
        
        # Test 1: Empty Text -> Warning
        widget.text_input.setPlainText("")
        with patch("PyQt6.QtWidgets.QMessageBox.warning") as mock_warn:
            widget.generate_graph()
            mock_warn.assert_called()
            
        # Test 2: Empty Key -> Warning
        widget.text_input.setPlainText("Some text")
        widget.api_key_input.setText("")
        # The widget reads text().strip()
        
        with patch("PyQt6.QtWidgets.QMessageBox.warning") as mock_warn:
            widget.generate_graph()
            # Expect warning about API key
            args = mock_warn.call_args[0]
            assert "API Key" in args[2]

        # Test 3: Valid Input -> Call Extractor
        widget.api_key_input.setText("fake_key")
        widget.model_selector.setCurrentIndex(0) # gemini-2.0-flash
        
        # Mock successful extraction
        mock_extractor_instance.extract_triples.reset_mock()
        mock_extractor_instance.extract_triples.return_value = [("sub", "pred", "obj")]
        
        with patch("PyQt6.QtWidgets.QMessageBox.information") as mock_info:
            widget.generate_graph()
            
        # Verify calls
        mock_extractor_instance.set_api_key.assert_called_with("fake_key")
        mock_extractor_instance.set_model.assert_called()
        mock_extractor_instance.extract_triples.assert_called_with("Some text")
        
        # Verify UI state update
        assert widget.add_to_main_btn.isEnabled()
        
        # Test 4: Fetch Models
        mock_extractor_instance.list_models.return_value = ["model-a", "model-b"]
        
        with patch("PyQt6.QtWidgets.QMessageBox.information") as mock_info:
            widget.fetch_models()
            
        assert widget.model_selector.count() == 2
        assert widget.model_selector.itemText(0) == "model-a"
        
        print("SUCCESS: Gemini UI Interaction Verified")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    test_gemini_ui_layout(app)
    test_gemini_interaction(app)

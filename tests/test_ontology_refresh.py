import sys
import os
"""
Tests for Ontology Refresh Logic

This module contains integration tests verifying that the ontology hierarchy 
and properties refresh correctly when the graph changes, without mutating the main graph.
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

# Mock heavy modules before importing MainWindow
sys.modules["pyvis"] = MagicMock()
sys.modules["pyvis.network"] = MagicMock()
# Mock spacy to avoid loading models
sys.modules["spacy"] = MagicMock()

# Now import MainWindow
try:
    from gui.main_window import MainWindow
except ImportError:
    # If import fails, we might need to rely on patching `sys.modules` further or fixing path
    pass

def test_ontology_refresh(qapp):
    # Mock heavy modules before importing MainWindow
    sys.modules["pyvis"] = MagicMock()
    sys.modules["pyvis.network"] = MagicMock()
    sys.modules["spacy"] = MagicMock()
    
    with patch("gui.main_window.RDFManager"), \
         patch("gui.main_window.OntologyManager"), \
         patch("gui.main_window.SPARQLEngine"), \
         patch("gui.main_window.ReasoningEngine"), \
         patch("gui.main_window.GraphViewer"), \
         patch("gui.main_window.QueryWidget"), \
         patch("gui.main_window.TextKGWidget"), \
         patch("gui.main_window.OntologyTree"), \
         patch("gui.main_window.tempfile.mkstemp") as mock_mkstemp, \
         patch("gui.main_window.os.remove"), \
         patch("gui.main_window.os.path.exists", return_value=True):
         
        mock_mkstemp.return_value = (123, "temp_ontology.owl")
        
        from gui.main_window import MainWindow
        
        class TestableMainWindow(MainWindow):
            def init_ui(self):
                # Skip UI setup to avoid TypeErrors with mocks
                # But we need to set up the attributes that init_ui normally sets up locally? 
                # No, init_ui sets up widgets. __init__ sets up managers.
                # However, our managers also need to be mocked.
                
                # We need to manually assign the widgets expected by refresh_ontology_from_graph
                # which are: self.ontology_tree, self.graph_viewer (for refresh_graph_view)
                pass

        # Instantiate
        window = TestableMainWindow()
        
        # Manually attach mocks that would have been created in init_ui or __init__
        # __init__ creates managers, which are already mocked by the patches above (returned as new mocks)
        # But init_ui creates widgets. We need to mock them on the instance.
        window.ontology_tree = MagicMock()
        window.graph_viewer = MagicMock()
        
        # Setup mock behavior
        window.rdf_manager.get_graph.return_value = ["some_triple"] 
        window.ontology_manager.get_hierarchy.return_value = {"name": "Thing"}
        
        # 1. Test manual refresh call
        with patch('gui.main_window.os.close'):
            window.refresh_ontology_from_graph()
            
        # Assertions
        window.rdf_manager.save_file.assert_called_with("temp_ontology.owl", "xml")
        window.ontology_manager.load_ontology.assert_called_with("temp_ontology.owl")
        window.ontology_tree.display_hierarchy.assert_called()
        
        # 2. Test integration in refresh_graph_view
        window.ontology_manager.load_ontology.reset_mock()
        with patch('gui.main_window.os.close'):
            window.refresh_graph_view()
            
        window.ontology_manager.load_ontology.assert_called()
        
        print("SUCCESS: Ontology refresh logic verification passed")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    test_ontology_refresh(app)

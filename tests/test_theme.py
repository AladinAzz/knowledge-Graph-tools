
import sys
import os
"""
UI Tests for Application Theming

This module contains tests for the dark theme toggle and settings persistence 
related to visual appearance.
"""

import pytest
from PyQt6.QtWidgets import QApplication

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock heavy modules
from unittest.mock import MagicMock
sys.modules["google"] = MagicMock()
sys.modules["google.generativeai"] = MagicMock()
sys.modules["spacy"] = MagicMock()
sys.modules["pyvis"] = MagicMock()
sys.modules["pyvis.network"] = MagicMock()
sys.modules["PyQt6.QtWebEngineWidgets"] = MagicMock()

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app

def test_theme_toggle(qapp):
    # Patch internals of MainWindow to avoid full load
    from unittest.mock import patch
    
    with patch("gui.main_window.GraphViewer"), \
         patch("gui.main_window.QueryWidget"), \
         patch("gui.main_window.TextKGWidget"), \
         patch("gui.main_window.OntologyTree"), \
         patch("gui.main_window.QDockWidget"), \
         patch("gui.main_window.RDFManager"), \
         patch("gui.main_window.OntologyManager"), \
         patch("gui.main_window.SPARQLEngine"), \
         patch("gui.main_window.ReasoningEngine"), \
         patch("gui.main_window.QTabWidget"): # Bypass addTab type check
         
        from gui.main_window import MainWindow
        
        # Patch setCentralWidget on the class or instance to avoid type check
        with patch.object(MainWindow, 'setCentralWidget'), \
             patch.object(MainWindow, 'addDockWidget'):
            window = MainWindow()
        
        # Test Default (Light)
        assert window.dark_theme_action.isChecked() == False
        # assert qapp.styleSheet() == "" # Might have some defaults, but let's check it's not the dark one yet
        
        # Toggle Dark
        window.dark_theme_action.setChecked(True)
        window.toggle_theme()
        
        # Verify Stylesheet Loaded
        # The stylesheet content is large, checking for a known string
        assert "background-color: #2b2b2b" in qapp.styleSheet()
        
        # Toggle Back (Light)
        window.dark_theme_action.setChecked(False)
        window.toggle_theme()
        
        assert qapp.styleSheet() == ""
        
        print("SUCCESS: Theme Toggle Verified")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    test_theme_toggle(app)

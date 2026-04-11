
import sys
import os
"""
Unit Tests for SettingsManager Persistence

This module contains unit tests for the SettingsManager, verifying 
that settings and query history are correctly saved to and loaded from XML.
"""

import pytest
from unittest.mock import MagicMock, patch
import xml.etree.ElementTree as ET

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

SETTINGS_FILE = "test_settings.xml"

def cleanup():
    if os.path.exists(SETTINGS_FILE):
        os.remove(SETTINGS_FILE)

def test_settings_manager_persistence():
    cleanup()
    
    from core.settings_manager import SettingsManager
    
    # 1. Create and Save
    manager = SettingsManager(SETTINGS_FILE)
    manager.set_api_key("test-key-123")
    manager.set_model("gemini-pro")
    manager.set_dark_theme(True)
    manager.add_to_history("SELECT * WHERE { ?s ?p ?o }")
    manager.save_settings()
    
    assert os.path.exists(SETTINGS_FILE)
    
    # 2. Load New Instance
    new_manager = SettingsManager(SETTINGS_FILE)
    
    assert new_manager.get_api_key() == "test-key-123"
    assert new_manager.get_model() == "gemini-pro"
    assert new_manager.get_dark_theme() == True
    assert len(new_manager.get_query_history()) == 1
    assert new_manager.get_query_history()[0] == "SELECT * WHERE { ?s ?p ?o }"
    
    print("SUCCESS: Settings Persistence Verified")
    cleanup()

if __name__ == "__main__":
    test_settings_manager_persistence()

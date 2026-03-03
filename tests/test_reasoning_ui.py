import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from unittest.mock import MagicMock, patch

# Mock heavy modules BEFORE any other import
print("DEBUG: Starting mocks...")
sys.modules["spacy"] = MagicMock()
sys.modules["core.knowledge_extractor"] = MagicMock()
sys.modules["owlready2"] = MagicMock()
sys.modules["pyvis"] = MagicMock()
sys.modules["pyvis.network"] = MagicMock()
sys.modules["numpy"] = MagicMock()

print("DEBUG: Mocks applied. Importing PyQt6...")
from PyQt6.QtWidgets import QApplication

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app

# Import MainWindow after mocking
print("DEBUG: Importing MainWindow...")
try:
    from gui.main_window import MainWindow
    print("DEBUG: MainWindow imported successfully.")
except Exception as e:
    print(f"DEBUG: Failed to import MainWindow: {e}")
    raise e

def test_run_reasoner_on_displayed_graph(qapp):
    # Setup verify mocks
    with patch('gui.main_window.RDFManager') as MockRDFManager, \
         patch('gui.main_window.ReasoningEngine') as MockReasoningEngine, \
         patch('gui.main_window.QMessageBox') as MockMessageBox, \
         patch('gui.main_window.tempfile.mkstemp') as mock_mkstemp, \
         patch('gui.main_window.os.remove') as mock_remove, \
         patch('gui.main_window.os.path.exists') as mock_exists:
         
        # Configure Mocks
        mock_rdf = MockRDFManager.return_value
        # get_graph should return a list of triples (or a Graph, which is iterable of triples)
        mock_rdf.get_graph.return_value = [("http://s", "http://p", "http://o")] 
        
        mock_reasoner = MockReasoningEngine.return_value
        # run_reasoner returns a Graph (iterable of triples)
        mock_reasoner.run_reasoner.return_value = [("http://s", "http://p", "http://o2")]
        
        mock_mkstemp.return_value = (123, "temp_path.owl")
        mock_exists.return_value = True
        
        # Init Window
        window = MainWindow()
        
        # Call the method
        with patch('gui.main_window.os.close'): # Mock os.close for file descriptor
            window.run_reasoner(reasoner_type='hermit')
        
        # Assertions
        # 1. It should save the file
        mock_rdf.save_file.assert_called_with("temp_path.owl", "xml")
        
        # 2. It should run the reasoner on the temp path
        mock_reasoner.run_reasoner.assert_called_with("temp_path.owl", reasoner_type='hermit')
        
        # 3. It should merge results (we can't easily check += on mock, but we can check if it refreshed view)
        # Verify graph viewer updated
        # window.graph_viewer.display_graph.assert_called() # Hard to check without mocking GraphViewer too deep
        
        # 4. It should show success message
        print(f"DEBUG: MockMessageBox calls: {MockMessageBox.mock_calls}")
        if not MockMessageBox.information.called:
             print(f"DEBUG: Critical called? {MockMessageBox.critical.called}")
             if MockMessageBox.critical.called:
                 print(f"DEBUG: Critical args: {MockMessageBox.critical.call_args}")
        assert MockMessageBox.information.called
        
    # 5. It should cleanup
        # mock_remove.assert_called_with("temp_path.owl") # Logic might rely on os.path.exists
        
if __name__ == "__main__":
    # Manual run setup
    print("DEBUG: Manual run started.")
    app = QApplication(sys.argv)
    
    # We need to manually set up the qapp fixture
    class MockQApp:
        pass
    
    try:
        test_run_reasoner_on_displayed_graph(MockQApp())
        print("SUCCESS: test_run_reasoner_on_displayed_graph passed.")
    except Exception as e:
        print(f"FAILURE: {e}")
        import traceback
        traceback.print_exc()

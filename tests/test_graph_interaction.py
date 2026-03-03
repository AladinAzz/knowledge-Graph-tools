import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from unittest.mock import MagicMock, patch, mock_open

# Mock heavy modules if likely to cause issues
# sys.modules["pyvis"] = MagicMock() 
# We don't mock pyvis globally because we want to patch it specifically in the measure module
# But GraphViewer imports Network at top level. mocking it in sys.modules is safer.
sys.modules["pyvis"] = MagicMock()
sys.modules["pyvis.network"] = MagicMock()

from PyQt6.QtWidgets import QApplication

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app

# Import module to ensure it's loaded before patching
try:
    import gui.widgets.graph_viewer
except ImportError:
    pass # Will be handled in test or fail later

def test_html_injection(qapp):
    # We need to patch the Network class imported in graph_viewer
    # Since we mocked sys.modules["pyvis.network"], the import "from pyvis.network import Network"
    # in graph_viewer will get the mock.
    
    # We also need to patch builtins.open to verify file write content
    
    # Import GraphViewer
    # Use patch context to handle open and other things
    with patch("builtins.open", mock_open()) as mocked_file, \
         patch("gui.widgets.graph_viewer.tempfile.mkstemp") as mock_mkstemp, \
         patch("gui.widgets.graph_viewer.os.close"), \
         patch("gui.widgets.graph_viewer.QWebEngineView"), \
         patch("gui.widgets.graph_viewer.GraphWebPage") as MockPage, \
         patch("gui.widgets.graph_viewer.QUrl"), \
         patch("gui.widgets.graph_viewer.QVBoxLayout"), \
         patch("gui.widgets.graph_viewer.QHBoxLayout"), \
         patch("gui.widgets.graph_viewer.QLabel"), \
         patch("gui.widgets.graph_viewer.QComboBox"):
         
        mock_mkstemp.return_value = (123, "test.html")
        
        # Setup the Network mock behavior
        # We need to access the mock that graph_viewer uses.
        # It imports Network from pyvis.network.
        try:
             from gui.widgets.graph_viewer import GraphViewer
             from pyvis.network import Network
        except ImportError as e:
             pytest.fail(f"Failed to import GraphViewer: {e}")
        
        instance = Network.return_value
        instance.generate_html.return_value = "<html><body><script>var network = new vis.Network();</script></body></html>"
        
        viewer = GraphViewer()
        viewer.display_graph([])
        
        # Verify write
        handle = mocked_file()
        # write might be called multiple times? No, just once.
        handle.write.assert_called()
        written_content = handle.write.call_args[0][0]
        
        print("\nDEBUG: Written Content Start")
        print(written_content[:200])
        print("DEBUG: Written Content End")
        
        # Verify content has new JS logic for select/deselect/doubleClick
        html_content = handle.write.call_args[0][0]
        
        # Debug print
        print("DEBUG: HTML Content HEAD")
        print(html_content[:500])
        print("DEBUG: HTML Content TAIL")
        print(html_content[-1500:])
        
        assert "selectNode" in html_content
        assert "doubleClick" in html_content
        assert "cmd://select/" in html_content
        
        # Verify WebPage handling of cmd://
        page = viewer.web_page
        
        # Test select
        url = MagicMock()
        url.scheme.return_value = "cmd"
        url.toString.return_value = "cmd://select/http://example.org/Data"
        page.acceptNavigationRequest(url, 0, True)
        assert viewer.selected_node_id == "http://example.org/Data"
        assert viewer.remove_btn.isEnabled()
        
        # Test deselect
        url.toString.return_value = "cmd://deselect"
        page.acceptNavigationRequest(url, 0, True)
        assert viewer.selected_node_id is None
        assert not viewer.remove_btn.isEnabled()
        
        # Test remove logic
        # Setup graph mock for remove
        graph_mock = MagicMock()
        viewer.current_graph = graph_mock
        viewer.selected_node_id = "http://bad/node"
        
        viewer.remove_selected_node()
        
        # verify remove called twice (s, p, o) and (o, p, s) - wait, logic is (node, None, None) and (None, None, node)
        assert graph_mock.remove.call_count == 2


if __name__ == "__main__":
    # Manual run
    print("DEBUG: Manual run started")
    app = QApplication(sys.argv)
    try:
        test_html_injection(app)
        print("SUCCESS: test_html_injection passed")
    except Exception as e:
        print(f"FAILURE: {e}")
        import traceback
        traceback.print_exc()


import sys
import os
import pytest
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QApplication

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app

def test_namespace_dialog(qapp):
    from gui.widgets.namespace_dialog import NamespaceDialog
    
    # Mock RDFManager
    mock_rdf = MagicMock()
    mock_rdf.get_namespaces.return_value = [("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#"), ("ex", "http://example.org/")]
    
    # Initialize Dialog
    dialog = NamespaceDialog(mock_rdf)
    
    # Test Loading
    assert dialog.table.rowCount() == 2
    assert dialog.table.item(0, 0).text() == "ex" # Sorted alphabetically
    
    # Test Adding Namespace
    dialog.prefix_input.setText("foaf")
    dialog.uri_input.setText("http://xmlns.com/foaf/0.1/")
    
    with patch("PyQt6.QtWidgets.QMessageBox.information") as mock_info:
        dialog.add_namespace()
        
        # Verify call to RDFManager
        # Since we import URIRef inside the method, we check call args
        args = mock_rdf.bind_namespace.call_args[0]
        assert args[0] == "foaf"
        assert str(args[1]) == "http://xmlns.com/foaf/0.1/"
        
        # Verify reload (mock_rdf.get_namespaces called again)
        assert mock_rdf.get_namespaces.call_count > 1
        
    # Test Removing Namespace
    # Select first row
    dialog.table.selectRow(0)
    
    with patch("PyQt6.QtWidgets.QMessageBox.warning") as mock_warn:
        dialog.remove_namespace()
        mock_rdf.remove_namespace.assert_called_with("ex")

    print("SUCCESS: Namespace Dialog Verified")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    test_namespace_dialog(app)

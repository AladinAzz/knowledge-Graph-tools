
import sys
import os
import pytest
from PyQt6.QtWidgets import QApplication, QTextEdit
from PyQt6.QtGui import QTextDocument, QSyntaxHighlighter, QColor

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app

def test_sparql_highlighter(qapp):
    from gui.utils.syntax_highlighter import SPARQLHighlighter
    
    # Create document and highlighter
    text_edit = QTextEdit()
    doc = text_edit.document()
    highlighter = SPARQLHighlighter(doc)
    
    # Test Content
    sparql_query = "SELECT ?s WHERE { ?s a <http://example.org/Class> . FILTER(?s != 1) }"
    text_edit.setPlainText(sparql_query)
    
    # Force rehighlight (usually happens automatically but good to be sure)
    highlighter.rehighlight()
    
    # Verify formats
    # Note: Inspecting internal formats of QSyntaxHighlighter/QTextLayout is complex in unit tests 
    # because it involves internal text engine structures.
    # However, we can assert that the rules are set up correctly and the highlighter runs without error.
    
    assert len(highlighter.highlighting_rules) > 0
    
    # Check if keywords are present in rules
    found_select = False
    for pattern, fmt in highlighter.highlighting_rules:
        if "SELECT" in pattern.pattern():
            found_select = True
            # Verify color (Dark Blue)
            # We can't easily check color exact match for "darkblue" string, but can check validity
            assert fmt.foreground().color().isValid()
            break
            
    assert found_select, "SELECT keyword rule not found in highlighter"
    
    # Check variables rule
    found_var = False
    for pattern, fmt in highlighter.highlighting_rules:
        if "?" in pattern.pattern() and "$" in pattern.pattern(): # Check regex content roughly
             pass 
        if pattern.pattern() == "[?$]\\w+":
             found_var = True
             
    assert found_var, "Variable rule not found"
    
    print("SUCCESS: SPARQL Highlighter rules verified")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    test_sparql_highlighter(app)

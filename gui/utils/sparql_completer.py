"""
SPARQL Auto-Completer Module

Provides auto-completion for SPARQL queries in the query editor.
Supports SPARQL keywords, built-in functions, and dynamic prefix/variable suggestions.
"""

from PyQt6.QtWidgets import QCompleter, QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt, QStringListModel, QRect
from PyQt6.QtGui import QTextCursor
import re


# All SPARQL 1.1 keywords
SPARQL_KEYWORDS = [
    "SELECT", "DISTINCT", "REDUCED", "WHERE", "FROM", "NAMED",
    "FILTER", "OPTIONAL", "UNION", "GRAPH", "MINUS",
    "EXISTS", "NOT EXISTS", "BIND", "AS", "VALUES",
    "CONSTRUCT", "DESCRIBE", "ASK",
    "ORDER BY", "ASC", "DESC", "LIMIT", "OFFSET",
    "GROUP BY", "HAVING",
    "PREFIX", "BASE",
    "INSERT DATA", "DELETE DATA", "INSERT", "DELETE",
    "LOAD", "CLEAR", "DROP", "CREATE", "COPY", "MOVE", "ADD",
    "SERVICE", "SILENT", "INTO", "USING", "WITH",
    "a"  # shorthand for rdf:type
]

# SPARQL built-in functions
SPARQL_FUNCTIONS = [
    "STR", "LANG", "LANGMATCHES", "DATATYPE", "BOUND", "IRI", "URI",
    "BNODE", "RAND", "ABS", "CEIL", "FLOOR", "ROUND", "CONCAT",
    "SUBSTR", "STRLEN", "REPLACE", "UCASE", "LCASE", "ENCODE_FOR_URI",
    "CONTAINS", "STRSTARTS", "STRENDS", "STRBEFORE", "STRAFTER",
    "YEAR", "MONTH", "DAY", "HOURS", "MINUTES", "SECONDS", "TIMEZONE",
    "TZ", "NOW", "UUID", "STRUUID", "MD5", "SHA1", "SHA256",
    "COALESCE", "IF", "STRLANG", "STRDT", "sameTerm",
    "isIRI", "isURI", "isBLANK", "isLITERAL", "isNUMERIC", "REGEX",
    "COUNT", "SUM", "MIN", "MAX", "AVG", "SAMPLE", "GROUP_CONCAT"
]

# Common prefixes
COMMON_PREFIXES = [
    "rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>",
    "rdfs: <http://www.w3.org/2000/01/rdf-schema#>",
    "owl: <http://www.w3.org/2002/07/owl#>",
    "xsd: <http://www.w3.org/2001/XMLSchema#>",
    "foaf: <http://xmlns.com/foaf/0.1/>",
    "dc: <http://purl.org/dc/elements/1.1/>",
    "dcterms: <http://purl.org/dc/terms/>",
    "skos: <http://www.w3.org/2004/02/skos/core#>",
    "schema: <http://schema.org/>",
    "kb: <http://example.org/kb/>",
]


class SPARQLCompleter:
    """
    Provides auto-completion for a QPlainTextEdit SPARQL editor.
    Uses a popup QListWidget since QPlainTextEdit doesn't natively support QCompleter.
    """
    
    def __init__(self, text_edit, rdf_manager=None):
        self.text_edit = text_edit
        self.rdf_manager = rdf_manager
        
        # Create popup list
        self.popup = QListWidget()
        self.popup.setWindowFlags(Qt.WindowType.Popup)
        self.popup.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.popup.setMouseTracking(True)
        self.popup.setStyleSheet("""
            QListWidget {
                border: 1px solid #555;
                background-color: #2b2b2b;
                color: #e0e0e0;
                font-family: "Consolas", "Courier New", monospace;
                font-size: 13px;
            }
            QListWidget::item:selected {
                background-color: #3a6ea5;
            }
        """)
        self.popup.setMaximumHeight(200)
        self.popup.setMaximumWidth(350)
        self.popup.itemClicked.connect(self.insert_completion)
        
        # Build base completions
        self.base_completions = sorted(
            set(SPARQL_KEYWORDS + SPARQL_FUNCTIONS),
            key=str.lower
        )
        
        # Connect to text changes
        self.text_edit.textChanged.connect(self.on_text_changed)
    
    def on_text_changed(self):
        """Called when the text changes. Shows/hides the popup."""
        cursor = self.text_edit.textCursor()
        text = self.text_edit.toPlainText()
        pos = cursor.position()
        
        # Get current word being typed
        word = self._get_current_word(text, pos)
        
        if len(word) < 2:
            self.popup.hide()
            return
        
        # Build completion list
        candidates = self._get_candidates(text, word)
        
        if not candidates:
            self.popup.hide()
            return
        
        # Populate popup
        self.popup.clear()
        for item in candidates[:15]:  # Limit to 15 suggestions
            self.popup.addItem(item)
        
        # Position popup below cursor
        cursor_rect = self.text_edit.cursorRect()
        global_pos = self.text_edit.mapToGlobal(cursor_rect.bottomLeft())
        self.popup.move(global_pos)
        self.popup.setCurrentRow(0)
        self.popup.show()
    
    def _get_current_word(self, text, pos):
        """Extracts the word being typed at the cursor position."""
        if pos == 0:
            return ""
        
        # Walk backwards from cursor
        start = pos - 1
        while start >= 0 and (text[start].isalnum() or text[start] in '?$_:'):
            start -= 1
        start += 1
        
        return text[start:pos]
    
    def _get_candidates(self, full_text, prefix):
        """Returns matching completion candidates."""
        candidates = []
        prefix_upper = prefix.upper()
        prefix_lower = prefix.lower()
        
        # 1. SPARQL keywords and functions
        for kw in self.base_completions:
            if kw.upper().startswith(prefix_upper):
                candidates.append(kw)
        
        # 2. Variables already used in the query
        if prefix.startswith('?') or prefix.startswith('$'):
            vars_in_query = set(re.findall(r'[?$]\w+', full_text))
            for v in sorted(vars_in_query):
                if v.startswith(prefix) and v != prefix:
                    candidates.append(v)
        
        # 3. Prefix suggestions after "PREFIX "
        if prefix_upper.startswith("PREFIX"):
            candidates = ["PREFIX " + p for p in COMMON_PREFIXES]
        
        # 4. Namespace prefixes from the loaded graph
        if self.rdf_manager and ':' in prefix:
            ns_prefix = prefix.split(':')[0]
            for p, uri in self.rdf_manager.get_namespaces():
                if p.startswith(ns_prefix):
                    candidates.append(f"{p}:")
        
        return candidates
    
    def insert_completion(self, item):
        """Inserts the selected completion into the text editor."""
        completion = item.text()
        
        cursor = self.text_edit.textCursor()
        text = self.text_edit.toPlainText()
        pos = cursor.position()
        
        # Find the start of the current word
        word = self._get_current_word(text, pos)
        
        # Replace the partial word with the completion
        cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.MoveAnchor, len(word))
        cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, len(word))
        cursor.insertText(completion)
        
        self.text_edit.setTextCursor(cursor)
        self.popup.hide()
    
    def handle_key_press(self, event):
        """
        Handle special keys when the popup is visible.
        Returns True if the event was consumed, False otherwise.
        """
        if not self.popup.isVisible():
            return False
        
        key = event.key()
        
        if key == Qt.Key.Key_Down:
            row = self.popup.currentRow()
            if row < self.popup.count() - 1:
                self.popup.setCurrentRow(row + 1)
            return True
        
        elif key == Qt.Key.Key_Up:
            row = self.popup.currentRow()
            if row > 0:
                self.popup.setCurrentRow(row - 1)
            return True
        
        elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Tab):
            current = self.popup.currentItem()
            if current:
                self.insert_completion(current)
            return True
        
        elif key == Qt.Key.Key_Escape:
            self.popup.hide()
            return True
        
        return False

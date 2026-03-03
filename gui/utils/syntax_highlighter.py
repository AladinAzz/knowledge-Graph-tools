"""
Syntax Highlighter Module

This module provides a QSyntaxHighlighter for SPARQL queries.
"""

from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import QRegularExpression

class SPARQLHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)

        self.highlighting_rules = []

        # Keyword Format (Blue, Bold)
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("darkblue"))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        
        keywords = [
            "SELECT", "WHERE", "FILTER", "OPTIONAL", "UNION", "Generic",
            "DISTINCT", "LIMIT", "OFFSET", "ORDER BY", "ASC", "DESC",
            "Construct", "DESCRIBE", "ASK", "PREFIX", "BASE",
            "FROM", "NAMED", "GRAPH", "MINUS", "EXISTS", "NOT EXISTS",
            "BIND", "AS", "VALUES", "a"
        ]
        
        for word in keywords:
            pattern = QRegularExpression(f"\\b{word}\\b", QRegularExpression.PatternOption.CaseInsensitiveOption)
            self.highlighting_rules.append((pattern, keyword_format))

        # Variable Format (Green) ?var or $var
        variable_format = QTextCharFormat()
        variable_format.setForeground(QColor("darkgreen"))
        self.highlighting_rules.append((QRegularExpression("[?$]\\w+"), variable_format))

        # Function/Built-in Format (Purple)
        function_format = QTextCharFormat()
        function_format.setForeground(QColor("purple"))
        functions = [
            "STR", "LANG", "LANGMATCHES", "DATATYPE", "BOUND", "IRI", "URI",
            "BNODE", "RAND", "ABS", "CEIL", "FLOOR", "ROUND", "CONCAT",
            "SUBSTR", "STRLEN", "REPLACE", "UCASE", "LCASE", "ENCODE_FOR_URI",
            "CONTAINS", "STRSTARTS", "STRENDS", "STRBEFORE", "STRAFTER",
            "YEAR", "MONTH", "DAY", "HOURS", "MINUTES", "SECONDS", "TIMEZONE",
            "TZ", "NOW", "UUID", "STRUUID", "MD5", "SHA1", "SHA256", "SHA384",
            "SHA512", "COALESCE", "IF", "STRLANG", "STRDT", "sameTerm",
            "isIRI", "isURI", "isBLANK", "isLITERAL", "isNUMERIC", "REGEX"
        ]
        for func in functions:
             pattern = QRegularExpression(f"\\b{func}\\b", QRegularExpression.PatternOption.CaseInsensitiveOption)
             self.highlighting_rules.append((pattern, function_format))

        # URI Format (Dark Cyan) <http://...>
        uri_format = QTextCharFormat()
        uri_format.setForeground(QColor("darkcyan"))
        self.highlighting_rules.append((QRegularExpression("<[^>]+>"), uri_format))
        
        # QName Format (Dark Cyan) prefix:suffix
        qname_format = QTextCharFormat()
        qname_format.setForeground(QColor("darkcyan"))
        # Simple QName regex
        self.highlighting_rules.append((QRegularExpression("\\w*:\\w+"), qname_format))

        # String Format (Red) "string" or 'string'
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("darkred"))
        self.highlighting_rules.append((QRegularExpression("\".*\""), string_format))
        self.highlighting_rules.append((QRegularExpression("'.*'"), string_format))

        # Comment Format (Gray, Italic) # comment
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("gray"))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((QRegularExpression("#[^\n]*"), comment_format))

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)

"""
Query Widget Module

This module defines the QueryWidget, which provides an interface for executing SPARQL queries
(SELECT, CONSTRUCT, ASK, DESCRIBE) and SPARQL UPDATE operations (INSERT, DELETE).
It includes a text area for query input with syntax highlighting and auto-completion,
a table for displaying results, a graph view for visualization, and query history.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit, 
                             QPushButton, QTableWidget, QTableWidgetItem, QLabel, 
                             QHeaderView, QMessageBox, QTabWidget, QListWidget, 
                             QSplitter, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from rdflib import Graph, URIRef, Literal, BNode
from .graph_viewer import GraphViewer
from gui.utils.syntax_highlighter import SPARQLHighlighter
from gui.utils.sparql_completer import SPARQLCompleter
import json
import csv

class QueryWidget(QWidget):
    """
    A widget for entering and executing SPARQL queries and displaying results.
    """
    # Signal emitted when an UPDATE modifies the graph
    graph_updated = pyqtSignal()
    
    def __init__(self, sparql_engine, settings_manager, rdf_manager=None):
        super().__init__()
        self.sparql_engine = sparql_engine
        self.settings_manager = settings_manager
        self.rdf_manager = rdf_manager
        self.current_results = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Top Section: Splitter for Input and History
        top_splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(top_splitter)
        
        # Left: Query Input
        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)
        input_layout.setContentsMargins(0, 0, 0, 0)
        
        self.query_input = QPlainTextEdit()
        self.query_input.setPlaceholderText("Enter SPARQL Query here...")
        self.query_input.setPlainText("SELECT * WHERE { ?s ?p ?o } LIMIT 10")
        input_layout.addWidget(QLabel("SPARQL Query:"))
        
        # Apply Syntax Highlighter
        self.highlighter = SPARQLHighlighter(self.query_input.document())
        
        # Apply Auto-Completer
        self.completer = SPARQLCompleter(self.query_input, self.rdf_manager)
        
        input_layout.addWidget(self.query_input)
        
        # Button row
        btn_row = QHBoxLayout()
        self.exec_btn = QPushButton("Execute Query")
        self.exec_btn.clicked.connect(self.run_query)
        btn_row.addWidget(self.exec_btn)
        
        self.update_btn = QPushButton("Execute UPDATE")
        self.update_btn.setToolTip("Run INSERT/DELETE SPARQL UPDATE operations")
        self.update_btn.clicked.connect(self.run_update)
        btn_row.addWidget(self.update_btn)
        
        input_layout.addLayout(btn_row)
        
        top_splitter.addWidget(input_widget)
        
        # Right: History
        history_widget = QWidget()
        history_layout = QVBoxLayout(history_widget)
        history_layout.setContentsMargins(0, 0, 0, 0)
        
        history_layout.addWidget(QLabel("History:"))
        self.history_list = QListWidget()
        self.history_list.itemDoubleClicked.connect(self.load_history_query)
        # Load from settings (single source of truth)
        self.history_list.addItems(self.settings_manager.get_query_history())
        history_layout.addWidget(self.history_list)
        
        top_splitter.addWidget(history_widget)
        
        # Set initial sizes (70% Input, 30% History)
        top_splitter.setStretchFactor(0, 3)
        top_splitter.setStretchFactor(1, 1)

        # Status bar for timing
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: gray; font-style: italic; padding: 2px;")
        layout.addWidget(self.status_label)

        # Results Area (Tabs)
        layout.addWidget(QLabel("Results:"))
        self.results_tabs = QTabWidget()
        layout.addWidget(self.results_tabs)
        
        # Table Tab
        self.results_table = QTableWidget()
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.results_tabs.addTab(self.results_table, "Table")
        
        # Graph Tab
        self.results_graph = GraphViewer()
        self.results_tabs.addTab(self.results_graph, "Visualization")
        
        # Export Button
        self.export_btn = QPushButton("Export Results")
        self.export_btn.clicked.connect(self.export_results)
        layout.addWidget(self.export_btn)

    def run_query(self):
        query_text = self.query_input.toPlainText().strip()
        if not query_text:
            return
        
        # Auto-detect UPDATE queries and redirect
        if self.sparql_engine.is_update_query(query_text):
            self.run_update()
            return
            
        try:
            results, elapsed = self.sparql_engine.execute_query(query_text)
            formatted = self.sparql_engine.format_results(results)
            self.current_results = formatted
            self.display_results(formatted)
            
            # Show timing
            count = len(formatted.get('bindings', [])) if formatted['type'] == 'SELECT' else 0
            self.status_label.setText(f"✓ {count} result(s) in {elapsed:.3f}s")
            
            # Add to history (single source of truth via settings_manager)
            self._add_to_history(query_text)
                 
        except Exception as e:
            self.status_label.setText(f"✗ Query failed")
            QMessageBox.critical(self, "Query Error", str(e))
    
    def run_update(self):
        """Execute a SPARQL UPDATE (INSERT/DELETE) operation."""
        query_text = self.query_input.toPlainText().strip()
        if not query_text:
            return
        
        try:
            result, elapsed = self.sparql_engine.execute_update(query_text)
            delta = result['delta']
            sign = "+" if delta >= 0 else ""
            self.status_label.setText(
                f"✓ UPDATE completed in {elapsed:.3f}s — "
                f"{result['triples_before']} → {result['triples_after']} triples ({sign}{delta})"
            )
            
            # Add to history
            self._add_to_history(query_text)
            
            # Notify main window to refresh views
            self.graph_updated.emit()
            
            QMessageBox.information(self, "UPDATE Success", 
                f"UPDATE completed successfully.\n"
                f"Triples: {result['triples_before']} → {result['triples_after']} ({sign}{delta})")
                
        except Exception as e:
            self.status_label.setText(f"✗ UPDATE failed")
            QMessageBox.critical(self, "UPDATE Error", str(e))
    
    def _add_to_history(self, query_text):
        """Add a query to history via the settings manager (single source of truth)."""
        history = self.settings_manager.get_query_history()
        if query_text not in history:
            self.settings_manager.add_to_history(query_text)
            self.settings_manager.save_settings()
            # Refresh the UI list
            self.history_list.clear()
            self.history_list.addItems(self.settings_manager.get_query_history())

    def load_history_query(self, item):
        self.query_input.setPlainText(item.text())

    def display_results(self, formatted):
        self.results_table.clear()
        
        if formatted['type'] == 'SELECT':
            self.results_tabs.setCurrentIndex(0)
            vars = formatted['vars']
            self.results_table.setColumnCount(len(vars))
            self.results_table.setHorizontalHeaderLabels([str(v) for v in vars])
            
            bindings = formatted['bindings']
            self.results_table.setRowCount(len(bindings))
            
            # Construct a temporary graph for visualization if we have 3 vars (s, p, o potential)
            temp_graph = Graph()
            has_graph_data = False
            
            if len(vars) == 3:
                v1, v2, v3 = vars[0], vars[1], vars[2]
                has_graph_data = True
            
            for row_idx, row_data in enumerate(bindings):
                for col_idx, var in enumerate(vars):
                    val = row_data.get(str(var), None)
                    str_val = str(val) if val is not None else ""
                    self.results_table.setItem(row_idx, col_idx, QTableWidgetItem(str_val))
                
                if has_graph_data:
                    try:
                        s = row_data.get(str(v1))
                        p = row_data.get(str(v2))
                        o = row_data.get(str(v3))
                        if s and p and o:
                            temp_graph.add((s, p, o))
                    except:
                        pass
                        
            if has_graph_data and len(temp_graph) > 0:
                self.results_graph.display_graph(temp_graph)
            else:
                 self.results_graph.display_graph(Graph())
                    
        elif formatted['type'] == 'ASK':
            self.results_tabs.setCurrentIndex(0)
            self.results_table.setColumnCount(1)
            self.results_table.setRowCount(1)
            self.results_table.setHorizontalHeaderLabels(["Result"])
            self.results_table.setItem(0, 0, QTableWidgetItem(str(formatted['boolean'])))
            
        elif formatted['type'] == 'CONSTRUCT' or formatted['type'] == 'DESCRIBE':
            graph = formatted['graph']
            self.results_table.setColumnCount(3)
            self.results_table.setHorizontalHeaderLabels(["Subject", "Predicate", "Object"])
            self.results_table.setRowCount(len(graph))
            
            for row_idx, (s, p, o) in enumerate(graph):
                self.results_table.setItem(row_idx, 0, QTableWidgetItem(str(s)))
                self.results_table.setItem(row_idx, 1, QTableWidgetItem(str(p)))
                self.results_table.setItem(row_idx, 2, QTableWidgetItem(str(o)))
                
            self.results_graph.display_graph(graph)
            self.results_tabs.setCurrentIndex(1)

    def export_results(self):
        if not self.current_results:
            QMessageBox.warning(self, "Warning", "No results to export.")
            return

        import xml.etree.ElementTree as ET

        file_path, _ = QFileDialog.getSaveFileName(self, "Export Results", "", 
                                                   "JSON (*.json);;CSV (*.csv);;XML (*.xml)")
        if not file_path:
            return
            
        try:
            data = self.current_results
            if file_path.endswith('.json'):
                if data['type'] in ['CONSTRUCT', 'DESCRIBE']:
                    triples = []
                    for s, p, o in data['graph']:
                        triples.append({"s": str(s), "p": str(p), "o": str(o)})
                    export_data = {"type": data['type'], "triples": triples}
                else:
                    export_data = data
                    
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=4, default=str)
                    
            elif file_path.endswith('.csv'):
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    if data['type'] == 'SELECT':
                        vars_list = [str(v) for v in data['vars']]
                        writer.writerow(vars_list)
                        for row in data['bindings']:
                            writer.writerow([str(row.get(v, "")) for v in vars_list])
                    elif data['type'] in ['CONSTRUCT', 'DESCRIBE']:
                        writer.writerow(["Subject", "Predicate", "Object"])
                        for s, p, o in data['graph']:
                            writer.writerow([str(s), str(p), str(o)])
                    elif data['type'] == 'ASK':
                        writer.writerow(["Result"])
                        writer.writerow([data['boolean']])
                        
            elif file_path.endswith('.xml'):
                if data['type'] == 'SELECT':
                    root = ET.Element("sparql")
                    root.set("xmlns", "http://www.w3.org/2005/sparql-results#")
                    head = ET.SubElement(root, "head")
                    for var in data['vars']:
                        ET.SubElement(head, "variable", name=str(var))
                    results_elem = ET.SubElement(root, "results")
                    for binding in data['bindings']:
                        result = ET.SubElement(results_elem, "result")
                        for var in data['vars']:
                            val = binding.get(str(var))
                            if val is not None:
                                b_elem = ET.SubElement(result, "binding", name=str(var))
                                # BUG-5 fix: proper type detection using isinstance
                                if isinstance(val, URIRef):
                                    ET.SubElement(b_elem, "uri").text = str(val)
                                elif isinstance(val, BNode):
                                    ET.SubElement(b_elem, "bnode").text = str(val)
                                else:
                                    ET.SubElement(b_elem, "literal").text = str(val)
                    tree = ET.ElementTree(root)
                    tree.write(file_path, encoding="utf-8", xml_declaration=True)
                    
                elif data['type'] in ['CONSTRUCT', 'DESCRIBE']:
                    g_out = Graph()
                    for s, p, o in data['graph']:
                        g_out.add((s, p, o))
                    g_out.serialize(destination=file_path, format='xml')
                    
                elif data['type'] == 'ASK':
                    root = ET.Element("sparql")
                    root.set("xmlns", "http://www.w3.org/2005/sparql-results#")
                    head = ET.SubElement(root, "head")
                    ET.SubElement(root, "boolean").text = str(data['boolean']).lower()
                    tree = ET.ElementTree(root)
                    tree.write(file_path, encoding="utf-8", xml_declaration=True)

            QMessageBox.information(self, "Success", f"Exported to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export: {e}")

"""
Query Widget Module

This module defines the QueryWidget, which provides an interface for executing SPARQL queries.
It includes a text area for query input, a table for displaying results, and a graph view
for visualizing CONSTRUCT/DESCRIBE results or SELECT results that return triples.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit, 
                             QPushButton, QTableWidget, QTableWidgetItem, QLabel, QHeaderView, QMessageBox, QTabWidget, QListWidget, QSplitter)
from PyQt6.QtCore import Qt
from rdflib import Graph
from .graph_viewer import GraphViewer
from gui.utils.syntax_highlighter import SPARQLHighlighter

class QueryWidget(QWidget):
    """
    A widget for entering and executing SPARQL queries and displaying results.
    """
    def __init__(self, sparql_engine, settings_manager):
        super().__init__()
        self.sparql_engine = sparql_engine
        self.settings_manager = settings_manager
        self.query_history = self.settings_manager.get_query_history() # Load from settings
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
        
        input_layout.addWidget(self.query_input)
        
        self.exec_btn = QPushButton("Execute Query")
        self.exec_btn.clicked.connect(self.run_query)
        input_layout.addWidget(self.exec_btn)
        
        top_splitter.addWidget(input_widget)
        
        # Right: History
        history_widget = QWidget()
        history_layout = QVBoxLayout(history_widget)
        history_layout.setContentsMargins(0, 0, 0, 0)
        
        history_layout.addWidget(QLabel("History:"))
        self.history_list = QListWidget()
        self.history_list.itemDoubleClicked.connect(self.load_history_query)
        self.history_list.addItems(self.query_history) # Populate list
        history_layout.addWidget(self.history_list)
        
        top_splitter.addWidget(history_widget)
        
        # Set initial sizes (70% Input, 30% History)
        top_splitter.setStretchFactor(0, 3)
        top_splitter.setStretchFactor(1, 1)

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
            
        try:
            results = self.sparql_engine.execute_query(query_text)
            formatted = self.sparql_engine.format_results(results)
            self.current_results = formatted # Store for export
            self.display_results(formatted)
            
            # Add to history if unique or not recent
            if query_text not in self.query_history:
                self.query_history.insert(0, query_text) # Prepend
                self.history_list.insertItem(0, query_text)
                
                # Persist
                self.settings_manager.add_to_history(query_text)
                self.settings_manager.save_settings()
                
            elif self.query_history and self.query_history[0] != query_text:
                 # Move to top?
                 pass
                 
        except Exception as e:
            QMessageBox.critical(self, "Query Error", str(e))

    def load_history_query(self, item):
        self.query_input.setPlainText(item.text())

    def display_results(self, formatted):
        self.results_table.clear()
        
        if formatted['type'] == 'SELECT':
            self.results_tabs.setCurrentIndex(0) # Switch to Table
            vars = formatted['vars']
            self.results_table.setColumnCount(len(vars))
            self.results_table.setHorizontalHeaderLabels([str(v) for v in vars])
            
            bindings = formatted['bindings']
            self.results_table.setRowCount(len(bindings))
            
            # Construct a temporary graph for visualization if we have 3 vars (s, p, o potential)
            temp_graph = Graph()
            has_graph_data = False
            
            # Check if we have 3 variables
            if len(vars) == 3:
                # Naive assumption: columns are s, p, o in order? 
                # Or just take the first 3.
                v1, v2, v3 = vars[0], vars[1], vars[2]
                has_graph_data = True
            
            for row_idx, row_data in enumerate(bindings):
                # Update Table
                for col_idx, var in enumerate(vars):
                    val = row_data.get(str(var), None)
                    str_val = str(val) if val is not None else ""
                    self.results_table.setItem(row_idx, col_idx, QTableWidgetItem(str_val))
                
                # Update Graph logic
                if has_graph_data:
                    try:
                        s = row_data.get(str(v1))
                        p = row_data.get(str(v2))
                        o = row_data.get(str(v3))
                        if s and p and o:
                            temp_graph.add((s, p, o))
                    except:
                        pass # enhancing visualization shouldn't crash result display
                        
            # If we populated the graph, show it in the tab
            if has_graph_data and len(temp_graph) > 0:
                self.results_graph.display_graph(temp_graph)
                # We can decide whether to auto-switch or not. 
                # User asked for "link", maybe keeping table as primary for SELECT is better, 
                # but having the graph available is key.
                # self.results_tabs.setCurrentIndex(1) # Optional: auto-switch
            else:
                 # Clear graph if no valid data
                 self.results_graph.display_graph(Graph())
                    
        elif formatted['type'] == 'ASK':
            self.results_tabs.setCurrentIndex(0) # Switch to Table
            self.results_table.setColumnCount(1)
            self.results_table.setRowCount(1)
            self.results_table.setHorizontalHeaderLabels(["Result"])
            self.results_table.setItem(0, 0, QTableWidgetItem(str(formatted['boolean'])))
            
        elif formatted['type'] == 'CONSTRUCT' or formatted['type'] == 'DESCRIBE':
            # Display graph as triples in Table
            graph = formatted['graph']
            self.results_table.setColumnCount(3)
            self.results_table.setHorizontalHeaderLabels(["Subject", "Predicate", "Object"])
            self.results_table.setRowCount(len(graph))
            
            for row_idx, (s, p, o) in enumerate(graph):
                self.results_table.setItem(row_idx, 0, QTableWidgetItem(str(s)))
                self.results_table.setItem(row_idx, 1, QTableWidgetItem(str(p)))
                self.results_table.setItem(row_idx, 2, QTableWidgetItem(str(o)))
                
            # Display graph in GraphViewer
            self.results_graph.display_graph(graph)
            self.results_tabs.setCurrentIndex(1) # Switch to Visualization

    def export_results(self):
        if not hasattr(self, 'current_results') or not self.current_results:
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
                # For graph, we can't easily serialize with json dump directly if it contains rdflib objects
                # Need to convert to serializable format
                if data['type'] in ['CONSTRUCT', 'DESCRIBE']:
                    # Serialize graph to JSON-LD or just triples list
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
                        vars = [str(v) for v in data['vars']]
                        writer.writerow(vars)
                        for row in data['bindings']:
                            writer.writerow([row.get(str(v), "") for v in vars])
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
                            if val:
                                b_elem = ET.SubElement(result, "binding", name=str(var))
                                # Naive check for URI vs Literal vs BNode
                                if val.startswith("http"):
                                    ET.SubElement(b_elem, "uri").text = str(val)
                                else:
                                    ET.SubElement(b_elem, "literal").text = str(val)
                    tree = ET.ElementTree(root)
                    tree.write(file_path, encoding="utf-8", xml_declaration=True)
                    
                elif data['type'] in ['CONSTRUCT', 'DESCRIBE']:
                    # Use rdflib's serializer
                    # Convert list of triples back to graph if needed or just add to temp graph
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

            QMessageBox.information(self, "Success", f"exported to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export: {e}")

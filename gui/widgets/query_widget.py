from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit, 
                             QPushButton, QTableWidget, QTableWidgetItem, QLabel, QHeaderView, QMessageBox, QTabWidget)
from rdflib import Graph
from .graph_viewer import GraphViewer

class QueryWidget(QWidget):
    def __init__(self, sparql_engine):
        super().__init__()
        self.sparql_engine = sparql_engine
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Query Input Area
        self.query_input = QPlainTextEdit()
        self.query_input.setPlaceholderText("Enter SPARQL Query here...")
        self.query_input.setPlainText("SELECT * WHERE { ?s ?p ?o } LIMIT 10")
        layout.addWidget(QLabel("SPARQL Query:"))
        layout.addWidget(self.query_input)

        # Execute Button
        self.exec_btn = QPushButton("Execute Query")
        self.exec_btn.clicked.connect(self.run_query)
        layout.addWidget(self.exec_btn)

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
        query_text = self.query_input.toPlainText()
        try:
            results = self.sparql_engine.execute_query(query_text)
            formatted = self.sparql_engine.format_results(results)
            self.current_results = formatted # Store for export
            self.display_results(formatted)
        except Exception as e:
            QMessageBox.critical(self, "Query Error", str(e))

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

        from PyQt6.QtWidgets import QFileDialog
        import json
        import csv

        file_path, _ = QFileDialog.getSaveFileName(self, "Export Results", "", 
                                                   "JSON (*.json);;CSV (*.csv)")
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
                        
            QMessageBox.information(self, "Success", f"exported to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export: {e}")

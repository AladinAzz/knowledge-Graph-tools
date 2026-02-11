"""
Text to RDF Widget

This widget allows users to input text, generate an RDF graph using the KnowledgeExtractor,
and visualize the result. It provides a table view of extracted triples and a graph visualization.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit, 
                             QPushButton, QLabel, QMessageBox, QTabWidget, QTableWidget, 
                             QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import Qt, pyqtSignal
from rdflib import Graph
from core.knowledge_extractor import KnowledgeExtractor
from .graph_viewer import GraphViewer

class TextKGWidget(QWidget):
    # Signal emitted when new triples are merged into the main graph
    graph_merged = pyqtSignal()

    def __init__(self, rdf_manager):
        super().__init__()
        self.rdf_manager = rdf_manager
        self.extractor = KnowledgeExtractor()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 1. Text Input Area
        layout.addWidget(QLabel("Input Text for RDF Generation:"))
        self.text_input = QPlainTextEdit()
        self.text_input.setPlaceholderText("Enter text here (e.g., 'Albert Einstein was born in Ulm.')...")
        layout.addWidget(self.text_input)
        
        # 2. Action Buttons
        btn_layout = QHBoxLayout()
        self.generate_btn = QPushButton("Generate RDF")
        self.generate_btn.clicked.connect(self.generate_graph)
        btn_layout.addWidget(self.generate_btn)
        
        self.add_to_main_btn = QPushButton("Merge to Main Graph")
        self.add_to_main_btn.clicked.connect(self.add_to_main_graph)
        self.add_to_main_btn.setEnabled(False)
        btn_layout.addWidget(self.add_to_main_btn)
        
        layout.addLayout(btn_layout)
        
        # 3. Results Area (Tabs)
        layout.addWidget(QLabel("Results:"))
        self.results_tabs = QTabWidget()
        layout.addWidget(self.results_tabs)
        
        # Tab 1: Table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(3)
        self.results_table.setHorizontalHeaderLabels(["Subject", "Predicate", "Object"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.results_tabs.addTab(self.results_table, "Table")
        
        # Tab 2: Visualization
        self.graph_viewer = GraphViewer()
        self.results_tabs.addTab(self.graph_viewer, "Visualization")
        
        # 4. Export Button
        self.export_btn = QPushButton("Export RDF")
        self.export_btn.clicked.connect(self.export_rdf)
        self.export_btn.setEnabled(False)
        layout.addWidget(self.export_btn)
        
        # State
        self.generated_graph = None

    def generate_graph(self):
        text = self.text_input.toPlainText()
        if not text:
            QMessageBox.warning(self, "Warning", "Please enter some text.")
            return
            
        try:
            self.generated_graph = self.extractor.extract_triples(text)
            
            # Update Table
            self.display_table(self.generated_graph)
            
            # Update Graph View
            self.graph_viewer.display_graph(self.generated_graph)
            
            if len(self.generated_graph) > 0:
                self.add_to_main_btn.setEnabled(True)
                self.export_btn.setEnabled(True)
                self.results_tabs.setCurrentIndex(1) # Switch to Viz by default? Or Table? User said same as SPARQL.
                # In SPARQL, CONSTRUCT goes to Viz. This is like CONSTRUCT.
                QMessageBox.information(self, "Success", f"Generated {len(self.generated_graph)} triples.")
            else:
                self.add_to_main_btn.setEnabled(False)
                self.export_btn.setEnabled(False)
                QMessageBox.information(self, "Info", "No triples extracted.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Extraction failed: {e}")

    def display_table(self, graph):
        self.results_table.setRowCount(len(graph))
        for row_idx, (s, p, o) in enumerate(graph):
            self.results_table.setItem(row_idx, 0, QTableWidgetItem(str(s)))
            self.results_table.setItem(row_idx, 1, QTableWidgetItem(str(p)))
            self.results_table.setItem(row_idx, 2, QTableWidgetItem(str(o)))

    def add_to_main_graph(self):
        if self.generated_graph:
            try:
                # Add generated triples to the main RDF manager's graph
                self.rdf_manager.graph += self.generated_graph
                QMessageBox.information(self, "Success", "Added extracted triples to the main graph.")
                self.add_to_main_btn.setEnabled(False) # Prevent double adding
                
                # Emit signal to notify parent
                self.graph_merged.emit()
                
            except Exception as e:
                 QMessageBox.critical(self, "Error", f"Failed to add to main graph: {e}")

    def export_rdf(self):
        if not self.generated_graph:
            return
            
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(self, "Export RDF", "", 
                                                   "Turtle (*.ttl);;RDF/XML (*.rdf *.xml);;N-Triples (*.nt)")
        if file_path:
            try:
                fmt = 'turtle'
                if file_path.endswith('.xml') or file_path.endswith('.rdf'): fmt = 'xml'
                elif file_path.endswith('.nt'): fmt = 'nt'
                
                self.generated_graph.serialize(destination=file_path, format=fmt)
                QMessageBox.information(self, "Success", f"RDF exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export: {e}")

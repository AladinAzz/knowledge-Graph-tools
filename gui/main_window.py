"""
Main Window Module

This module defines the main application window (MainWindow).
It orchestrates the UI layout, initializes core components (RDFManager, SPARQLEngine, etc.),
and handles high-level user interactions such as loading files and executing reasoning.
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTabWidget, 
                             QDockWidget, QFileDialog, QMessageBox, QMenu, QMenuBar)
from PyQt6.QtCore import Qt
import os

from core.rdf_manager import RDFManager
from core.ontology_manager import OntologyManager
from core.sparql_engine import SPARQLEngine
from core.reasoner import ReasoningEngine

from gui.widgets.graph_viewer import GraphViewer
from gui.widgets.query_widget import QueryWidget
from gui.widgets.ontology_tree import OntologyTree

class MainWindow(QMainWindow):
    """
    The main window of the application.
    Integrates the graph viewer, query widget, and ontology tree.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KB Manager")
        self.resize(1200, 800)

        # Initialize Logic
        self.rdf_manager = RDFManager()
        self.ontology_manager = OntologyManager()
        self.sparql_engine = SPARQLEngine(self.rdf_manager)
        self.reasoner_engine = ReasoningEngine()
        
        # Setup UI
        self.init_ui()

    def init_ui(self):
        # Menu Bar
        self.create_menus()
        
        # Central Area (Tabs for Graph & Query)
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.graph_viewer = GraphViewer()
        self.query_widget = QueryWidget(self.sparql_engine)
        
        self.tabs.addTab(self.graph_viewer, "Graph Visualization")
        self.tabs.addTab(self.query_widget, "SPARQL Query")
        
        # Dock Widget for Ontology Tree
        self.dock = QDockWidget("Ontology Hierarchy", self)
        self.ontology_tree = OntologyTree()
        self.dock.setWidget(self.ontology_tree)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock)

    def create_menus(self):
        menu_bar = self.menuBar()
        
        # File Menu
        file_menu = menu_bar.addMenu("File")
        
        load_rdf_action = file_menu.addAction("Load RDF Graph")
        load_rdf_action.triggered.connect(self.load_rdf)
        
        load_onto_action = file_menu.addAction("Load Ontology")
        load_onto_action.triggered.connect(self.load_ontology)
        
        file_menu.addSeparator()
        
        reset_action = file_menu.addAction("Reset/Clear Graph")
        reset_action.triggered.connect(self.reset_graph)
        
        file_menu.addSeparator()
        
        export_action = file_menu.addAction("Export Graph")
        export_action.triggered.connect(self.export_graph)
        
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        
        # Reasoning Menu
        reasoning_menu = menu_bar.addMenu("Reasoning")
        
        run_hermit_action = reasoning_menu.addAction("Run Reasoner (HermiT)")
        run_hermit_action.triggered.connect(lambda: self.run_reasoner('hermit'))
        
        run_pellet_action = reasoning_menu.addAction("Run Reasoner (Pellet)")
        run_pellet_action.triggered.connect(lambda: self.run_reasoner('pellet'))

    def load_rdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open RDF File", "", 
                                                   "RDF Files (*.ttl *.xml *.rdf *.nt);;All Files (*)")
        if file_path:
            try:
                self.rdf_manager.load_file(file_path)
                self.graph_viewer.display_graph(self.rdf_manager.get_graph())
                QMessageBox.information(self, "Success", f"Loaded {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load RDF: {e}")

    def load_ontology(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Ontology File", "", 
                                                   "Ontology Files (*.owl *.rdf *.xml);;All Files (*)")
        if file_path:
            try:
                # Load into ontology manager
                self.ontology_manager.load_ontology(file_path)
                hierarchy = self.ontology_manager.get_hierarchy()
                self.ontology_tree.display_hierarchy(hierarchy)
                
                # Also load into RDF manager for querying/graph visualization
                self.rdf_manager.load_file(file_path)
                self.graph_viewer.display_graph(self.rdf_manager.get_graph())
                
                QMessageBox.information(self, "Success", f"Loaded Ontology {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load Ontology: {e}")
                
    def reset_graph(self):
        # Clear RDF Graph
        self.rdf_manager = RDFManager()
        self.sparql_engine = SPARQLEngine(self.rdf_manager) # Re-bind
        self.graph_viewer.display_graph(self.rdf_manager.get_graph()) # Clear view
        
        # We might want to clear ontology tree too
        # self.ontology_tree.clear() # If implemented
        QMessageBox.information(self, "Reset", "Graph cleared.")

    def run_reasoner(self, reasoner_type='hermit'):
        # We need an ontology loaded to run reasoning reliably
        # For simplicity, we ask user to pick the ontology file to reason upon
        # OR we could track the last loaded ontology path
        
        file_path, _ = QFileDialog.getOpenFileName(self, f"Select Ontology for Reasoning ({reasoner_type})", "", 
                                                   "Ontology Files (*.owl *.rdf *.xml)")
        if file_path:
            try:
                inferred_graph = self.reasoner_engine.run_reasoner(file_path, reasoner_type=reasoner_type)
                
                # Merge inferred graph into main graph logic if desired, 
                # or just display it.
                # Here we replace the view with the inferred graph
                self.graph_viewer.display_graph(inferred_graph)
                
                # Update SPARQL engine to query over the inferred graph
                # This requires replacing the graph in RDFManager or switching engines
                # For now, let's update RDFManager's graph + inferred
                # self.rdf_manager.graph += inferred_graph # This might be slow
                
                # Better: display standard + inferred
                self.rdf_manager.graph = self.rdf_manager.graph + inferred_graph
                self.graph_viewer.display_graph(self.rdf_manager.get_graph())
                
                QMessageBox.information(self, "Success", f"Reasoning ({reasoner_type}) complete. Graph updated with inferences.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Reasoning failed: {e}")

    def export_graph(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Graph", "", 
                                                   "Turtle (*.ttl);;RDF/XML (*.xml);;N-Triples (*.nt)")
        if file_path:
            try:
                fmt = 'turtle'
                if file_path.endswith('.xml'): fmt = 'xml'
                elif file_path.endswith('.nt'): fmt = 'nt'
                
                self.rdf_manager.save_file(file_path, fmt)
                QMessageBox.information(self, "Success", f"Graph exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export: {e}")
    
    def closeEvent(self, event):
        # Cleanup temp files
        self.graph_viewer.cleanup()
        event.accept()

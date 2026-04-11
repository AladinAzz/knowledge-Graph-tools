"""
Main Window Module

This module defines the main application window (MainWindow).
It orchestrates the UI layout, initializes core components (RDFManager, SPARQLEngine, etc.),
and handles high-level user interactions such as loading files, executing reasoning,
and managing validation.
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTabWidget, 
                             QDockWidget, QFileDialog, QMessageBox, QMenu, QMenuBar, QApplication)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
import os
import tempfile
import sys

from core.rdf_manager import RDFManager
from core.ontology_manager import OntologyManager
from core.sparql_engine import SPARQLEngine
from core.reasoner import ReasoningEngine

from gui.widgets.graph_viewer import GraphViewer
from gui.widgets.query_widget import QueryWidget
from gui.widgets.ontology_tree import OntologyTree
from gui.widgets.text_kg_widget import TextKGWidget
from gui.widgets.stats_widget import StatsWidget

from core.settings_manager import SettingsManager

class MainWindow(QMainWindow):
    """
    The main window of the application.
    Integrates the graph viewer, query widget, ontology tree, text-to-KG widget, and stats panel.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Knowledge Graph Manager")
        self.resize(1200, 800)

        # Initialize Logic
        self.settings_manager = SettingsManager()
        self.rdf_manager = RDFManager()
        self.ontology_manager = OntologyManager()
        self.sparql_engine = SPARQLEngine(self.rdf_manager)
        self.reasoner_engine = ReasoningEngine()
        
        # Setup UI
        self.init_ui()
        
        # Apply Saved Settings
        if self.settings_manager.get_dark_theme():
            self.dark_theme_action.setChecked(True)
            self.toggle_theme()
        
        # Restore reasoning toggle state
        if self.settings_manager.get_reasoning_enabled():
            self.reasoning_toggle_action.setChecked(True)
        
        # Restore reasoning profile
        profile = self.settings_manager.get_reasoning_profile()
        profile_map = {"hermit": 0, "pellet": 1, "rdfs": 2}
        idx = profile_map.get(profile, 0)
        self.reasoner_selector.setCurrentIndex(idx)

    def init_ui(self):
        # Menu Bar
        self.create_menus()
        
        # Toolbar
        self.create_toolbar()
        
        # Central Area (Tabs for Graph & Query)
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.graph_viewer = GraphViewer()
        self.query_widget = QueryWidget(self.sparql_engine, self.settings_manager, self.rdf_manager)
        self.text_kg_widget = TextKGWidget(self.rdf_manager, self.settings_manager)
        
        # Connect signals
        self.text_kg_widget.graph_merged.connect(self.refresh_graph_view)
        self.query_widget.graph_updated.connect(self.refresh_graph_view)
        
        self.tabs.addTab(self.graph_viewer, "Graph Visualization")
        self.tabs.addTab(self.query_widget, "SPARQL Query")
        self.tabs.addTab(self.text_kg_widget, "Text to RDF")
        
        # Dock Widget for Ontology Tree (left)
        self.dock = QDockWidget("Ontology Hierarchy", self)
        self.ontology_tree = OntologyTree()
        self.dock.setWidget(self.ontology_tree)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock)
        
        # Dock Widget for Statistics (right)
        self.stats_dock = QDockWidget("Graph Statistics", self)
        self.stats_widget = StatsWidget(self.rdf_manager)
        self.stats_dock.setWidget(self.stats_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.stats_dock)

    def refresh_graph_view(self):
        """Refreshes the main graph visualization, ontology tree, and statistics."""
        self.graph_viewer.display_graph(self.rdf_manager.get_graph())
        self.stats_widget.update_stats()
        self.refresh_ontology_from_graph()

    def refresh_ontology_from_graph(self):
        """
        Saves the current RDF graph to a temp file and re-loads the ontology hierarchy.
        Uses a COPY of the graph to avoid mutating the main graph (BUG-14 fix).
        """
        if len(self.rdf_manager.get_graph()) == 0:
            self.ontology_tree.tree.clear()
            self.ontology_tree.props_tree.clear()
            return
            
        try:
            fd, temp_path = tempfile.mkstemp(suffix=".owl")
            os.close(fd)
            
            from rdflib import Graph as RDFGraph, RDF, OWL
            
            # BUG-14 fix: create a COPY, never mutate the main graph
            temp_graph = RDFGraph()
            for triple in self.rdf_manager.get_graph():
                temp_graph.add(triple)
            
            # Copy namespace bindings
            for prefix, uri in self.rdf_manager.get_graph().namespaces():
                temp_graph.bind(prefix, uri)
            
            # Identify potential classes and add explicit declarations to the COPY
            used_classes = set()
            for s, p, o in temp_graph.triples((None, RDF.type, None)):
                used_classes.add(o)
                
            for cls in used_classes:
                if (cls, RDF.type, OWL.Class) not in temp_graph:
                    temp_graph.add((cls, RDF.type, OWL.Class))
            
            # Save the copy (not the main graph)
            temp_graph.serialize(destination=temp_path, format="xml")
            
            # Load into ontology manager
            self.ontology_manager.load_ontology(temp_path)
            
            # Update Class Hierarchy Tree
            hierarchy = self.ontology_manager.get_hierarchy()
            self.ontology_tree.display_hierarchy(hierarchy)
            
            # Update Properties Tree
            props_info = self.ontology_manager.get_properties_info()
            self.ontology_tree.display_properties(props_info)
            
            # Cleanup
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
        except Exception as e:
            print(f"Warning: Could not refresh ontology hierarchy: {e}")
            if 'temp_path' in locals() and os.path.exists(temp_path):
                try: os.remove(temp_path)
                except: pass

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

        # View Menu
        view_menu = menu_bar.addMenu("View")
        
        self.dark_theme_action = view_menu.addAction("Dark Theme")
        self.dark_theme_action.setCheckable(True)
        self.dark_theme_action.triggered.connect(self.toggle_theme)
        
        # Reasoning Menu
        reasoning_menu = menu_bar.addMenu("Reasoning")
        
        self.reasoning_toggle_action = reasoning_menu.addAction("Enable Auto-Reasoning")
        self.reasoning_toggle_action.setCheckable(True)
        self.reasoning_toggle_action.triggered.connect(self.toggle_reasoning)
        
        reasoning_menu.addSeparator()
        
        run_hermit_action = reasoning_menu.addAction("Run Reasoner (HermiT)")
        run_hermit_action.triggered.connect(lambda: self.run_reasoner('hermit'))
        
        run_pellet_action = reasoning_menu.addAction("Run Reasoner (Pellet)")
        run_pellet_action.triggered.connect(lambda: self.run_reasoner('pellet'))

        # Tools Menu
        tools_menu = menu_bar.addMenu("Tools")
        
        ns_action = tools_menu.addAction("Manage Namespaces")
        ns_action.triggered.connect(self.manage_namespaces)
        
        tools_menu.addSeparator()
        
        validate_action = tools_menu.addAction("Validate Ontology")
        validate_action.triggered.connect(self.validate_ontology)

    def manage_namespaces(self):
        from gui.widgets.namespace_dialog import NamespaceDialog
        dialog = NamespaceDialog(self.rdf_manager, self)
        dialog.exec()
    
    def validate_ontology(self):
        """Run ontology validation and show results."""
        if len(self.rdf_manager.get_graph()) == 0:
            QMessageBox.warning(self, "Warning", "The graph is empty. Please load data or an ontology first.")
            return
        
        # Ask user to save the graph as .owl before validation
        owl_path, _ = QFileDialog.getSaveFileName(
            self, "Save Graph as OWL for Validation", "ontology.owl",
            "OWL Files (*.owl);;RDF/XML (*.rdf *.xml);;All Files (*)")
        if not owl_path:
            return  # User cancelled
        
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        
        try:
            self.rdf_manager.save_file(owl_path, "xml")
            
            from core.ontology_validator import OntologyValidator
            validator = OntologyValidator()
            results = validator.validate(owl_path)
            
            QApplication.restoreOverrideCursor()
            
            # Show dialog
            from gui.widgets.validation_dialog import ValidationDialog
            dialog = ValidationDialog(results, self)
            dialog.exec()
            
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "Error", f"Validation failed: {e}")

    def create_toolbar(self):
        from PyQt6.QtWidgets import QToolBar, QLabel, QComboBox
        from PyQt6.QtGui import QAction, QIcon
        
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        # Reasoner Profile
        toolbar.addWidget(QLabel("  Reasoning Profile: "))
        self.reasoner_selector = QComboBox()
        self.reasoner_selector.addItems(["OWL DL (HermiT)", "OWL DL (Pellet)", "RDFS (via OWL DL)"])
        self.reasoner_selector.currentIndexChanged.connect(self._save_reasoning_profile)
        toolbar.addWidget(self.reasoner_selector)
        
        toolbar.addSeparator()
        
        run_reasoner_action = QAction("Run Reasoner", self)
        run_reasoner_action.setStatusTip("Run the selected reasoner on the active ontology")
        run_reasoner_action.triggered.connect(self.run_reasoner_from_toolbar)
        toolbar.addAction(run_reasoner_action)
    
    def _save_reasoning_profile(self):
        """Save the reasoning profile selection to settings."""
        profile_map = {0: "hermit", 1: "pellet", 2: "rdfs"}
        profile = profile_map.get(self.reasoner_selector.currentIndex(), "hermit")
        self.settings_manager.set_reasoning_profile(profile)
        self.settings_manager.save_settings()

    def toggle_reasoning(self):
        """Toggle auto-reasoning on/off."""
        enabled = self.reasoning_toggle_action.isChecked()
        self.settings_manager.set_reasoning_enabled(enabled)
        self.settings_manager.save_settings()
        
        status = "enabled" if enabled else "disabled"
        QMessageBox.information(self, "Reasoning", f"Auto-reasoning {status}.\nReasoning will {'automatically run' if enabled else 'only run manually'} when the graph changes.")

    def run_reasoner_from_toolbar(self):
        profile = self.reasoner_selector.currentText()
        if "Pellet" in profile:
            self.run_reasoner('pellet')
        else:
            self.run_reasoner('hermit')

    def load_rdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open RDF File", "", 
                                                   "RDF Files (*.ttl *.xml *.rdf *.nt *.owl *.jsonld *.trig *.nq);;All Files (*)")
        if file_path:
            try:
                self.rdf_manager.load_file(file_path)
                self.graph_viewer.display_graph(self.rdf_manager.get_graph())
                self.stats_widget.update_stats()
                
                # Also refresh ontology tree
                self.refresh_ontology_from_graph()
                
                QMessageBox.information(self, "Success", f"Loaded {file_path}")
                
                # Auto-reasoning if enabled
                if self.settings_manager.get_reasoning_enabled():
                    self.run_reasoner_from_toolbar()
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load RDF: {e}")

    def load_ontology(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Ontology File", "", 
                                                   "Ontology Files (*.owl *.rdf *.xml *.ttl);;All Files (*)")
        if file_path:
            try:
                self.ontology_manager.load_ontology(file_path)
                hierarchy = self.ontology_manager.get_hierarchy()
                self.ontology_tree.display_hierarchy(hierarchy)
                
                # Also display properties
                props_info = self.ontology_manager.get_properties_info()
                self.ontology_tree.display_properties(props_info)
                
                # Also load into RDF manager for querying/graph visualization
                self.rdf_manager.load_file(file_path)
                self.graph_viewer.display_graph(self.rdf_manager.get_graph())
                self.stats_widget.update_stats()
                
                QMessageBox.information(self, "Success", f"Loaded Ontology {file_path}")
                
                # Auto-reasoning if enabled
                if self.settings_manager.get_reasoning_enabled():
                    self.run_reasoner_from_toolbar()
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load Ontology: {e}")
                
    def reset_graph(self):
        # BUG-4 fix: also update references in child widgets
        self.rdf_manager = RDFManager()
        self.sparql_engine = SPARQLEngine(self.rdf_manager)
        
        # Update references in child widgets
        self.query_widget.sparql_engine = self.sparql_engine
        self.query_widget.rdf_manager = self.rdf_manager
        self.text_kg_widget.rdf_manager = self.rdf_manager
        self.stats_widget.rdf_manager = self.rdf_manager
        
        # Clear views
        self.graph_viewer.display_graph(self.rdf_manager.get_graph())
        self.stats_widget.clear_stats()
        
        # Clear ontology tree
        self.ontology_tree.tree.clear()
        self.ontology_tree.props_tree.clear()
        
        QMessageBox.information(self, "Reset", "Graph cleared.")

    def run_reasoner(self, reasoner_type='hermit'):
        if len(self.rdf_manager.get_graph()) == 0:
            QMessageBox.warning(self, "Warning", "The graph is empty. Please load data or an ontology first.")
            return

        # Ask user to save the graph as .owl before reasoning
        owl_path, _ = QFileDialog.getSaveFileName(
            self, "Save Graph as OWL for Reasoning", "ontology.owl",
            "OWL Files (*.owl);;RDF/XML (*.rdf *.xml);;All Files (*)")
        if not owl_path:
            return  # User cancelled

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        
        try:
            # We use XML as it accurately maps global OWL metadata so owlready2 respects the native HTTP URIs.
            self.rdf_manager.save_file(owl_path, "xml")
            
            # Save original graph for diff
            from rdflib import Graph as RDFGraph
            original_graph = RDFGraph()
            for triple in self.rdf_manager.get_graph():
                original_graph.add(triple)
            
            # Run reasoning (now returns tuple with elapsed time)
            inferred_graph, elapsed = self.reasoner_engine.run_reasoner(owl_path, reasoner_type=reasoner_type)
            
            # Calculate the diff (only new triples)
            inferred_only = self.reasoner_engine.apply_inference_to_graph(original_graph, inferred_graph)
            
            # Merge inferred graph into main graph
            initial_count = len(self.rdf_manager.get_graph())
            self.rdf_manager.graph += inferred_graph
            final_count = len(self.rdf_manager.get_graph())
            new_triples = final_count - initial_count
            
            # Refresh Views
            self.graph_viewer.display_graph(self.rdf_manager.get_graph())
            self.stats_widget.update_stats()
            self.refresh_ontology_from_graph()
            
            QApplication.restoreOverrideCursor()
            
            # Show inferred triples dialog
            from gui.widgets.inferred_triples_dialog import InferredTriplesDialog
            dialog = InferredTriplesDialog(inferred_only, elapsed, self)
            dialog.exec()
                
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "Error", f"Reasoning failed: {e}")

    def export_graph(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Graph", "", 
                                                   "Turtle (*.ttl);;RDF/XML (*.rdf *.xml);;N-Triples (*.nt)")
        if file_path:
            try:
                fmt = 'turtle'
                if file_path.endswith('.xml') or file_path.endswith('.rdf'): fmt = 'xml'
                elif file_path.endswith('.nt'): fmt = 'nt'
                
                self.rdf_manager.save_file(file_path, fmt)
                QMessageBox.information(self, "Success", f"Graph exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export: {e}")
    
    def toggle_theme(self):
        app = QApplication.instance()
        if self.dark_theme_action.isChecked():
            style_file = os.path.join(os.path.dirname(__file__), "styles", "dark_theme.qss")
            if os.path.exists(style_file):
                with open(style_file, "r") as f:
                    app.setStyleSheet(f.read())
            else:
                QMessageBox.warning(self, "Warning", f"Style file not found: {style_file}")
                self.settings_manager.set_dark_theme(False)
        else:
            app.setStyleSheet("")
            
        self.settings_manager.set_dark_theme(self.dark_theme_action.isChecked())
        self.settings_manager.save_settings()

    def closeEvent(self, event):
        self.graph_viewer.cleanup()
        event.accept()

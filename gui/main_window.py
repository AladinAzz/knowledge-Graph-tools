"""
Main Window Module

This module defines the main application window (MainWindow).
It orchestrates the UI layout, initializes core components (RDFManager, SPARQLEngine, etc.),
and handles high-level user interactions such as loading files and executing reasoning.
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTabWidget, 
                             QDockWidget, QFileDialog, QMessageBox, QMenu, QMenuBar, QApplication)
from PyQt6.QtCore import Qt
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

from core.settings_manager import SettingsManager

class MainWindow(QMainWindow):
    """
    The main window of the application.
    Integrates the graph viewer, query widget, ontology tree, and text-to-KG widget.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KB Manager")
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

    def init_ui(self):
        # Menu Bar
        self.create_menus()
        
        # Toolbar
        self.create_toolbar()
        
        # Central Area (Tabs for Graph & Query)
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.graph_viewer = GraphViewer()
        self.query_widget = QueryWidget(self.sparql_engine, self.settings_manager)
        self.text_kg_widget = TextKGWidget(self.rdf_manager, self.settings_manager)
        
        # Connect signals
        self.text_kg_widget.graph_merged.connect(self.refresh_graph_view)
        
        self.tabs.addTab(self.graph_viewer, "Graph Visualization")
        self.tabs.addTab(self.query_widget, "SPARQL Query")
        self.tabs.addTab(self.text_kg_widget, "Text to RDF")
        
        # Dock Widget for Ontology Tree
        self.dock = QDockWidget("Ontology Hierarchy", self)
        self.ontology_tree = OntologyTree()
        self.dock.setWidget(self.ontology_tree)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock)

    def refresh_graph_view(self):
        """Refreshes the main graph visualization and ontology tree."""
        self.graph_viewer.display_graph(self.rdf_manager.get_graph())
        self.refresh_ontology_from_graph()

    def refresh_ontology_from_graph(self):
        """
        Saves the current RDF graph to a temp file and re-loads the ontology hierarchy.
        This ensures the tree view stays in sync with merges/reasoning.
        """
        # If empty, clear tree
        if len(self.rdf_manager.get_graph()) == 0:
            self.ontology_tree.tree.clear()
            return
            
        try:
            # Create temp file
            fd, temp_path = tempfile.mkstemp(suffix=".owl")
            os.close(fd)
            
            # Temporary graph to augment with explicit class declarations
            # We don't want to modify the main graph, just the one we save for owlready2
            temp_graph = self.rdf_manager.get_graph() 
            # Note: simply assigning isn't a deep copy of triplets in rdflib if it's the same object
            # But we can just add triples to it and remove them later? 
            # Or better, serialize the main graph, parse into a new graph, augment, then save.
            # Or even simpler: Just iterate the main graph and find classes
            
            # Let's find all used classes and ensure they are typed as owl:Class in the saved file
            # We can do this by adding them to the graph before saving, but that modifies user data?
            # Yes. So we should copy or just accept that "inferring" class type is fine.
            # Actually, modifying the main graph to say "X is a Class" if "Y is a X" is usually a good thing.
            # But let's be safe and only do it for the export to owlready2.
            
            from rdflib import RDF, OWL
            
            # We must serialize to a file. 
            # Let's create a temporary in-memory graph to augment
            # Copying a large graph might be slow. 
            # Alternative: Add the triples, save, then remove them? 
            # Let's try adding them to the main graph. If it's a valid RDF inference, it should be fine.
            # "If S a O, then O is a Class/RDFS Class". 
            
            # Identify potential classes
            used_classes = set()
            for s, p, o in self.rdf_manager.get_graph().triples((None, RDF.type, None)):
                used_classes.add(o)
                
            # Add explicit declaration if missing
            added_triples = []
            for cls in used_classes:
                if (cls, RDF.type, OWL.Class) not in self.rdf_manager.get_graph():
                    self.rdf_manager.get_graph().add((cls, RDF.type, OWL.Class))
                    added_triples.append((cls, RDF.type, OWL.Class))
            
            # Save current graph (now with explicit classes)
            self.rdf_manager.save_file(temp_path, "xml")
            
            # Remove the temporary triples to keep main graph clean? 
            # Or keep them? Providing explicit typing is usually good.
            # The user asked to "refresh based on graph state". implicit -> explicit is a refresh.
            # But strict preservation of user input might be desired.
            # Let's remove them to be safe, so we don't pollute the graph with inferred axioms permanently here.
            for t in added_triples:
                self.rdf_manager.get_graph().remove(t)
            
            # Load into ontology manager (this updates its internal world)
            self.ontology_manager.load_ontology(temp_path)
            
            # Update Tree
            hierarchy = self.ontology_manager.get_hierarchy()
            self.ontology_tree.display_hierarchy(hierarchy)
            
            # Cleanup
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
        except Exception as e:
            # If it fails (e.g. invalid RDF for OWL), we just log/ignore or show warning
            # Depending on UX preference. For now, print to console/ignore to not annoy user on every merge
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
        
        # These now just alias to the toolbar logic or specific calls
        run_hermit_action = reasoning_menu.addAction("Run Reasoner (Hermit)")
        run_hermit_action.triggered.connect(lambda: self.run_reasoner('hermit'))
        
        run_pellet_action = reasoning_menu.addAction("Run Reasoner (Pellet)")
        run_pellet_action.triggered.connect(lambda: self.run_reasoner('pellet'))

        # Tools Menu
        tools_menu = menu_bar.addMenu("Tools")
        
        ns_action = tools_menu.addAction("Manage Namespaces")
        ns_action.triggered.connect(self.manage_namespaces)

    def manage_namespaces(self):
        from gui.widgets.namespace_dialog import NamespaceDialog
        dialog = NamespaceDialog(self.rdf_manager, self)
        dialog.exec()

    def create_toolbar(self):
        from PyQt6.QtWidgets import QToolBar, QLabel, QComboBox
        from PyQt6.QtGui import QAction, QIcon
        
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        # Reasoner Profile
        toolbar.addWidget(QLabel("  Reasoning Profile: "))
        self.reasoner_selector = QComboBox()
        self.reasoner_selector.addItems(["OWL DL (HermiT)", "OWL DL (Pellet)", "RDFS (via OWL DL)"])
        toolbar.addWidget(self.reasoner_selector)
        
        toolbar.addSeparator()
        
        run_reasoner_action = QAction("Run Reasoner", self)
        run_reasoner_action.setStatusTip("Run the selected reasoner on the active ontology")
        run_reasoner_action.triggered.connect(self.run_reasoner_from_toolbar)
        toolbar.addAction(run_reasoner_action)

    def run_reasoner_from_toolbar(self):
        profile = self.reasoner_selector.currentText()
        if "Pellet" in profile:
            self.run_reasoner('pellet')
        else:
            self.run_reasoner('hermit')

    def load_rdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open RDF File", "", 
                                                   "RDF Files (*.ttl *.xml *.rdf *.nt);;All Files (*)")
        if file_path:
            try:
                self.rdf_manager.load_file(file_path)
                self.graph_viewer.display_graph(self.rdf_manager.get_graph())
                
                # Also refresh ontology tree
                self.refresh_ontology_from_graph()
                
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
        
        # Clear ontology tree
        self.ontology_tree.tree.clear()
        
        QMessageBox.information(self, "Reset", "Graph cleared.")

    def run_reasoner(self, reasoner_type='hermit'):
        # Ensure there is data to reason upon
        if len(self.rdf_manager.get_graph()) == 0:
            QMessageBox.warning(self, "Warning", "The graph is empty. Please load data or an ontology first.")
            return

        # Show busy cursor
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        
        try:
            # Save current graph to temp file (RDF/XML is best for owlready2)
            # We use .owl extension for owlready2 to recognize it easily as potential ontology
            fd, temp_path = tempfile.mkstemp(suffix=".owl")
            os.close(fd)
            
            # Save the current graph to this temp file
            self.rdf_manager.save_file(temp_path, "xml")
            
            # Run reasoning on this temp file
            inferred_graph = self.reasoner_engine.run_reasoner(temp_path, reasoner_type=reasoner_type)
            
            # Merge inferred graph into main graph
            # We can calculate the difference to show what was added, or just update the view
            # Let's count new triples
            initial_count = len(self.rdf_manager.get_graph())
            self.rdf_manager.graph += inferred_graph
            final_count = len(self.rdf_manager.get_graph())
            new_triples = final_count - initial_count
            
            # Refresh View
            self.graph_viewer.display_graph(self.rdf_manager.get_graph())
            
            # Update Ontology Tree with inferred hierarchy
            self.refresh_ontology_from_graph()
            
            QApplication.restoreOverrideCursor()
            
            if new_triples > 0:
                QMessageBox.information(self, "Success", f"Reasoning ({reasoner_type}) complete.\nInferred {new_triples} new triples.")
            else:
                QMessageBox.information(self, "Success", f"Reasoning ({reasoner_type}) complete.\nNo new triples inferred.")
                
            # Cleanup temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
        except Exception as e:
            QApplication.restoreOverrideCursor()
            # Cleanup temp file in case of error
            if 'temp_path' in locals() and os.path.exists(temp_path):
                try: os.remove(temp_path)
                except: pass
                
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
            # Load Dark Theme
            style_file = os.path.join(os.path.dirname(__file__), "styles", "dark_theme.qss")
            if os.path.exists(style_file):
                with open(style_file, "r") as f:
                    app.setStyleSheet(f.read())
            else:
                QMessageBox.warning(self, "Warning", f"Style file not found: {style_file}")
                self.settings_manager.set_dark_theme(False)
        else:
            # Revert to default
            app.setStyleSheet("")
            
        # Save Setting
        self.settings_manager.set_dark_theme(self.dark_theme_action.isChecked())
        self.settings_manager.save_settings()

    def closeEvent(self, event):
        # Cleanup temp files
        self.graph_viewer.cleanup()
        event.accept()

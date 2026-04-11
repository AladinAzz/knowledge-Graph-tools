"""
Text to RDF Widget

This widget provides two tabs for converting text to RDF:
1. Gemini AI extraction - uses Google Gemini API for intelligent triple extraction
2. SpaCy NLP extraction - uses local SpaCy NLP for rule-based triple extraction

Both generate RDF graphs that can be visualized and merged into the main graph.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit, 
                             QPushButton, QLabel, QMessageBox, QTabWidget, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QLineEdit, QComboBox,
                             QFileDialog, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal
from rdflib import Graph
from core.gemini_extractor import GeminiExtractor
from .graph_viewer import GraphViewer

class TextKGWidget(QWidget):
    # Signal emitted when new triples are merged into the main graph
    graph_merged = pyqtSignal()

    def __init__(self, rdf_manager, settings_manager):
        super().__init__()
        self.rdf_manager = rdf_manager
        self.settings_manager = settings_manager
        self.extractor = GeminiExtractor() 
        self.spacy_extractor = None  # Lazy-loaded
        self.generated_graph = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Main tabs: Gemini vs SpaCy
        self.method_tabs = QTabWidget()
        layout.addWidget(self.method_tabs)
        
        # === Tab 1: Gemini Extraction ===
        gemini_widget = QWidget()
        gemini_layout = QVBoxLayout(gemini_widget)
        
        # Settings Area (API Key & Model)
        settings_layout = QHBoxLayout()
        settings_layout.addWidget(QLabel("API Key:"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("Enter Google Gemini API Key")
        self.api_key_input.setText(self.settings_manager.get_api_key())
        # BUG-13 fix: save on editing finished, not every keystroke
        self.api_key_input.editingFinished.connect(self.save_settings)
        settings_layout.addWidget(self.api_key_input)
        
        settings_layout.addWidget(QLabel("Model:"))
        self.model_selector = QComboBox()
        self.model_selector.setMinimumWidth(150)
        self.model_selector.addItems(["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"])
        self.model_selector.setCurrentText(self.settings_manager.get_model())
        self.model_selector.currentTextChanged.connect(self.save_settings)
        settings_layout.addWidget(self.model_selector)
        
        self.fetch_models_btn = QPushButton("Fetch Models")
        self.fetch_models_btn.setToolTip("Fetch available Gemini models using the API Key")
        self.fetch_models_btn.clicked.connect(self.fetch_models)
        settings_layout.addWidget(self.fetch_models_btn)
        
        gemini_layout.addLayout(settings_layout)
        
        # Text Input
        gemini_layout.addWidget(QLabel("Input Text for RDF Generation (Gemini AI):"))
        self.gemini_text_input = QPlainTextEdit()
        self.gemini_text_input.setPlaceholderText("Enter text here (e.g., 'Albert Einstein was born in Ulm.')...")
        gemini_layout.addWidget(self.gemini_text_input)
        
        # Action Buttons
        gemini_btn_layout = QHBoxLayout()
        self.gemini_generate_btn = QPushButton("Generate RDF (Gemini)")
        self.gemini_generate_btn.clicked.connect(self.generate_graph_gemini)
        gemini_btn_layout.addWidget(self.gemini_generate_btn)
        
        self.gemini_merge_btn = QPushButton("Merge to Main Graph")
        self.gemini_merge_btn.clicked.connect(self.add_to_main_graph)
        self.gemini_merge_btn.setEnabled(False)
        gemini_btn_layout.addWidget(self.gemini_merge_btn)
        gemini_layout.addLayout(gemini_btn_layout)
        
        # Results
        gemini_layout.addWidget(QLabel("Results:"))
        self.gemini_results_tabs = QTabWidget()
        gemini_layout.addWidget(self.gemini_results_tabs)
        
        self.gemini_table = QTableWidget()
        self.gemini_table.setColumnCount(3)
        self.gemini_table.setHorizontalHeaderLabels(["Subject", "Predicate", "Object"])
        self.gemini_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.gemini_results_tabs.addTab(self.gemini_table, "Table")
        
        self.gemini_graph_viewer = GraphViewer()
        self.gemini_results_tabs.addTab(self.gemini_graph_viewer, "Visualization")
        
        self.gemini_export_btn = QPushButton("Export RDF")
        self.gemini_export_btn.clicked.connect(self.export_rdf)
        self.gemini_export_btn.setEnabled(False)
        gemini_layout.addWidget(self.gemini_export_btn)
        
        self.method_tabs.addTab(gemini_widget, "🤖 Gemini AI")
        
        # === Tab 2: SpaCy Extraction ===
        spacy_widget = QWidget()
        spacy_layout = QVBoxLayout(spacy_widget)
        
        spacy_layout.addWidget(QLabel("Input Text for RDF Generation (SpaCy NLP):"))
        self.spacy_text_input = QPlainTextEdit()
        self.spacy_text_input.setPlaceholderText("Enter text here (e.g., 'Alice is a scientist. She lives in Paris.')...")
        spacy_layout.addWidget(self.spacy_text_input)
        
        spacy_btn_layout = QHBoxLayout()
        self.spacy_generate_btn = QPushButton("Generate RDF (SpaCy)")
        self.spacy_generate_btn.clicked.connect(self.generate_graph_spacy)
        spacy_btn_layout.addWidget(self.spacy_generate_btn)
        
        self.spacy_merge_btn = QPushButton("Merge to Main Graph")
        self.spacy_merge_btn.clicked.connect(self.add_to_main_graph)
        self.spacy_merge_btn.setEnabled(False)
        spacy_btn_layout.addWidget(self.spacy_merge_btn)
        spacy_layout.addLayout(spacy_btn_layout)
        
        spacy_layout.addWidget(QLabel("Results:"))
        self.spacy_results_tabs = QTabWidget()
        spacy_layout.addWidget(self.spacy_results_tabs)
        
        self.spacy_table = QTableWidget()
        self.spacy_table.setColumnCount(3)
        self.spacy_table.setHorizontalHeaderLabels(["Subject", "Predicate", "Object"])
        self.spacy_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.spacy_results_tabs.addTab(self.spacy_table, "Table")
        
        self.spacy_graph_viewer = GraphViewer()
        self.spacy_results_tabs.addTab(self.spacy_graph_viewer, "Visualization")
        
        self.spacy_export_btn = QPushButton("Export RDF")
        self.spacy_export_btn.clicked.connect(self.export_rdf)
        self.spacy_export_btn.setEnabled(False)
        spacy_layout.addWidget(self.spacy_export_btn)
        
        self.method_tabs.addTab(spacy_widget, "🧠 SpaCy NLP")
    
    def generate_graph_gemini(self):
        text = self.gemini_text_input.toPlainText()
        if not text:
            QMessageBox.warning(self, "Warning", "Please enter some text.")
            return

        api_key = self.api_key_input.text().strip()
        if not api_key:
             QMessageBox.warning(self, "Warning", "Please enter a valid Gemini API Key.")
             return
            
        model = self.model_selector.currentText()
        
        self.extractor.set_api_key(api_key)
        self.extractor.set_model(model)
            
        try:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            
            self.generated_graph = self.extractor.extract_triples(text)
            
            QApplication.restoreOverrideCursor()
            
            self._display_table(self.gemini_table, self.generated_graph)
            self.gemini_graph_viewer.display_graph(self.generated_graph)
            
            if len(self.generated_graph) > 0:
                self.gemini_merge_btn.setEnabled(True)
                self.gemini_export_btn.setEnabled(True)
                self.gemini_results_tabs.setCurrentIndex(1) 
                QMessageBox.information(self, "Success", f"Generated {len(self.generated_graph)} triples using {model}.")
            else:
                self.gemini_merge_btn.setEnabled(False)
                self.gemini_export_btn.setEnabled(False)
                QMessageBox.information(self, "Info", "No triples extracted or model returned empty results.")
                
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "Error", f"Extraction failed: {e}")

    def generate_graph_spacy(self):
        text = self.spacy_text_input.toPlainText()
        if not text:
            QMessageBox.warning(self, "Warning", "Please enter some text.")
            return
        
        try:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            
            # Lazy-load SpaCy extractor
            if self.spacy_extractor is None:
                from core.knowledge_extractor import KnowledgeExtractor
                self.spacy_extractor = KnowledgeExtractor()
            
            self.generated_graph = self.spacy_extractor.extract_triples(text)
            
            QApplication.restoreOverrideCursor()
            
            self._display_table(self.spacy_table, self.generated_graph)
            self.spacy_graph_viewer.display_graph(self.generated_graph)
            
            if len(self.generated_graph) > 0:
                self.spacy_merge_btn.setEnabled(True)
                self.spacy_export_btn.setEnabled(True)
                self.spacy_results_tabs.setCurrentIndex(1)
                QMessageBox.information(self, "Success", f"Generated {len(self.generated_graph)} triples using SpaCy NLP.")
            else:
                self.spacy_merge_btn.setEnabled(False)
                self.spacy_export_btn.setEnabled(False)
                QMessageBox.information(self, "Info", "No triples extracted. Try more explicit sentences with clear subject-verb-object structure.")
                
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "Error", f"SpaCy extraction failed: {e}")

    def _display_table(self, table, graph):
        table.setRowCount(len(graph))
        for row_idx, (s, p, o) in enumerate(graph):
            table.setItem(row_idx, 0, QTableWidgetItem(str(s)))
            table.setItem(row_idx, 1, QTableWidgetItem(str(p)))
            table.setItem(row_idx, 2, QTableWidgetItem(str(o)))

    def add_to_main_graph(self):
        if self.generated_graph:
            try:
                self.rdf_manager.graph += self.generated_graph
                QMessageBox.information(self, "Success", "Added extracted triples to the main graph.")
                self.gemini_merge_btn.setEnabled(False)
                self.spacy_merge_btn.setEnabled(False)
                
                self.graph_merged.emit()
                
            except Exception as e:
                 QMessageBox.critical(self, "Error", f"Failed to add to main graph: {e}")

    def export_rdf(self):
        if not self.generated_graph:
            return
            
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

    def fetch_models(self):
        api_key = self.api_key_input.text().strip()
        if not api_key:
             QMessageBox.warning(self, "Warning", "Please enter a valid Gemini API Key first.")
             return
             
        try:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            
            self.extractor.set_api_key(api_key)
            models = self.extractor.list_models()
            
            self.model_selector.clear()
            self.model_selector.addItems(models)
            
            QApplication.restoreOverrideCursor()
            QMessageBox.information(self, "Success", f"Fetched {len(models)} models.")
            
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "Error", f"Failed to list models: {e}")

    def save_settings(self):
        self.settings_manager.set_api_key(self.api_key_input.text().strip())
        self.settings_manager.set_model(self.model_selector.currentText())
        self.settings_manager.save_settings()

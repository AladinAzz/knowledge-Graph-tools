"""
Inferred Triples Dialog

A dialog that displays only the newly inferred triples after a reasoning operation.
Allows the user to inspect and export the inferred triples separately.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QLabel, QHeaderView,
                             QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt


class InferredTriplesDialog(QDialog):
    """Dialog showing inferred triples from reasoning."""
    
    def __init__(self, inferred_graph, elapsed_seconds=0, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Inferred Triples")
        self.resize(800, 500)
        self.inferred_graph = inferred_graph
        self.elapsed = elapsed_seconds
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Summary
        count = len(self.inferred_graph) if self.inferred_graph else 0
        summary = QLabel(f"Reasoning completed in {self.elapsed:.3f}s — {count} new triple(s) inferred.")
        summary.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(summary)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Subject", "Predicate", "Object"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)
        
        # Populate table
        if self.inferred_graph and len(self.inferred_graph) > 0:
            triples = list(self.inferred_graph)
            self.table.setRowCount(len(triples))
            for row_idx, (s, p, o) in enumerate(triples):
                self.table.setItem(row_idx, 0, QTableWidgetItem(str(s)))
                self.table.setItem(row_idx, 1, QTableWidgetItem(str(p)))
                self.table.setItem(row_idx, 2, QTableWidgetItem(str(o)))
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.export_btn = QPushButton("Export Inferred Triples")
        self.export_btn.clicked.connect(self.export_inferred)
        self.export_btn.setEnabled(count > 0)
        btn_layout.addWidget(self.export_btn)
        
        btn_layout.addStretch()
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.close_btn)
        
        layout.addLayout(btn_layout)
    
    def export_inferred(self):
        """Export only the inferred triples to a file."""
        if not self.inferred_graph:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Inferred Triples", "",
            "Turtle (*.ttl);;RDF/XML (*.rdf *.xml);;N-Triples (*.nt)"
        )
        if file_path:
            try:
                fmt = 'turtle'
                if file_path.endswith('.xml') or file_path.endswith('.rdf'):
                    fmt = 'xml'
                elif file_path.endswith('.nt'):
                    fmt = 'nt'
                
                self.inferred_graph.serialize(destination=file_path, format=fmt)
                QMessageBox.information(self, "Success", f"Inferred triples exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export: {e}")

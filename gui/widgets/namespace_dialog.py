"""
Namespace Management Dialog

This module provides a dialog for viewing and editing RDF namespace prefixes.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QLabel, QHeaderView, 
                             QLineEdit, QMessageBox)
from PyQt6.QtCore import Qt

class NamespaceDialog(QDialog):
    def __init__(self, rdf_manager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Namespaces")
        self.resize(600, 400)
        self.rdf_manager = rdf_manager
        
        self.init_ui()
        self.load_namespaces()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Prefix", "URI"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)
        
        # Add New Area
        add_layout = QHBoxLayout()
        add_layout.addWidget(QLabel("Prefix:"))
        self.prefix_input = QLineEdit()
        self.prefix_input.setPlaceholderText("ex")
        add_layout.addWidget(self.prefix_input)
        
        add_layout.addWidget(QLabel("URI:"))
        self.uri_input = QLineEdit()
        self.uri_input.setPlaceholderText("http://example.org/")
        add_layout.addWidget(self.uri_input)
        
        self.add_btn = QPushButton("Bind/Update")
        self.add_btn.clicked.connect(self.add_namespace)
        add_layout.addWidget(self.add_btn)
        
        layout.addLayout(add_layout)
        
        # Action Buttons
        btn_layout = QHBoxLayout()
        self.remove_btn = QPushButton("Remove Selected")
        self.remove_btn.clicked.connect(self.remove_namespace)
        btn_layout.addWidget(self.remove_btn)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.close_btn)
        
        layout.addLayout(btn_layout)

    def load_namespaces(self):
        self.table.setRowCount(0)
        namespaces = self.rdf_manager.get_namespaces()
        # Sort by prefix
        namespaces.sort(key=lambda x: x[0])
        
        self.table.setRowCount(len(namespaces))
        for row_idx, (prefix, uri) in enumerate(namespaces):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(prefix)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(uri)))

    def add_namespace(self):
        prefix = self.prefix_input.text().strip()
        uri = self.uri_input.text().strip()
        
        if not prefix or not uri:
            QMessageBox.warning(self, "Warning", "Prefix and URI are required.")
            return
            
        try:
            # Bind
            from rdflib import URIRef
            self.rdf_manager.bind_namespace(prefix, URIRef(uri))
            
            # Reload
            self.load_namespaces()
            self.prefix_input.clear()
            self.uri_input.clear()
            
            QMessageBox.information(self, "Success", f"Bound {prefix} to {uri}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to bind namespace: {e}")

    def remove_namespace(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Warning", "Please select a namespace to remove.")
            return
            
        # Get prefix from first column
        row = selected[0].row()
        prefix = self.table.item(row, 0).text()
        
        try:
            self.rdf_manager.remove_namespace(prefix)
            self.load_namespaces()
        except Exception as e:
             QMessageBox.critical(self, "Error", f"Failed to remove namespace: {e}")

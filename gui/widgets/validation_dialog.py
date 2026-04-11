"""
Ontology Validation Dialog

A dialog that displays ontology validation results with severity-based icons.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem,
                             QPushButton, QLabel, QHeaderView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


class ValidationDialog(QDialog):
    """Dialog showing ontology validation results."""
    
    SEVERITY_ICONS = {
        "error": "❌",
        "warning": "⚠️",
        "info": "ℹ️",
    }
    
    SEVERITY_COLORS = {
        "error": QColor(255, 100, 100),
        "warning": QColor(255, 200, 100),
        "info": QColor(100, 200, 255),
    }
    
    def __init__(self, results, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ontology Validation Results")
        self.resize(700, 450)
        self.results = results
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Summary counts
        errors = sum(1 for r in self.results if r["severity"] == "error")
        warnings = sum(1 for r in self.results if r["severity"] == "warning")
        infos = sum(1 for r in self.results if r["severity"] == "info")
        
        summary = QLabel(f"❌ {errors} Error(s)   ⚠️ {warnings} Warning(s)   ℹ️ {infos} Info(s)")
        summary.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(summary)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Severity", "Message"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # Sort: errors first, then warnings, then info
        sorted_results = sorted(self.results, key=lambda r: {"error": 0, "warning": 1, "info": 2}.get(r["severity"], 3))
        
        self.table.setRowCount(len(sorted_results))
        for row_idx, result in enumerate(sorted_results):
            severity = result["severity"]
            icon = self.SEVERITY_ICONS.get(severity, "")
            
            severity_item = QTableWidgetItem(f"{icon} {severity.upper()}")
            severity_item.setFlags(severity_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            
            message_item = QTableWidgetItem(result["message"])
            message_item.setFlags(message_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            
            self.table.setItem(row_idx, 0, severity_item)
            self.table.setItem(row_idx, 1, message_item)
        
        layout.addWidget(self.table)
        
        # Close button
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        layout.addWidget(self.close_btn)

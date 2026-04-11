"""
Graph Statistics Widget

Displays real-time statistics about the loaded RDF graph:
number of triples, subjects, predicates, objects, and classes.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox, QFormLayout
from PyQt6.QtCore import Qt


class StatsWidget(QWidget):
    """A widget that displays graph statistics in a compact panel."""
    
    def __init__(self, rdf_manager):
        super().__init__()
        self.rdf_manager = rdf_manager
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Title
        title = QLabel("Graph Statistics")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # Stats Group
        group = QGroupBox()
        form = QFormLayout(group)
        
        self.triples_label = QLabel("0")
        self.subjects_label = QLabel("0")
        self.predicates_label = QLabel("0")
        self.objects_label = QLabel("0")
        self.classes_label = QLabel("0")
        
        form.addRow("Triples:", self.triples_label)
        form.addRow("Subjects:", self.subjects_label)
        form.addRow("Predicates:", self.predicates_label)
        form.addRow("Objects:", self.objects_label)
        form.addRow("Classes:", self.classes_label)
        
        layout.addWidget(group)
        layout.addStretch()
    
    def update_stats(self):
        """Refreshes the statistics from the RDF manager."""
        stats = self.rdf_manager.get_statistics()
        self.triples_label.setText(str(stats.get("num_triples", 0)))
        self.subjects_label.setText(str(stats.get("num_subjects", 0)))
        self.predicates_label.setText(str(stats.get("num_predicates", 0)))
        self.objects_label.setText(str(stats.get("num_objects", 0)))
        self.classes_label.setText(str(stats.get("num_classes", 0)))
    
    def clear_stats(self):
        """Resets all statistics to 0."""
        self.triples_label.setText("0")
        self.subjects_label.setText("0")
        self.predicates_label.setText("0")
        self.objects_label.setText("0")
        self.classes_label.setText("0")

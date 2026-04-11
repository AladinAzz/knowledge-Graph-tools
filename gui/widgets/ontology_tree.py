"""
Ontology Tree Widget

This module provides the OntologyTree widget, which displays the class hierarchy
and properties of an ontology in a tabbed tree structure.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
                             QLabel, QTabWidget)


class OntologyTree(QWidget):
    """
    A widget that displays the ontology class hierarchy and properties in tree views.
    """
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(QLabel("Ontology Structure"))
        
        # Tabs for Classes and Properties
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        # Tab 1: Class Hierarchy
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Class", "IRI"])
        self.tabs.addTab(self.tree, "Classes")
        
        # Tab 2: Properties
        self.props_tree = QTreeWidget()
        self.props_tree.setHeaderLabels(["Property", "Type", "Domain", "Range"])
        self.tabs.addTab(self.props_tree, "Properties")

    def display_hierarchy(self, hierarchy_data):
        """
        Populates the tree with the hierarchy data.
        hierarchy_data: dict returned by OntologyManager.get_hierarchy()
        """
        self.tree.clear()
        if not hierarchy_data:
            return

        # hierarchy_data is a single root dict (usually Thing)
        root_item = QTreeWidgetItem(self.tree)
        self._populate_item(root_item, hierarchy_data)
        self.tree.expandAll()

    def _populate_item(self, item, data):
        item.setText(0, str(data.get("name", "Unknown")))
        item.setText(1, str(data.get("iri", "")))
        
        children = data.get("children", [])
        for child_data in children:
            child_item = QTreeWidgetItem(item)
            self._populate_item(child_item, child_data)
    
    def display_properties(self, properties_info):
        """
        Populates the properties tree.
        properties_info: list of dicts from OntologyManager.get_properties_info()
        """
        self.props_tree.clear()
        if not properties_info:
            return
        
        # Group by type
        obj_props = [p for p in properties_info if p["type"] == "ObjectProperty"]
        data_props = [p for p in properties_info if p["type"] == "DataProperty"]
        other_props = [p for p in properties_info if p["type"] not in ("ObjectProperty", "DataProperty")]
        
        # Object Properties
        if obj_props:
            obj_root = QTreeWidgetItem(self.props_tree)
            obj_root.setText(0, f"Object Properties ({len(obj_props)})")
            obj_root.setText(1, "ObjectProperty")
            for prop in obj_props:
                item = QTreeWidgetItem(obj_root)
                item.setText(0, prop["name"])
                item.setText(1, prop["type"])
                item.setText(2, ", ".join(prop.get("domain", [])) or "—")
                item.setText(3, ", ".join(prop.get("range", [])) or "—")
        
        # Data Properties
        if data_props:
            data_root = QTreeWidgetItem(self.props_tree)
            data_root.setText(0, f"Data Properties ({len(data_props)})")
            data_root.setText(1, "DataProperty")
            for prop in data_props:
                item = QTreeWidgetItem(data_root)
                item.setText(0, prop["name"])
                item.setText(1, prop["type"])
                item.setText(2, ", ".join(prop.get("domain", [])) or "—")
                item.setText(3, ", ".join(prop.get("range", [])) or "—")
        
        # Other Properties
        if other_props:
            other_root = QTreeWidgetItem(self.props_tree)
            other_root.setText(0, f"Other Properties ({len(other_props)})")
            for prop in other_props:
                item = QTreeWidgetItem(other_root)
                item.setText(0, prop["name"])
                item.setText(1, prop["type"])
                item.setText(2, ", ".join(prop.get("domain", [])) or "—")
                item.setText(3, ", ".join(prop.get("range", [])) or "—")
        
        self.props_tree.expandAll()

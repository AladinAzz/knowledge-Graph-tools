from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QLabel

class OntologyTree(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(QLabel("Class Hierarchy"))
        
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Class", "IRI"])
        self.layout.addWidget(self.tree)

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

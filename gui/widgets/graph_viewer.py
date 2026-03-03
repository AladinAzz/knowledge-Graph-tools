"""
Graph Viewer Widget

This module provides the GraphViewer widget, which embeds a PyVis network visualization
inside a PyQt6 QWebEngineView. It handles converting rdflib graphs to interactive HTML visualizations.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
from pyvis.network import Network
import tempfile
import os

from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWebEngineCore import QWebEnginePage

class GraphWebPage(QWebEnginePage):
    """
    Custom WebEnginePage to intercept navigation requests and open URLs in the system browser.
    """
    def __init__(self, viewer):
        super().__init__(viewer.web_view)
        self.viewer = viewer

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        # Check if it's a clicked link or explicit navigation to an external site
        scheme = url.scheme()
        url_str = url.toString()
        
        if scheme == 'cmd':
            if url_str.startswith("cmd://select/"):
                node_id = url_str.replace("cmd://select/", "")
                self.viewer.selected_node_id = node_id
                self.viewer.remove_btn.setEnabled(True)
                return False
            elif url_str == "cmd://deselect":
                self.viewer.selected_node_id = None
                self.viewer.remove_btn.setEnabled(False)
                return False
        
        if scheme in ['http', 'https']:
            QDesktopServices.openUrl(url)
            return False # Prevent loading in the widget
            
        return super().acceptNavigationRequest(url, _type, isMainFrame)

class GraphViewer(QWidget):
    """
    A widget for displaying interactive force-directed graphs using PyVis and QWebEngineView.
    """
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        
        # Layout Selector
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(QLabel("Layout:"))
        self.layout_selector = QComboBox()
        self.layout_selector.addItems(["Force Directed", "Hierarchical", "Barnes Hut"])
        self.layout_selector.currentIndexChanged.connect(self.update_layout)
        controls_layout.addWidget(self.layout_selector)
        
        from PyQt6.QtWidgets import QPushButton
        self.remove_btn = QPushButton("Remove Selected Node")
        self.remove_btn.setEnabled(False)
        self.remove_btn.clicked.connect(self.remove_selected_node)
        controls_layout.addWidget(self.remove_btn)
        
        controls_layout.addStretch()
        self.layout.addLayout(controls_layout)

        self.web_view = QWebEngineView()
        # Set custom page to handle navigation
        self.web_page = GraphWebPage(self)
        self.web_view.setPage(self.web_page)
        self.layout.addWidget(self.web_view)
        
        self.current_graph = None
        self.tmp_file = None
        self.selected_node_id = None

    def update_layout(self):
        if self.current_graph:
            self.display_graph(self.current_graph)
            
    def remove_selected_node(self):
        if self.selected_node_id and self.current_graph:
            from rdflib import URIRef
            node_uri = URIRef(self.selected_node_id)
            
            # Remove all triples where node is subject or object
            self.current_graph.remove((node_uri, None, None))
            self.current_graph.remove((None, None, node_uri))
            
            # Refresh view
            self.display_graph(self.current_graph)
            
            # Reset selection
            self.selected_node_id = None
            self.remove_btn.setEnabled(False)

    def display_graph(self, rdflib_graph):
        """
        Converts rdflib graph to PyVis network and displays it.
        """
        self.current_graph = rdflib_graph
        # Use in_line resources to embed vis.js directly in the HTML
        # This fixes 'vis is not defined' when loading from temp file in QWebEngineView
        net = Network(height="100%", width="100%", bgcolor="#222222", font_color="white", cdn_resources="in_line")
        
        # Apply Layout Options
        layout_mode = self.layout_selector.currentText()
        if layout_mode == "Hierarchical":
            net.hrepulsion()
            net.set_options("""
            var options = {
              "layout": {
                "hierarchical": {
                  "enabled": true,
                  "direction": "UD",
                  "sortMethod": "directed"
                }
              },
              "physics": {
                "hierarchicalRepulsion": {
                  "nodeDistance": 150
                }
              }
            }
            """)
        elif layout_mode == "Barnes Hut":
            net.barnes_hut()
        else:
            # Default Force Directed (ForceAtlas2 is usually good)
            net.force_atlas_2based()

        # Limit nodes for performance if graph is large
        max_nodes = 500
        count = 0
        
        for s, p, o in rdflib_graph:
            if count > max_nodes:
                break
                
            s_str = str(s)
            o_str = str(o)
            p_str = str(p)
            
            # Add nodes
            # Simple heuristic for labels: last part of URI
            s_label = s_str.split('/')[-1].split('#')[-1]
            o_label = o_str.split('/')[-1].split('#')[-1]
            
            # Use URI as title (tooltip) AND id
            net.add_node(s_str, label=s_label, title=s_str, color="#97C2FC")
            net.add_node(o_str, label=o_label, title=o_str, color="#FB7E81")
            
            # Add edge
            net.add_edge(s_str, o_str, title=p_str, label=p_str.split('/')[-1].split('#')[-1])
            count += 1
            
        # Use temp file to load into QWebEngineView
        fd, path = tempfile.mkstemp(suffix=".html")
        os.close(fd)
        
        # PyVis save_graph uses default encoding (cp1252 on Windows) which fails with unicode chars.
        # We generate the HTML string and write it manually with utf-8.
        html = net.generate_html()
        
        # 1. Ensure 'network' variable is accessible globally so we can attach events
        # PyVis often declares 'var network = ...'. We change it to 'window.network = ...' 
        # or just hope it's global. Replacing 'var network' with 'window.network' is safer.
        html = html.replace("var network = ", "window.network = ")
        
        # 2. Inject JS Event Listeners
        # logic:
        # - click/selectNode: Selects the node (notify Python to enable remove button)
        # - doubleClick: Opens URI
        js_handler = """
        <script type="text/javascript">
            // Wait for network to be ready
            setTimeout(function() {
                if (typeof window.network !== 'undefined') {
                    
                    // Handle Selection (Single Click / Select)
                    window.network.on("selectNode", function (params) {
                        if (params.nodes.length > 0) {
                            var nodeId = params.nodes[0];
                            // Navigate to special CMD url to notify Python
                            window.location.href = "cmd://select/" + nodeId;
                        }
                    });
                    
                    // Handle Deselection
                    window.network.on("deselectNode", function (params) {
                         window.location.href = "cmd://deselect";
                    });

                    // Handle Double Click (Open URI)
                    window.network.on("doubleClick", function (params) {
                        if (params.nodes.length > 0) {
                            var nodeId = params.nodes[0];
                            // Check if it's a valid http/https URI
                            if (nodeId.startsWith("http://") || nodeId.startsWith("https://")) {
                                // Navigate to it - this will be intercepted by Python
                                window.location.href = nodeId;
                            }
                        }
                    });
                    
                } else {
                    console.log("Error: window.network not found for click handler.");
                }
            }, 500); // Small delay to ensure init
        </script>
        """
        
        html = html.replace('</body>', js_handler + '</body>')
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
            
        self.tmp_file = path
        self.web_view.setUrl(QUrl.fromLocalFile(path))

    def cleanup(self):
        if self.tmp_file and os.path.exists(self.tmp_file):
            try:
                os.remove(self.tmp_file)
            except:
                pass

from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
from pyvis.network import Network
import tempfile
import os

class GraphViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.web_view = QWebEngineView()
        self.layout.addWidget(self.web_view)
        self.current_graph = None
        self.tmp_file = None

    def display_graph(self, rdflib_graph):
        """
        Converts rdflib graph to PyVis network and displays it.
        """
        self.current_graph = rdflib_graph
        # Use in_line resources to embed vis.js directly in the HTML
        # This fixes 'vis is not defined' when loading from temp file in QWebEngineView
        net = Network(height="100%", width="100%", bgcolor="#222222", font_color="white", cdn_resources="in_line")
        
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
            
            net.add_node(s_str, label=s_label, title=s_str, color="#97C2FC")
            net.add_node(o_str, label=o_label, title=o_str, color="#FB7E81")
            
            # Add edge
            net.add_edge(s_str, o_str, title=p_str, label=p_str.split('/')[-1].split('#')[-1])
            count += 1
            
        net.toggle_physics(True)
        # Use temp file to load into QWebEngineView
        fd, path = tempfile.mkstemp(suffix=".html")
        os.close(fd)
        
        # PyVis save_graph uses default encoding (cp1252 on Windows) which fails with unicode chars.
        # We generate the HTML string and write it manually with utf-8.
        html = net.generate_html()
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

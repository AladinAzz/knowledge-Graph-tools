from pyvis.network import Network
import os

try:
    net = Network(cdn_resources="in_line")
    net.add_node(1, label="Test")
    net.write_html("test_vis.html")
    
    with open("test_vis.html", "r", encoding="utf-8") as f:
        content = f.read()
        
    if "vis.js" in content or "vis-network.min.js" in content:
        print("SUCCESS: Vis.js found in HTML (inline or refereced)")
    else:
        print("WARNING: Vis.js not clearly found in HTML")
        
    # Check if file size is substantial (inline JS is large)
    size = os.path.getsize("test_vis.html")
    print(f"File size: {size} bytes")
    if size > 100000:
        print("SUCCESS: File size suggests inline JS")
    else:
        print("FAILURE: File too small for inline JS")
        
    os.remove("test_vis.html")
    
except Exception as e:
    print(f"Error: {e}")

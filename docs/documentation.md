# Knowledge Base Management System - User Manual

## Overview
A desktop application for managing Knowledge Bases (RDF/OWL). 
Features include RDF loading, Ontology visualization, SPARQL querying, and Reasoning.

## Installation
1. Ensure Python 3.10+ is installed.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. (Optional) For Reasoning, ensure Java is installed (for HermiT/Pellet).

## Running the Application
### Option A: Using the Batch Script (Recommended)
Double-click `run.bat` in the project folder.

### Option B: Using Python directly
Open a terminal in the project folder and run:
```bash
python app.py
```

### Option C: Standalone Executable
If built successfully, run `dist/KBManager.exe`.

## Features
### 1. File Management
- **Load RDF Graph**: Load Turtle (`.ttl`), RDF/XML (`.rdf`, `.xml`), or N-Triples (`.nt`) files.
- **Load Ontology**: Load OWL ontologies (`.owl`). This populates the Class Hierarchy view.
- **Export Graph**: Save the current graph to a file.

### 2. Visualization
- **Graph Visualization Tab**: Interactive graph view (Zoom, Pan, Drag nodes).
- **Ontology Hierarchy**: Left panel shows the class structure of loaded ontologies.

### 3. SPARQL Query
- Go to the **SPARQL Query** tab.
- Enter your query (SELECT, ASK, CONSTRUCT).
- Click **Execute Query**.
- **Tabular Results**: Shown in the "Table" tab.
- **Graph Results**: Shown in the "Visualization" tab. 
  - For `CONSTRUCT`/`DESCRIBE`: The full result graph is shown.
  - For `SELECT`: If the query returns exactly 3 variables (e.g., `?s ?p ?o`), the application attempts to visualize them as a graph.
- Click **Export Results** to save as CSV or JSON.

### 6. Text to RDF
- Go to the **Text to RDF** tab.
- Enter English text.
- Click **Generate RDF**.
- **Table Tab**: View extracted triples.
- **Visualization Tab**: View the graph.
- Click **Export RDF** to save the generated graph to a file.
- Click **Merge to Main Graph** to add to your current workspace. 
  - For `CONSTRUCT`/`DESCRIBE`: The full result graph is shown.
  - For `SELECT`: If the query returns exactly 3 variables (e.g., `?s ?p ?o`), the application attempts to visualize them as a graph.
- Click **Export Results** to save as CSV or JSON.

### 4. Reasoning
- Menu **Reasoning** -> **Run Reasoner (HermiT)** or **(Pellet)**.
- Select an ontology file to apply reasoning rules.
- Inferred triples (e.g., subclass relationships, transitivity) will be added to the graph.

## Troubleshooting
- **Reasoner fails?** Ensure Java is installed and accessible in your system PATH.
- **Graph too large?** The visualization limits nodes to 500 for performance. Use SPARQL to explore specific parts.

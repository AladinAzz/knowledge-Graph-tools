# Knowledge Graph Manager — Documentation Technique

## 1. Vue d'ensemble du Projet

**Knowledge Graph Manager** est une application de bureau construite avec Python et PyQt6 permettant de :

- Charger, visualiser et manipuler des graphes RDF et des ontologies OWL.
- Interroger les données via SPARQL (SELECT, CONSTRUCT, ASK, DESCRIBE, INSERT, DELETE).
- Extraire automatiquement des triplets RDF à partir de texte libre grâce au NLP (SpaCy) et à l'IA générative (Google Gemini).
- Exécuter du raisonnement automatisé (HermiT / Pellet) pour inférer de nouveaux faits.
- Valider la cohérence logique d'une ontologie.
- Gérer les espaces de noms, exporter les résultats, et naviguer visuellement dans les classes et propriétés.

L'application peut être compilée en un exécutable Windows autonome via PyInstaller, et distribuée via un installateur Inno Setup.

---

## 2. Architecture du Projet

```
knowledge-Graph-tools/
│
├── app.py                          # Point d'entrée principal
├── requirements.txt                # Dépendances de production
├── requirements-dev.txt            # Dépendances de développement
├── .env                            # Clé API (Gemini)
├── settings.xml                    # Paramètres persistants de l'application
├── run.bat                         # Script de lancement rapide
├── build_executable.bat            # Script de compilation PyInstaller
├── build_installer.iss             # Script Inno Setup (installateur Windows)
├── Knowledge Graph Manager.spec    # Configuration PyInstaller générée
├── icon.ico                        # Icône de l'application
├── example.ttl                     # Fichier Turtle d'exemple
├── test_ontology.owl               # Ontologie d'exemple pour tests
├── test_ontology.rdf               # Même ontologie en format RDF/XML
├── ontology.owl                    # Ontologie de travail principale
├── .gitignore                      # Fichiers exclus du contrôle de version
├── SCENARIO_VIDEO.md               # Scénario de démonstration vidéo
│
├── core/                           # Logique métier (backend)
│   ├── __init__.py
│   ├── rdf_manager.py              # Gestion du graphe RDF (rdflib)
│   ├── sparql_engine.py            # Moteur d'exécution SPARQL
│   ├── ontology_manager.py         # Chargement et inspection d'ontologies (owlready2)
│   ├── ontology_validator.py       # Validation de cohérence d'ontologies
│   ├── reasoner.py                 # Moteur de raisonnement (HermiT/Pellet)
│   ├── knowledge_extractor.py      # Extraction de triplets via SpaCy NLP
│   ├── gemini_extractor.py         # Extraction de triplets via Google Gemini API
│   └── settings_manager.py         # Gestion des paramètres (XML + .env)
│
├── gui/                            # Interface graphique (frontend)
│   ├── __init__.py
│   ├── main_window.py              # Fenêtre principale de l'application
│   ├── styles/
│   │   └── dark_theme.qss          # Feuille de style sombre (QSS)
│   ├── utils/
│   │   ├── syntax_highlighter.py   # Coloration syntaxique SPARQL
│   │   └── sparql_completer.py     # Auto-complétion SPARQL
│   └── widgets/
│       ├── __init__.py
│       ├── graph_viewer.py         # Visualisation de graphe interactive (PyVis)
│       ├── query_widget.py         # Interface complète pour les requêtes SPARQL
│       ├── text_kg_widget.py       # Conversion texte → RDF (Gemini + SpaCy)
│       ├── ontology_tree.py        # Arbre hiérarchique des classes/propriétés
│       ├── stats_widget.py         # Panneau de statistiques du graphe
│       ├── namespace_dialog.py     # Dialogue de gestion des préfixes
│       ├── validation_dialog.py    # Dialogue de résultats de validation
│       └── inferred_triples_dialog.py  # Dialogue des triplets inférés
│
├── lib/                            # Bibliothèques externes embarquées
│   ├── bindings/
│   │   └── utils.js                # Utilitaires JS de PyVis (highlighting, filtrage)
│   ├── tom-select/                 # Bibliothèque CSS/JS Tom Select (sélecteurs)
│   └── vis-9.1.2/                  # Vis.js v9.1.2 (visualisation de réseau)
│
├── data/                           # Données de test et exemples
│   ├── dev.ttl                     # Données Turtle de développement
│   ├── test.ttl                    # Données Turtle de test
│   ├── examples/                   # Ontologies d'exemple (pizza.owl, etc.)
│   └── reasoners/                  # Données de test pour le raisonnement
│
├── scripts/                        # Scripts utilitaires de débogage
│   ├── debug_extraction.py         # Débogage de l'extraction NLP
│   ├── debug_reasoner.py           # Débogage du moteur de raisonnement
│   └── verify_pyvis.py             # Vérification du fonctionnement de PyVis
│
├── tests/                          # Tests unitaires (pytest)
│   ├── test_rdf_manager.py
│   ├── test_sparql_engine.py
│   ├── test_ontology_manager.py
│   ├── test_reasoner.py
│   ├── test_knowledge_extractor.py
│   ├── test_gemini_ui.py
│   ├── test_graph_interaction.py
│   ├── test_new_features.py
│   ├── test_ontology_refresh.py
│   ├── test_reasoning_ui.py
│   ├── test_settings_persistence.py
│   ├── test_namespace_manager.py
│   ├── test_syntax_highlighter.py
│   ├── test_theme.py
│   ├── t.rdf                       # Données RDF de test
│   └── t.ttl                       # Données Turtle de test
│
├── build/                          # Artéfacts de compilation (généré)
├── dist/                           # Exécutable compilé (généré)
├── Installateur/                   # Installateur Windows (généré)
│   └── Knowledge_Graph_Manager_Setup.exe
├── .venv/                          # Environnement virtuel Python
└── venv/                           # Environnement virtuel alternatif
```

---

## 3. Description Détaillée Fichier par Fichier

### 3.1 Fichiers Racine

#### `app.py` — Point d'entrée

Le point d'entrée principal de l'application. Il initialise `QApplication` (PyQt6), instancie la `MainWindow`, et lance la boucle d'événements. Ce fichier est volontairement minimaliste pour séparer clairement le lancement de la logique applicative.

#### `requirements.txt` — Dépendances de production

Déclare toutes les bibliothèques Python nécessaires à l'exécution :

| Dépendance | Version | Rôle |
|---|---|---|
| `PyQt6` | ≥6.5, <7 | Framework GUI de bureau |
| `PyQt6-WebEngine` | ≥6.5, <7 | Moteur de rendu web intégré (pour les graphes PyVis) |
| `rdflib` | ≥6.3 | Manipulation de graphes RDF (parsing, sérialisation, SPARQL) |
| `owlready2` | ≥0.45 | Chargement d'ontologies OWL, raisonnement (HermiT/Pellet) |
| `pyvis` | ≥0.3 | Génération de visualisations de réseau interactives (HTML/Vis.js) |
| `networkx` | ≥3.0 | Dépendance de PyVis pour la structure de graphe |
| `spacy` | ≥3.5 | Pipeline NLP pour l'extraction de connaissances |
| `spacy-lookups-data` | — | Données de lookup pour SpaCy (lemmatisation, etc.) |
| `google-generativeai` | ≥0.3 | SDK de l'API Google Gemini |
| `python-dotenv` | ≥1.0 | Chargement de variables d'environnement depuis `.env` |

#### `requirements-dev.txt` — Dépendances de développement

Outils nécessaires uniquement pour le développement et la compilation :
- `pyinstaller` ≥6.0 — Compilation en exécutable Windows.
- `pytest` ≥7.0 — Exécution des tests unitaires.

#### `.env` — Variables d'environnement

Stocke la clé API Google Gemini (`GEMINI_API_KEY`). Ce fichier est exclu du contrôle de version (`.gitignore`) pour des raisons de sécurité. Il est chargé automatiquement au démarrage via `python-dotenv`.

#### `settings.xml` — Paramètres persistants

Fichier XML qui persiste les préférences utilisateur :
- Modèle Gemini sélectionné
- Thème sombre activé/désactivé
- Profil de raisonnement (HermiT/Pellet)
- Historique des requêtes SPARQL

Ce fichier est également exclu du `.gitignore` car il contient des préférences locales.

#### `run.bat` — Lancement rapide

Script batch Windows qui détecte la présence d'un environnement virtuel (`.venv`) et lance l'application avec le bon interpréteur Python. Cela simplifie l'expérience utilisateur : un double-clic suffit pour lancer l'application.

#### `build_executable.bat` — Script de compilation

Automatise la compilation avec PyInstaller. Il :
1. Installe `pyinstaller` dans le venv si absent.
2. Exécute PyInstaller avec les options nécessaires (`--windowed`, `--collect-all`, `--hidden-import`).
3. Intègre les styles QSS, les modèles SpaCy, et les fichiers internes de owlready2, pyvis et rdflib.

#### `build_installer.iss` — Script Inno Setup

Configuration de l'installateur Windows. Il :
- Copie le contenu de `dist/Knowledge Graph Manager/` vers `Program Files`.
- Crée des raccourcis menu démarrer et bureau.
- Permet le lancement optionnel après installation.
- Génère un fichier `Knowledge_Graph_Manager_Setup.exe` dans le dossier `Installateur/`.

#### `Knowledge Graph Manager.spec` — Configuration PyInstaller

Fichier de spécification généré par PyInstaller, personnalisé pour inclure :
- Les fichiers de données de SpaCy (`en_core_web_sm`), owlready2, pyvis et rdflib.
- Les imports cachés (`spacy`, `en_core_web_sm`).
- Les styles QSS de l'interface.
- L'icône personnalisée.

#### `icon.ico` — Icône de l'application

Icône utilisée pour l'exécutable compilé et l'installateur.

#### `example.ttl` — Fichier d'exemple

Fichier Turtle contenant un petit graphe de connaissances sur Apple Inc. (fondateurs, siège social), servant de démonstration pour les fonctionnalités de l'application.

#### `test_ontology.owl` / `test_ontology.rdf` — Ontologies de test

Fichiers ontologie en formats OWL et RDF/XML utilisés pour tester le chargement, la hiérarchie de classes, et le raisonnement.

#### `.gitignore` — Exclusions Git

Exclut les fichiers sensibles (`.env`, `settings.xml`), les artéfacts de build (`dist/`, `build/`, `*.spec`), le cache Python, et les environnements virtuels.

---

### 3.2 Module `core/` — Logique Métier

#### `core/__init__.py`

Fichier vide requis par Python pour reconnaître `core/` comme un package importable.

#### `core/rdf_manager.py` — Gestionnaire de graphe RDF

**Classe principale : `RDFManager`**

Encapsule un objet `rdflib.Graph` et fournit des opérations de haut niveau :
- **`load_file(path)`** : Charge un fichier RDF en détectant automatiquement le format à partir de l'extension (`.ttl`, `.rdf`, `.owl`, `.nt`, `.jsonld`, `.trig`, `.nq`).
- **`save_file(path, fmt)`** : Sérialise le graphe dans le format spécifié.
- **`get_statistics()`** : Calcule et retourne des métriques (nombre de triplets, sujets, prédicats, objets, classes).
- **`get_namespaces()` / `bind_namespace()` / `remove_namespace()`** : Gestion des préfixes d'espaces de noms. La suppression est compatible rdflib 6.x et 7.x.

#### `core/sparql_engine.py` — Moteur SPARQL

**Classe principale : `SPARQLEngine`**

Exécute des requêtes SPARQL sur le graphe géré par `RDFManager` :
- **`execute_query(query_str)`** : Exécute SELECT/CONSTRUCT/ASK/DESCRIBE. Retourne les résultats et le temps d'exécution.
- **`execute_update(query_str)`** : Exécute INSERT/DELETE. Retourne un dictionnaire avec le delta de triplets.
- **`is_update_query(query_str)`** : Détecte si une requête est un UPDATE (en ignorant les commentaires et préfixes).
- **`format_results(results)`** : Convertit les résultats rdflib en dictionnaire structuré pour l'interface.

#### `core/ontology_manager.py` — Gestionnaire d'ontologies

**Classe principale : `OntologyManager`**

Utilise **owlready2** pour charger et inspecter des ontologies OWL/RDFS :
- **`load_ontology(path)`** : Charge une ontologie. Gère la conversion de chemins Windows en IRI valides pour owlready2.
- **`get_classes()` / `get_properties()`** : Liste les classes et propriétés de l'ontologie.
- **`get_hierarchy()`** : Construit un arbre hiérarchique récursif des classes (racine : `owl:Thing`).
- **`get_properties_info()`** : Retourne les métadonnées des propriétés (type, domaine, portée).

> **Justification de l'usage de owlready2 en parallèle de rdflib** : owlready2 fournit un accès orienté objet aux concepts OWL (classes, propriétés, hiérarchie, raisonnement) que rdflib ne peut pas offrir nativement. rdflib est utilisé pour la manipulation générale du graphe RDF et SPARQL.

#### `core/ontology_validator.py` — Validateur d'ontologies

**Classe principale : `OntologyValidator`**

Vérifie la cohérence logique d'une ontologie :
1. Vérifie la présence de classes, propriétés et individus.
2. Détecte les propriétés sans domaine ou portée définie.
3. Exécute le raisonneur HermiT pour trouver les classes insatisfiables.
4. Identifie les classes orphelines (sans parent autre que `Thing`).

Chaque résultat est classé par sévérité : `error`, `warning`, ou `info`.

#### `core/reasoner.py` — Moteur de Raisonnement

**Classe principale : `ReasoningEngine`**

Effectue du raisonnement automatisé sur les ontologies :
- **`run_reasoner(path, type)`** : Charge l'ontologie dans un `World` isolé, exécute le raisonneur choisi (HermiT ou Pellet via owlready2), sauvegarde le résultat dans un fichier temporaire, puis le parse avec rdflib pour le retourner comme graphe.
- **`apply_inference_to_graph(original, inferred)`** : Calcule le différentiel entre le graphe original et le graphe après raisonnement en utilisant une comparaison par fragments d'URI (pour ignorer les différences de chemins de fichiers temporaires).

#### `core/knowledge_extractor.py` — Extracteur NLP

**Classe principale : `KnowledgeExtractor`**

Utilise **SpaCy** (`en_core_web_sm`) pour extraire des triplets RDF à partir de texte :
- Analyse les dépendances syntaxiques pour identifier les relations sujet-prédicat-objet.
- Résout les pronoms via un mécanisme de coréférence simplifié.
- Expandit les conjonctions (« Alice et Bob » → deux sujets distincts).
- Ajoute des types OWL (`NamedIndividual`, `ObjectProperty`) et des types NER (`foaf:Person`, `foaf:Organization`, `schema:Place`).

#### `core/gemini_extractor.py` — Extracteur IA

**Classe principale : `GeminiExtractor`**

Utilise l'API **Google Gemini** pour extraire des triplets RDF :
- Envoie un prompt structuré demandant une sortie en format Turtle.
- Parse la réponse et la convertit en graphe rdflib.
- Gère les erreurs d'API (authentification, quota, réseau).
- Permet de lister dynamiquement les modèles disponibles.

#### `core/settings_manager.py` — Gestionnaire de Paramètres

**Classe principale : `SettingsManager`**

Gère la persistance des paramètres :
- **Clé API** : Chargée depuis `.env` (sécurité), avec fallback XML (compatibilité legacy).
- **Autres paramètres** : Stockés dans `settings.xml` (modèle Gemini, thème, profil de raisonnement, historique SPARQL).
- L'historique des requêtes est limité à 50 entrées.

---

### 3.3 Module `gui/` — Interface Graphique

#### `gui/__init__.py`

Fichier vide pour le package Python.

#### `gui/main_window.py` — Fenêtre Principale

**Classe principale : `MainWindow` (hérite de `QMainWindow`)**

Orchestre l'ensemble de l'interface :
- **Barre de menus** : File (charger, exporter, réinitialiser), View (thème), Reasoning (activer/exécuter), Tools (namespaces, validation).
- **Barre d'outils** : Sélecteur de profil de raisonnement, bouton d'exécution.
- **Onglets centraux** : Visualization, SPARQL Query, Text to RDF.
- **Panneaux latéraux (Docks)** : Ontology Hierarchy (gauche), Graph Statistics (droite).
- **Signaux** : `graph_merged` et `graph_updated` propagent les changements de graphe vers tous les composants.

#### `gui/styles/dark_theme.qss` — Thème Sombre

Feuille de style QSS (Qt Style Sheets) définissant le thème sombre de l'application. Couvre :
- Couleurs de fond et de texte pour tous les widgets.
- Style des onglets, boutons, champs de saisie, tableaux, arbres.
- Style des menus et barres de menus.
- Style des barres de défilement.

#### `gui/utils/syntax_highlighter.py` — Coloration Syntaxique

**Classe principale : `SPARQLHighlighter` (hérite de `QSyntaxHighlighter`)**

Applique la coloration syntaxique dans l'éditeur SPARQL :
- **Bleu gras** : Mots-clés SPARQL (`SELECT`, `WHERE`, `INSERT`, etc.) y compris les multi-mots (`ORDER BY`, `GROUP BY`).
- **Vert** : Variables (`?var`, `$var`).
- **Violet** : Fonctions built-in (`STR`, `COUNT`, `REGEX`, etc.).
- **Cyan foncé** : URIs (`<http://...>`) et QNames (`prefix:suffix`).
- **Rouge foncé** : Chaînes de caractères.
- **Gris italique** : Commentaires (`# ...`).

#### `gui/utils/sparql_completer.py` — Auto-complétion

**Classe principale : `SPARQLCompleter`**

Fournit l'auto-complétion dans l'éditeur SPARQL via un popup `QListWidget` :
- Propose les mots-clés et fonctions SPARQL 1.1.
- Suggère les variables déjà utilisées dans la requête.
- Propose les préfixes communs après le mot-clé `PREFIX`.
- Propose les préfixes d'espaces de noms chargés dans le graphe.
- S'active après 2 caractères tapés, limité à 15 suggestions.

#### `gui/widgets/graph_viewer.py` — Visualisation de Graphe

**Classes : `GraphViewer`, `GraphWebPage`**

Affiche le graphe RDF comme un réseau interactif :
- Convertit le graphe rdflib en réseau PyVis.
- Rend le réseau dans un `QWebEngineView` via un fichier HTML temporaire.
- Supporte 3 modes de mise en page : Force Directed, Hierarchical, Barnes Hut.
- Interception des clics : sélection de nœuds, ouverture d'URIs HTTP dans le navigateur système.
- Bouton « Remove Selected Node » pour supprimer un nœud et ses triplets associés.
- Limite d'affichage à 500 triplets pour les performances.

#### `gui/widgets/query_widget.py` — Interface SPARQL

**Classe principale : `QueryWidget`**

Interface complète pour les requêtes SPARQL :
- **Éditeur** avec coloration syntaxique et auto-complétion.
- **Boutons** : Execute Query (SELECT/ASK/CONSTRUCT/DESCRIBE) et Execute UPDATE (INSERT/DELETE).
- **Résultats** affichés dans deux onglets : Table et Visualization (sous-graphe du résultat).
- **Historique** des requêtes avec chargement rapide par double-clic.
- **Export** des résultats en JSON, CSV ou XML (SPARQL Results XML).
- Détection automatique des requêtes UPDATE.
- Barre de statut avec temps d'exécution et nombre de résultats.

#### `gui/widgets/text_kg_widget.py` — Conversion Texte → RDF

**Classe principale : `TextKGWidget`**

Widget à deux onglets pour l'extraction de connaissances :

1. **🤖 Gemini AI** : Configuration de la clé API et du modèle, extraction via l'API, visualisation du résultat, fusion vers le graphe principal.
2. **🧠 SpaCy NLP** : Extraction locale sans API, même workflow de visualisation et fusion.

Fonctionnalités communes :
- Tableau des triplets extraits.
- Visualisation du sous-graphe généré.
- Export RDF (Turtle, RDF/XML, N-Triples).
- Fusion vers le graphe principal avec signal de mise à jour.

#### `gui/widgets/ontology_tree.py` — Arbre Ontologique

**Classe principale : `OntologyTree`**

Affiche la structure de l'ontologie dans deux onglets :
- **Classes** : Arbre hiérarchique récursif (racine : `Thing`), avec nom et IRI.
- **Properties** : Groupées par type (Object Properties, Data Properties), avec domaine et portée.

#### `gui/widgets/stats_widget.py` — Statistiques du Graphe

**Classe principale : `StatsWidget`**

Panneau compact affichant en temps réel :
- Nombre de triplets, sujets, prédicats, objets et classes dans le graphe.

#### `gui/widgets/namespace_dialog.py` — Gestion des Espaces de Noms

**Classe principale : `NamespaceDialog`**

Dialogue modal permettant de :
- Visualiser tous les préfixes d'espaces de noms liés au graphe.
- Ajouter ou mettre à jour un binding (préfixe → URI).
- Supprimer un binding existant.

#### `gui/widgets/validation_dialog.py` — Résultats de Validation

**Classe principale : `ValidationDialog`**

Affiche les résultats de la validation d'ontologie :
- Résumé avec compteurs (erreurs, avertissements, informations).
- Tableau trié par sévérité (erreurs en premier).
- Icônes visuelles (❌, ⚠️, ℹ️) et codes couleur.

#### `gui/widgets/inferred_triples_dialog.py` — Triplets Inférés

**Classe principale : `InferredTriplesDialog`**

Affiche les résultats du raisonnement automatisé :
- Résumé avec temps d'exécution et nombre de nouveaux triplets.
- Tableau des triplets inférés (Subject, Predicate, Object).
- Bouton d'export des inférences uniquement.

---

### 3.4 Répertoire `lib/` — Bibliothèques Embarquées

#### `lib/bindings/utils.js`

Utilitaires JavaScript utilisés par PyVis pour la mise en surbrillance des nœuds et le filtrage dans les visualisations de réseau. Fournit :
- `neighbourhoodHighlight()` : Met en évidence le nœud sélectionné et ses voisins.
- `filterHighlight()` : Cache les nœuds non sélectionnés.
- `selectNode()` / `selectNodes()` : Sélection programmatique.
- `highlightFilter()` : Filtrage par propriété.

#### `lib/vis-9.1.2/`

Bibliothèque **Vis.js** v9.1.2 embarquée. Utilisée par PyVis pour le rendu des visualisations de réseau dans le navigateur embarqué.

#### `lib/tom-select/`

Bibliothèque **Tom Select** pour les sélecteurs enrichis dans les interfaces HTML générées par PyVis.

---

### 3.5 Répertoire `data/` — Données

- **`dev.ttl`** / **`test.ttl`** : Fichiers Turtle de développement et de test.
- **`examples/`** : Ontologies d'exemple (`pizza.owl`, `test.owl`, etc.) pour tester le chargement et le raisonnement.
- **`reasoners/`** : Données de test spécifiques pour le raisonnement (`famille_data.rdf`, `famille_complete.rdf`).

---

### 3.6 Répertoire `scripts/` — Scripts de Débogage

#### `scripts/debug_extraction.py`

Script autonome pour tester l'extraction NLP. Exécute SpaCy sur un texte d'exemple et affiche les entités et triplets extraits.

#### `scripts/debug_reasoner.py`

Script autonome pour tester le moteur de raisonnement. Crée une ontologie simple avec transitivité et vérifie que le raisonneur infère correctement les nouveaux triplets.

#### `scripts/verify_pyvis.py`

Script de vérification que PyVis fonctionne correctement (génération HTML, inclusion de Vis.js en mode inline).

---

### 3.7 Répertoire `tests/` — Tests Unitaires

Le projet contient **14 fichiers de test** couvrant :

| Fichier | Module testé |
|---|---|
| `test_rdf_manager.py` | Chargement, sauvegarde et statistiques RDF |
| `test_sparql_engine.py` | Exécution de requêtes SPARQL |
| `test_ontology_manager.py` | Chargement d'ontologies et hiérarchie |
| `test_reasoner.py` | Moteur de raisonnement |
| `test_knowledge_extractor.py` | Extraction NLP via SpaCy |
| `test_gemini_ui.py` | Interface Gemini AI |
| `test_graph_interaction.py` | Interactions avec le graphe (sélection, suppression) |
| `test_new_features.py` | Nouvelles fonctionnalités |
| `test_ontology_refresh.py` | Rafraîchissement de l'ontologie après modifications |
| `test_reasoning_ui.py` | Interface de raisonnement |
| `test_settings_persistence.py` | Persistance des paramètres |
| `test_namespace_manager.py` | Gestion des espaces de noms |
| `test_syntax_highlighter.py` | Coloration syntaxique SPARQL |
| `test_theme.py` | Thème sombre |

---

## 4. Justification des Technologies

### 4.1 Python

**Pourquoi Python ?**
- Écosystème riche pour le Web sémantique (rdflib, owlready2, SpaCy).
- Syntaxe claire et productive pour un projet universitaire.
- Large communauté et documentation abondante.
- Compatibilité avec les bibliothèques d'IA générative (google-generativeai).

### 4.2 PyQt6

**Pourquoi PyQt6 plutôt que Tkinter, Kivy ou une interface web ?**
- **Richesse des widgets** : QTreeWidget, QTableWidget, QDockWidget, QTabWidget — essentiels pour une interface complexe multi-panneaux.
- **QWebEngineView** : Permet d'embarquer un rendu HTML/JS complet (Vis.js) directement dans l'application de bureau, sans serveur web.
- **Thèmes via QSS** : Personnalisation visuelle avancée (thème sombre) sans dépendance externe.
- **Maturité** : Bindings Qt officiels, stabilité éprouvée, documentation exhaustive.
- **Cross-platform** : Fonctionne sur Windows, macOS et Linux.

### 4.3 rdflib

**Pourquoi rdflib ?**
- **Standard de facto** en Python pour la manipulation de graphes RDF.
- Supporte tous les formats requis : Turtle, RDF/XML, N-Triples, JSON-LD, TriG, N-Quads.
- Moteur SPARQL 1.1 intégré (SELECT, CONSTRUCT, ASK, DESCRIBE, INSERT, DELETE).
- Gestion native des espaces de noms.
- API Pythonique et bien documentée.

### 4.4 owlready2

**Pourquoi owlready2 en complément de rdflib ?**
- **Modèle objet OWL** : Accès direct aux classes, propriétés, individus, et hiérarchie — impossible avec rdflib seul.
- **Raisonneur intégré** : Interface transparente avec HermiT (Java) et Pellet pour l'inférence automatique.
- **Validation** : Détection des classes insatisfiables et des incohérences logiques.
- rdflib ne gère que la couche RDF ; owlready2 opère au niveau OWL, ce qui est indispensable pour le raisonnement.

### 4.5 PyVis + Vis.js

**Pourquoi PyVis ?**
- Génère des visualisations de réseau interactives en HTML/JS à partir de Python.
- Basé sur **Vis.js**, une bibliothèque mature de visualisation de réseau.
- Supporte plusieurs algorithmes de layout (force-directed, hierarchical, Barnes-Hut).
- Mode `cdn_resources="in_line"` : les assets JS/CSS sont embarqués dans le HTML, permettant un fonctionnement hors-ligne dans QWebEngineView.
- Interactions riches : zoom, pan, sélection, mise en évidence des voisins.

### 4.6 SpaCy

**Pourquoi SpaCy pour l'extraction NLP ?**
- Pipeline NLP de niveau industriel avec modèles pré-entraînés (`en_core_web_sm`).
- Analyse des dépendances syntaxiques (dependency parsing) — nécessaire pour extraire les relations sujet-prédicat-objet.
- Reconnaissance d'entités nommées (NER) intégrée — permet de typer automatiquement les entités (PERSON, ORG, GPE).
- Performance élevée, fonctionne en local sans API externe.
- Modèle léger (`en_core_web_sm` ~12MB) adapté à un exécutable distribué.

### 4.7 Google Gemini API

**Pourquoi Gemini en complément de SpaCy ?**
- **Compréhension sémantique profonde** : Un modèle de langage peut extraire des relations implicites et complexes que le parsing syntaxique ne capture pas.
- **Flexibilité** : Produit directement du Turtle valide, gérant automatiquement les vocabulaires standards (rdf, owl, foaf, schema).
- **Complémentarité** : SpaCy est local et rapide mais limité aux structures syntaxiques explicites. Gemini offre une extraction plus riche mais dépend d'une connexion internet.

### 4.8 python-dotenv

**Pourquoi python-dotenv ?**
- Sépare les secrets (clé API) du code et des paramètres.
- Convention standard (fichier `.env`) facilitant le déploiement.
- Compatible `.gitignore` : la clé n'est jamais versionnée.

### 4.9 PyInstaller + Inno Setup

**Pourquoi cette chaîne de distribution ?**
- **PyInstaller** : Compile l'application Python + toutes ses dépendances en un dossier autonome, sans nécessiter d'installation de Python chez l'utilisateur final.
- **Inno Setup** : Crée un installateur Windows professionnel (.exe) avec raccourcis, désinstallation propre, et compression LZMA.
- Cette combinaison permet de distribuer l'application comme un logiciel Windows standard.

### 4.10 XML pour les paramètres

**Pourquoi XML plutôt que JSON ou YAML ?**
- Cohérence sémantique avec le projet (RDF/XML, OWL/XML sont des formats centraux du web sémantique).
- Bibliothèque `xml.etree.ElementTree` intégrée à Python (aucune dépendance supplémentaire).
- Structure hiérarchique naturellement adaptée aux groupes de paramètres (Gemini, Appearance, Reasoning, History).

---

## 5. Diagramme d'Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        app.py (Entry Point)                     │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     gui/main_window.py                          │
│                       (MainWindow)                              │
│                                                                 │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────────┐ │
│  │ Graph Viewer │ │ Query Widget │ │    Text KG Widget        │ │
│  │  (PyVis +    │ │ (SPARQL +    │ │ (Gemini AI + SpaCy NLP)  │ │
│  │  WebEngine)  │ │  Highlighter │ │                          │ │
│  │              │ │  + Completer)│ │                          │ │
│  └──────────────┘ └──────────────┘ └──────────────────────────┘ │
│                                                                 │
│  ┌────────────────┐ ┌──────────────┐ ┌────────────────────────┐ │
│  │ Ontology Tree  │ │ Stats Widget │ │ Dialogs (Namespace,    │ │
│  │ (Dock - Left)  │ │ (Dock-Right) │ │  Validation, Inferred) │ │
│  └────────────────┘ └──────────────┘ └────────────────────────┘ │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                          core/ (Backend)                        │
│                                                                 │
│  ┌───────────────┐  ┌───────────────┐  ┌─────────────────────┐ │
│  │  RDFManager   │  │ SPARQLEngine  │  │ OntologyManager     │ │
│  │  (rdflib)     │──│ (rdflib)      │  │ (owlready2)         │ │
│  └───────────────┘  └───────────────┘  └─────────────────────┘ │
│                                                                 │
│  ┌───────────────┐  ┌───────────────┐  ┌─────────────────────┐ │
│  │ Reasoner      │  │ KnowledgeExtr.│  │ GeminiExtractor     │ │
│  │ (owlready2 +  │  │ (SpaCy NLP)   │  │ (Gemini API)        │ │
│  │  HermiT/      │  │               │  │                     │ │
│  │  Pellet)      │  │               │  │                     │ │
│  └───────────────┘  └───────────────┘  └─────────────────────┘ │
│                                                                 │
│  ┌───────────────┐  ┌──────────────────────────────────────── ┐ │
│  │ Settings Mgr  │  │ OntologyValidator (owlready2)           │ │
│  │ (XML + .env)  │  │                                         │ │
│  └───────────────┘  └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. Flux de Données

1. **Chargement** : `File → RDFManager.load_file()` → Graphe rdflib en mémoire.
2. **Visualisation** : Graphe rdflib → `GraphViewer.display_graph()` → PyVis → HTML → QWebEngineView.
3. **Requête SPARQL** : texte → `SPARQLEngine.execute_query()` → résultats → `QueryWidget.display_results()`.
4. **Extraction NLP** : texte → `KnowledgeExtractor.extract_triples()` → sous-graphe rdflib → fusion dans graphe principal.
5. **Extraction IA** : texte → `GeminiExtractor.extract_triples()` → Turtle → sous-graphe rdflib → fusion.
6. **Raisonnement** : graphe → export OWL → `ReasoningEngine.run_reasoner()` → graphe inféré → diff → fusion.
7. **Ontologie** : graphe → export temp OWL → `OntologyManager.load_ontology()` → hiérarchie → `OntologyTree`.

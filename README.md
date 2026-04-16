# Knowledge Graph Manager — Guide d'Utilisation

## Table des Matières

1. [Installation](#1-installation)
2. [Lancement de l'Application](#2-lancement-de-lapplication)
3. [Interface Utilisateur](#3-interface-utilisateur)
4. [Charger des Données](#4-charger-des-données)
5. [Visualiser le Graphe](#5-visualiser-le-graphe)
6. [Interroger avec SPARQL](#6-interroger-avec-sparql)
7. [Extraire des Connaissances depuis du Texte](#7-extraire-des-connaissances-depuis-du-texte)
8. [Raisonnement Automatisé](#8-raisonnement-automatisé)
9. [Valider une Ontologie](#9-valider-une-ontologie)
10. [Gérer les Espaces de Noms](#10-gérer-les-espaces-de-noms)
11. [Exporter les Données](#11-exporter-les-données)
12. [Paramètres et Personnalisation](#12-paramètres-et-personnalisation)
13. [Exemples de Scénarios](#13-exemples-de-scénarios)
14. [Dépannage](#14-dépannage)

---

## 1. Installation

### Option A : Installateur Windows (Recommandé)

1. Téléchargez le fichier `Knowledge_Graph_Manager_Setup.exe` depuis le lien `[Installateur](https://drive.google.com/file/d/1xb94AnZ67cGHQgXUKMIE9woHSfGFIg2k/view?usp=sharing)`.
2. Double-cliquez sur l'installateur et suivez les instructions.
3. Lancez l'application depuis le raccourci créé sur le Bureau ou dans le menu Démarrer.

### Option B : Depuis les Sources

#### Prérequis

- **Python 3.10+** (recommandé : Python 3.12)
- **Java 8+** (nécessaire pour les raisonneurs HermiT et Pellet)
- **Git** (optionnel, pour cloner le projet)

#### Étapes

```bash
# 1. Cloner le projet
git clone <url-du-repo>
cd knowledge-Graph-tools

# 2. Créer un environnement virtuel
python -m venv .venv

# 3. Activer l'environnement virtuel
# Windows :
.venv\Scripts\activate
# Linux/macOS :
source .venv/bin/activate

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Télécharger le modèle SpaCy
python -m spacy download en_core_web_sm

# 6. Configurer la clé API Gemini (optionnel)
# Créer un fichier .env à la racine du projet :
echo GEMINI_API_KEY=votre_clé_ici > .env

# 7. Lancer l'application
python app.py
```

> **Raccourci Windows** : Vous pouvez aussi double-cliquer sur `run.bat` pour lancer l'application automatiquement.

---

## 2. Lancement de l'Application

Au lancement, l'application affiche la fenêtre principale avec :
- Un graphe vide (onglet "Graph Visualization")
- Un éditeur SPARQL (onglet "SPARQL Query")
- Un extracteur de texte (onglet "Text to RDF")
- Le panneau de hiérarchie ontologique (à gauche)
- Le panneau de statistiques (à droite)

---

## 3. Interface Utilisateur

L'interface est composée de 5 zones principales :

```
┌──────────────────────────────────────────────────────────────┐
│  Menu Bar : File | View | Reasoning | Tools                 │
├──────────────────────────────────────────────────────────────┤
│  Toolbar : [Reasoning Profile ▼]  [Run Reasoner]            │
├──────────┬───────────────────────────────────┬───────────────┤
│          │                                   │               │
│ Ontology │   Central Area (Tabs)             │    Graph      │
│ Hierarchy│   ├── Graph Visualization         │  Statistics   │
│  (Dock)  │   ├── SPARQL Query                │   (Dock)      │
│          │   └── Text to RDF                 │               │
│          │                                   │               │
└──────────┴───────────────────────────────────┴───────────────┘
```

Les panneaux latéraux (Docks) sont redimensionnables et peuvent être détachés ou fermés.

---

## 4. Charger des Données

### 4.1 Charger un graphe RDF

1. Allez dans **File → Load RDF Graph**.
2. Sélectionnez un fichier RDF supporté :
   - Turtle (`.ttl`)
   - RDF/XML (`.xml`, `.rdf`, `.owl`)
   - N-Triples (`.nt`)
   - JSON-LD (`.jsonld`)
   - TriG (`.trig`)
   - N-Quads (`.nq`)
3. Le graphe est chargé, visualisé, et les statistiques sont mises à jour.

> **Astuce** : Vous pouvez charger plusieurs fichiers successivement — les données sont cumulées dans le même graphe.

### 4.2 Charger une ontologie

1. Allez dans **File → Load Ontology**.
2. Sélectionnez un fichier ontologie (`.owl`, `.rdf`, `.xml`, `.ttl`).
3. L'ontologie est chargée à la fois dans :
   - Le **panneau de hiérarchie** (arbre de classes et propriétés)
   - Le **graphe RDF** (pour la visualisation et les requêtes SPARQL)

### 4.3 Réinitialiser le graphe

- **File → Reset/Clear Graph** : Vide complètement le graphe en mémoire et réinitialise tous les panneaux.

---

## 5. Visualiser le Graphe

L'onglet **Graph Visualization** affiche un graphe interactif :

### Interactions

| Action | Effet |
|---|---|
| **Cliquer** sur un nœud | Le sélectionne (affiché dans la barre d'état) |
| **Double-cliquer** sur un nœud HTTP | Ouvre l'URI dans le navigateur système |
| **Glisser** un nœud | Déplace le nœud |
| **Molette** | Zoom avant/arrière |
| **Cliquer-glisser** dans le vide | Déplace la vue d'ensemble |

### Changer le mode de mise en page

Utilisez le sélecteur **Layout** en haut de l'onglet :

- **Force Directed** (défaut) : Les nœuds se repoussent naturellement, les arêtes agissent comme des ressorts. Idéal pour explorer la structure globale.
- **Hierarchical** : Affichage en arbre de haut en bas. Utile pour les ontologies avec une hiérarchie claire.
- **Barnes Hut** : Algorithme optimisé pour les grands graphes. Plus rapide que Force Directed pour beaucoup de nœuds.

### Supprimer un nœud

1. Cliquez sur un nœud pour le sélectionner.
2. Cliquez sur le bouton **"Remove Selected Node"**.
3. Le nœud et tous les triplets qui le référencent (comme sujet ou objet) seront supprimés.

### Légende des couleurs

- **Nœuds bleus** (🔵 `#97C2FC`) : Sujets des triplets
- **Nœuds roses** (🔴 `#FB7E81`) : Objets des triplets
- **Arêtes** : Prédicats (labels affichés sur les arêtes)

> **Note** : Pour les performances, seuls les 500 premiers triplets sont affichés dans le graphe.

---

## 6. Interroger avec SPARQL

L'onglet **SPARQL Query** offre un éditeur de requêtes complet.

### 6.1 Écrire une requête

L'éditeur fournit :
- **Coloration syntaxique** : Mots-clés en bleu, variables en vert, fonctions en violet, URIs en cyan, commentaires en gris.
- **Auto-complétion** : Commencez à taper et une liste de suggestions apparaît. Utilisez ↑/↓ pour naviguer et Tab/Entrée pour insérer.

### 6.2 Exécuter une requête SELECT

```sparql
# Exemple : Lister tous les triplets du graphe
SELECT * WHERE { ?s ?p ?o } LIMIT 10
```

1. Tapez votre requête dans l'éditeur.
2. Cliquez sur **"Execute Query"**.
3. Les résultats apparaissent dans l'onglet **Table** (tableau) et **Visualization** (sous-graphe).
4. La barre de statut affiche le nombre de résultats et le temps d'exécution.

### 6.3 Exécuter une requête CONSTRUCT

```sparql
# Exemple : Construire un sous-graphe des personnes
CONSTRUCT { ?person a foaf:Person . ?person foaf:name ?name }
WHERE { ?person a foaf:Person . ?person foaf:name ?name }
```

Les résultats d'un CONSTRUCT sont affichés à la fois comme tableau et comme graphe visualisé.

### 6.4 Exécuter une requête ASK

```sparql
# Exemple : Vérifier si un triplet existe
ASK WHERE { ?s a owl:Class }
```

Le résultat est un simple `True` ou `False`.

### 6.5 Exécuter un UPDATE (INSERT / DELETE)

```sparql
# Exemple : Ajouter un triplet
PREFIX ex: <http://example.org/>
INSERT DATA {
  ex:Alice a ex:Person .
}
```

```sparql
# Exemple : Supprimer un triplet
PREFIX ex: <http://example.org/>
DELETE DATA {
  ex:Alice a ex:Person .
}
```

1. Tapez votre opération UPDATE.
2. Cliquez sur **"Execute UPDATE"** (ou "Execute Query" — la détection est automatique).
3. Un message confirme le nombre de triplets ajoutés/supprimés.
4. Le graphe et les statistiques sont automatiquement mis à jour.

### 6.6 Historique des requêtes

- Les requêtes exécutées sont automatiquement sauvegardées dans le panneau **History** (à droite de l'éditeur).
- **Double-cliquez** sur une requête dans l'historique pour la recharger dans l'éditeur.
- L'historique est persisté entre les sessions dans `settings.xml`.

### 6.7 Exporter les résultats

1. Exécutez une requête.
2. Cliquez sur **"Export Results"**.
3. Choisissez le format :
   - **JSON** : Format structuré standard.
   - **CSV** : Compatible avec Excel et tableurs.
   - **XML** : Format SPARQL Results XML (standard W3C).

---

## 7. Extraire des Connaissances depuis du Texte

L'onglet **Text to RDF** permet de convertir du texte libre en triplets RDF.

### 7.1 Extraction avec Gemini AI (🤖)

1. Sélectionnez l'onglet **🤖 Gemini AI**.
2. **Configurez votre clé API** :
   - Collez votre clé Google Gemini dans le champ "API Key".
   - La clé est automatiquement sauvegardée dans le fichier `.env`.
3. **Choisissez un modèle** :
   - Par défaut : `gemini-2.0-flash` (rapide et bon marché).
   - Cliquez sur **"Fetch Models"** pour voir tous les modèles disponibles.
4. **Entrez votre texte** dans la zone de saisie.
5. Cliquez sur **"Generate RDF (Gemini)"**.
6. Les triplets extraits apparaissent dans un tableau et un graphe de visualisation.

**Exemple de texte** :
```
Apple Inc. was founded by Steve Jobs and Steve Wozniak in April 1976. 
The company is headquartered in Cupertino, California.
```

### 7.2 Extraction avec SpaCy NLP (🧠)

1. Sélectionnez l'onglet **🧠 SpaCy NLP**.
2. **Entrez votre texte** dans la zone de saisie.
3. Cliquez sur **"Generate RDF (SpaCy)"**.
4. Les triplets extraits sont affichés.

> **Conseil** : SpaCy fonctionne mieux avec des phrases simples ayant une structure sujet-verbe-objet claire. Par exemple : « Alice lives in Paris. Bob works at Google. »

### 7.3 Fusionner et exporter

- **"Merge to Main Graph"** : Ajoute les triplets extraits au graphe principal. Le graphe et les statistiques sont automatiquement mis à jour.
- **"Export RDF"** : Exporte les triplets extraits dans un fichier séparé (Turtle, RDF/XML, ou N-Triples).

### 7.4 Comparaison des deux méthodes

| Critère | SpaCy NLP | Gemini AI |
|---|---|---|
| **Connexion Internet** | ❌ Non requise | ✅ Requise |
| **Coût** | Gratuit | API payante (avec quota gratuit) |
| **Qualité** | Limitée aux structures S-V-O explicites | Comprend les relations implicites |
| **Vitesse** | Très rapide (local) | 1-5 secondes par requête |
| **Vocabulaire** | Basique (kb:, owl:, foaf:) | Riche (utilise rdfs:, schema:, etc.) |

---

## 8. Raisonnement Automatisé

Le raisonnement permet d'inférer de nouvelles connaissances à partir des données et de l'ontologie existante.

### 8.1 Choisir un profil de raisonnement

Dans la barre d'outils, sélectionnez un profil :

| Profil | Description |
|---|---|
| **OWL DL (HermiT)** | Raisonneur complet pour OWL DL. Détecte les sous-classes, l'appartenance de type, la transitivité, etc. |
| **OWL DL (Pellet)** | Alternative à HermiT. Supporte aussi l'inférence sur les propriétés de données. |
| **RDFS (via OWL DL)** | Mode simplifié utilisant uniquement les règles RDFS. |

> **Prérequis** : Java doit être installé sur votre système pour que les raisonneurs fonctionnent.

### 8.2 Exécuter manuellement le raisonnement

1. Chargez un graphe RDF ou une ontologie contenant des classes et des individus.
2. Allez dans **Reasoning → Run Reasoner (HermiT)** ou **Run Reasoner (Pellet)**, ou cliquez sur **"Run Reasoner"** dans la barre d'outils.
3. L'application vous demande de sauvegarder le graphe en format OWL (nécessaire pour le raisonneur).
4. Après le raisonnement, un dialogue affiche :
   - Le temps d'exécution.
   - Le nombre de nouveaux triplets inférés.
   - Un tableau détaillé des triplets inférés.
5. Vous pouvez **exporter** les triplets inférés séparément.

### 8.3 Activer le raisonnement automatique

- Allez dans **Reasoning → Enable Auto-Reasoning**.
- Quand cette option est activée, le raisonnement s'exécute automatiquement à chaque fois que le graphe change (chargement de fichier, fusion de données, etc.).

### 8.4 Exemple de raisonnement

**Données initiales** :
```
:Dog rdfs:subClassOf :Animal .
:Rex rdf:type :Dog .
```

**Après raisonnement** (triplet inféré) :
```
:Rex rdf:type :Animal .
```

Le raisonneur déduit que si Rex est un Chien et que Chien est une sous-classe d'Animal, alors Rex est aussi un Animal.

---

## 9. Valider une Ontologie

La validation vérifie la cohérence logique de votre ontologie.

### Étapes

1. Chargez un graphe RDF ou une ontologie.
2. Allez dans **Tools → Validate Ontology**.
3. L'application vous demande de sauvegarder le graphe au format OWL.
4. Un dialogue affiche les résultats classés par sévérité :
   - **❌ Erreur** : Classes insatisfiables, incohérences logiques.
   - **⚠️ Avertissement** : Propriétés sans domaine/portée, pas de classes définies.
   - **ℹ️ Information** : Statistiques, classes orphelines.

### Exemple de résultat

| Sévérité | Message |
|---|---|
| ℹ️ INFO | Found 5 class(es): Person, Organization, Place... |
| ℹ️ INFO | Found 3 property(ies). |
| ⚠️ WARNING | Property 'hasChild' has no range defined. |
| ℹ️ INFO | Consistency check passed: No unsatisfiable classes found. |

---

## 10. Gérer les Espaces de Noms

Les espaces de noms (namespaces) permettent d'utiliser des préfixes courts au lieu d'URIs complètes.

### Accéder au gestionnaire

1. Allez dans **Tools → Manage Namespaces**.
2. Le dialogue affiche tous les préfixes liés au graphe.

### Ajouter un préfixe

1. Remplissez les champs **Prefix** et **URI**.
   - Exemple : Prefix = `ex`, URI = `http://example.org/`
2. Cliquez sur **"Bind/Update"**.
3. Le préfixe est maintenant utilisable dans les requêtes SPARQL.

### Supprimer un préfixe

1. Sélectionnez une ligne dans le tableau.
2. Cliquez sur **"Remove Selected"**.

---

## 11. Exporter les Données

### 11.1 Exporter le graphe complet

1. Allez dans **File → Export Graph**.
2. Choisissez le format :
   - **Turtle** (`.ttl`) : Format lisible et compact.
   - **RDF/XML** (`.rdf`, `.xml`) : Format XML standard.
   - **N-Triples** (`.nt`) : Format simple, un triplet par ligne.

### 11.2 Exporter les résultats SPARQL

1. Exécutez une requête dans l'onglet SPARQL.
2. Cliquez sur **"Export Results"**.
3. Formats disponibles : JSON, CSV, XML.

### 11.3 Exporter les triplets extraits

Dans l'onglet "Text to RDF", cliquez sur **"Export RDF"** pour sauvegarder les triplets extraits dans un fichier séparé.

### 11.4 Exporter les triplets inférés

Après un raisonnement, dans le dialogue des résultats, cliquez sur **"Export Inferred Triples"**.

---

## 12. Paramètres et Personnalisation

### 12.1 Thème sombre

- Allez dans **View → Dark Theme** pour activer/désactiver le thème sombre.
- La préférence est sauvegardée automatiquement.

### 12.2 Clé API Gemini

- La clé est stockée dans le fichier `.env` (sécurisé, exclu de Git).
- Vous pouvez la modifier :
  - Via l'interface (onglet Text to RDF → champ API Key).
  - Manuellement dans le fichier `.env`.

### 12.3 Modèle Gemini

- Sélectionnable dans l'onglet Text to RDF.
- Cliquez sur **"Fetch Models"** pour voir les modèles disponibles avec votre clé API.
- Par défaut : `gemini-2.0-flash`.

### 12.4 Profil de raisonnement

- Modifiable dans la barre d'outils ou via le menu Reasoning.
- Sauvegardé automatiquement dans `settings.xml`.

---

## 13. Exemples de Scénarios

### Scénario 1 : Explorer une ontologie existante

1. **File → Load Ontology** → Sélectionnez `data/examples/pizza.owl`.
2. Observez la hiérarchie de classes dans le panneau gauche.
3. Passez à l'onglet **SPARQL Query** et exécutez :
   ```sparql
   SELECT ?class WHERE { ?class a owl:Class } LIMIT 20
   ```
4. Explorez le graphe dans l'onglet **Graph Visualization**.

### Scénario 2 : Créer un graphe de connaissances depuis du texte

1. Allez dans l'onglet **Text to RDF → 🤖 Gemini AI**.
2. Entrez le texte suivant :
   ```
   Marie Curie was born in Warsaw, Poland. She discovered radium 
   and polonium. She won two Nobel Prizes.
   ```
3. Cliquez sur **"Generate RDF (Gemini)"**.
4. Observez les triplets extraits.
5. Cliquez sur **"Merge to Main Graph"** pour les ajouter au graphe principal.
6. Passez à l'onglet **Graph Visualization** pour voir le résultat.

### Scénario 3 : Raisonnement et inférence

1. **File → Load RDF Graph** → Sélectionnez `data/reasoners/famille_data.rdf`.
2. Observez les données existantes avec :
   ```sparql
   SELECT * WHERE { ?s ?p ?o }
   ```
3. Cliquez sur **"Run Reasoner"** dans la barre d'outils.
4. Sauvegardez le graphe quand demandé.
5. Observez les nouveaux triplets inférés dans le dialogue.
6. Refaites la requête SPARQL : de nouveaux résultats apparaissent.

### Scénario 4 : Requête INSERT puis validation

1. Dans l'onglet **SPARQL Query**, exécutez :
   ```sparql
   PREFIX ex: <http://example.org/>
   PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
   PREFIX owl: <http://www.w3.org/2002/07/owl#>
   
   INSERT DATA {
     ex:Cat a owl:Class .
     ex:Animal a owl:Class .
     ex:Cat rdfs:subClassOf ex:Animal .
     ex:Felix a ex:Cat .
   }
   ```
2. Vérifiez dans le graphe que les données sont ajoutées.
3. Allez dans **Tools → Validate Ontology** pour vérifier la cohérence.
4. Lancez le raisonnement pour vérifier que Felix est inféré comme Animal.

---

## 14. Dépannage

### L'application ne se lance pas

- **Vérifiez que Python 3.10+ est installé** : `python --version`
- **Vérifiez l'environnement virtuel** : Assurez-vous que `.venv` existe et est activé.
- **Réinstallez les dépendances** : `pip install -r requirements.txt`
- **Vérifiez PyQt6-WebEngine** : `pip install PyQt6-WebEngine`

### Le graphe ne s'affiche pas

- Le composant `QWebEngineView` nécessite `PyQt6-WebEngine`. Installez-le si nécessaire.
- Sur certains systèmes, une variable d'environnement peut être nécessaire :
  ```bash
  set QTWEBENGINE_CHROMIUM_FLAGS=--disable-gpu
  ```

### Le raisonnement échoue

- **Vérifiez que Java est installé** : `java -version`
- **Assurez-vous que Java est dans le PATH**.
- Le raisonneur HermiT et Pellet sont des programmes Java embarqués dans owlready2.

### L'extraction Gemini échoue

- **Vérifiez votre clé API** : Assurez-vous qu'elle est valide et non expirée.
- **Vérifiez votre connexion Internet**.
- **Erreur 429 (quota)** : Attendez quelques minutes et réessayez.
- **Erreur 403** : Vérifiez que l'API Gemini est activée dans votre projet Google Cloud.

### SpaCy ne fonctionne pas

- **Installez le modèle** : `python -m spacy download en_core_web_sm`
- Si l'erreur persiste, essayez : `pip install spacy --upgrade`

### L'installateur ne fonctionne pas

- L'installateur nécessite des droits administrateur (installation dans Program Files).
- Si l'exécutable crash, vérifiez que le fichier `.env` et les données sont présents dans le dossier d'installation.

---

## Raccourcis et Astuces

| Astuce | Détail |
|---|---|
| **Chargement multiple** | Chargez plusieurs fichiers RDF pour les combiner dans un seul graphe |
| **Auto-complétion** | Tapez 2+ caractères dans l'éditeur SPARQL pour voir les suggestions |
| **Préfixes rapides** | Tapez `PREFIX` dans l'éditeur pour voir les préfixes courants |
| **Double-clic historique** | Double-cliquez sur une requête dans l'historique pour la recharger |
| **Double-clic URI** | Double-cliquez sur un nœud HTTP dans le graphe pour l'ouvrir dans le navigateur |
| **Panneaux flottants** | Les docks latéraux peuvent être détachés et repositionnés |
| **Thème pour les démos** | Le thème sombre est recommandé pour les présentations |

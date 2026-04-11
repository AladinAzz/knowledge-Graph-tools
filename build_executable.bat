@echo off
echo ====================================================
echo Compilation de l'application (Creation de l'Executable)
echo ====================================================

:: Verifier si pyinstaller est installe
.venv\Scripts\python.exe -m pip install pyinstaller

echo.
echo Construction en cours avec PyInstaller...
echo Cela peut prendre 1 a 3 minutes (SpaCy et PyQt6 sont volumineux).

:: Build command
:: --noconfirm: ecrase l'ancien build
:: --windowed: cache la console (GUI uniquement)
:: --add-data: inclut les fichiers de style QSS, avec un separateur ';' sous Windows
:: --hidden-import: force l'inclusion de spacy et de son modele linguistique
:: --icon: definit l'icone de l'executable (doit etre un fichier .ico)
:: --collect-all: importe les fichiers internes caches comme les dossiers pellet/hermit de owlready2, et les templates pyvis
.venv\Scripts\pyinstaller.exe --noconfirm --windowed --name "Knowledge Graph Manager" --icon="icon.ico" --hidden-import="spacy" --hidden-import="en_core_web_sm" --collect-all "owlready2" --collect-all "pyvis" --collect-all "rdflib" --collect-data "en_core_web_sm" --collect-data "spacy" --add-data "gui/styles;gui/styles" app.py

echo.
echo ====================================================
echo Termine !
echo Votre application executable se trouve dans le dossier: 
echo dist\"Knowledge Graph Manager"\"Knowledge Graph Manager".exe
echo.
echo ATTENTION:  N'oubliez pas de copier votre fichier ".env", "test_ontology.owl"
echo           et "reification_test.ttl" dans le meme dossier que l'executable 
echo           pour que la base fonctionne completement !
echo ====================================================
pause

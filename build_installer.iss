[Setup]
; Configuration de base de l'installateur
AppName=Knowledge Graph Manager
AppVersion=1.0
AppPublisher=Université - Projet Web Sémantique
DefaultDirName={autopf}\Knowledge Graph Manager
DefaultGroupName=Knowledge Graph Manager
OutputDir=.\Installateur
OutputBaseFilename=Knowledge_Graph_Manager_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=icon.ico

; L'application necessite les droits admin pour s'installer dans Program Files
PrivilegesRequired=admin

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; IMPORTANT: Cette ligne demande a Inno Setup de copier TOUT le contenu du dossier "dist\Knowledge Graph Manager" 
; (l'executable python compile) vers le dossier d'installation de l'utilisateur.
Source: "dist\Knowledge Graph Manager\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Cree les raccourcis dans le menu demarrer et sur le bureau
Name: "{group}\Knowledge Graph Manager"; Filename: "{app}\Knowledge Graph Manager.exe"
Name: "{group}\{cm:UninstallProgram,Knowledge Graph Manager}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Knowledge Graph Manager"; Filename: "{app}\Knowledge Graph Manager.exe"; Tasks: desktopicon

[Run]
; Option pour lancer l'application a la fin de l'installation
Filename: "{app}\Knowledge Graph Manager.exe"; Description: "{cm:LaunchProgram,Knowledge Graph Manager}"; Flags: nowait postinstall skipifsilent

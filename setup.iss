; https://jrsoftware.org/ishelp/index.php

#define AppName "HDLG"
#define Version "0.1.0"

[Setup]
AppId={#AppName}
AppName={#AppName}
AppPublisher=rlaphoenix
AppPublisherURL=https://github.com/rlaphoenix/hdlg
AppReadmeFile=https://github.com/rlaphoenix/hdlg/blob/master/README.md
AppSupportURL=https://github.com/rlaphoenix/hdlg/discussions
AppUpdatesURL=https://github.com/rlaphoenix/hdlg/releases
AppVerName={#AppName} {#Version}
AppVersion={#Version}
ArchitecturesAllowed=x64
Compression=lzma2/max
DefaultDirName={autopf}\{#AppName}
LicenseFile=LICENSE
; Python 3.9 has dropped support for <= Windows 7/Server 2008 R2 SP1. https://jrsoftware.org/ishelp/index.php?topic=winvernotes
MinVersion=6.2
OutputBaseFilename=HDLG-Setup
OutputDir=dist
OutputManifestFile=HDLG-Setup-Manifest.txt
PrivilegesRequiredOverridesAllowed=dialog commandline
; SetupIconFile=hdlg/icon.ico
SolidCompression=yes
VersionInfoVersion=1.0.0
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: dist\HDLG\*; DestDir: {app}; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppName}.exe"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppName}.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppName}.exe"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

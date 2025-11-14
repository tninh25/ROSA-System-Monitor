; ===============================================================
; Inno Setup Script — ROSA System Monitor (Admin + Auto-start)
; ===============================================================

#define MyAppName "ROSA System Monitor"
#define MyAppVersion "1.0"
#define MyAppPublisher "ROSA Computer, Inc."
#define MyAppURL "https://rosacomputer.vn/"
#define MyAppExeName "main.exe"
#define MyAppAssocName MyAppName + " File"
#define MyAppAssocExt ".myp"
#define MyAppAssocKey StringChange(MyAppAssocName, " ", "") + MyAppAssocExt

[Setup]
AppId={{446F2704-28DA-4B0F-A8E1-187C6A65E36C}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; --------------------------------------------------------------
; CÀI ĐẶT MẶC ĐỊNH VỚI QUYỀN ADMIN
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=commandline

; --------------------------------------------------------------
; THƯ MỤC CÀI ĐẶT MẶC ĐỊNH
DefaultDirName={autopf}\{#MyAppName}

; --------------------------------------------------------------
; KIẾN TRÚC 64-BIT
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

ChangesAssociations=yes
DisableProgramGroupPage=yes

; --------------------------------------------------------------
; FILE OUTPUT
OutputDir=C:\ext-lumin-vietson-api-project\CPU - Z (1)\install
OutputBaseFilename=ROSA System Monitor
SetupIconFile=C:\ext-lumin-vietson-api-project\CPU - Z (1)\rosa-monitor.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

; --------------------------------------------------------------
; TASKS (chỉ còn desktop icon)
[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

; --------------------------------------------------------------
; FILES
[Files]
Source: "C:\ext-lumin-vietson-api-project\CPU - Z (1)\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\ext-lumin-vietson-api-project\CPU - Z (1)\rosa-monitor.ico"; DestDir: "{app}"; Flags: ignoreversion

; --------------------------------------------------------------
; REGISTRY — AutoStart + File Association
[Registry]
; === AutoStart trong registry (HKCU) ===
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; \
    ValueType: string; ValueName: "{#MyAppName}"; \
    ValueData: """{app}\{#MyAppExeName}"" --startup"; \
    Flags: uninsdeletevalue

; === File Association ===
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocExt}\OpenWithProgids"; ValueType: string; ValueName: "{#MyAppAssocKey}"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}"; ValueType: string; ValueName: ""; ValueData: "{#MyAppAssocName}"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".myp"; ValueData: ""

; --------------------------------------------------------------
; ICONS — Desktop + Startup + Start Menu
[Icons]
; Start Menu shortcut
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
; Desktop shortcut
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
; Startup shortcut (đảm bảo tự khởi động)
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Flags: runminimized

; --------------------------------------------------------------
; RUN AFTER INSTALL
[Run]
Filename: "{app}\{#MyAppExeName}"; \
    Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; \
    Flags: nowait postinstall skipifsilent

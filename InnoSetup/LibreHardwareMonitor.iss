; ============================================================
;  Inno Setup script for LibreHardwareMonitor (hidden startup)
;  Author: ChatGPT (Professional setup)
;  Purpose: Install LibreHardwareMonitor, auto-run hidden at startup
; ============================================================
#define MyAppName "ROSA M-Core"
#define MyAppVersion "1.0"
#define MyAppPublisher "ROSA Computer, Inc"
#define MyAppURL "https://rosacomputer.vn/"
#define MyAppExeName "LibreHardwareMonitor.exe"

[Setup]
AppId={{7D52EFCD-1F85-4C9F-A07D-1AC2AFE55A24}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=C:\ext-lumin-vietson-api-project\CPU - Z (1)\install
OutputBaseFilename=ROSA MCore
SetupIconFile=C:\ext-lumin-vietson-api-project\CPU - Z (1)\rosa.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes
PrivilegesRequired=lowest

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
; === LibreHardwareMonitor binaries ===
Source: "C:\Users\ROSA\Downloads\LibreHardwareMonitor\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion
; === Optional config file (nếu có sẵn cấu hình minimize/tray) ===
; Source: "C:\Users\ROSA\Downloads\LibreHardwareMonitor\LibreHardwareMonitor.config"; DestDir: "{app}"; Flags: onlyifdoesntexist ignoreversion

[Icons]
; Shortcut trong Start Menu
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
; Shortcut ngoài desktop (nếu chọn)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
; === Shortcut khởi động cùng Windows (chạy ngầm bằng VBScript) ===
Name: "{userstartup}\{#MyAppName} (Auto start hidden)"; Filename: "{app}\start_hidden.vbs"; WorkingDir: "{app}"

[Run]
; Khởi chạy ngay sau khi cài đặt (ẩn hoàn toàn)
Filename: "{app}\start_hidden.vbs"; Description: "Launch {#MyAppName} in background"; Flags: nowait postinstall skipifsilent runhidden

[UninstallRun]
; Nếu muốn dừng tiến trình khi gỡ cài đặt (tuỳ chọn)
Filename: "{app}\{#MyAppExeName}"; Parameters: "/uninstall"; Flags: runhidden skipifdoesntexist

[Code]
procedure SaveVBScript();
var
  S: string;
  VbsPath: string;
begin
  VbsPath := ExpandConstant('{app}\start_hidden.vbs');
  S :=
    'Option Explicit' + #13#10 +
    'Dim shell, exePath' + #13#10 +
    'Set shell = CreateObject("WScript.Shell")' + #13#10 +
    'exePath = Replace(WScript.ScriptFullName, "start_hidden.vbs", "") & "LibreHardwareMonitor.exe"' + #13#10 +
    '' + #13#10 +
    'shell.Run Chr(34) & exePath & Chr(34), 0, False' + #13#10 +
    'Set shell = Nothing' + #13#10;
  if not SaveStringToFile(VbsPath, S, False) then
    MsgBox('❌ Failed to create startup VBScript: ' + VbsPath, mbError, MB_OK);
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    SaveVBScript(); // Tạo file VBScript để khởi động ẩn
  end;
end;
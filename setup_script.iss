
[Setup]
AppId={{Clip-CACHE_H4}}
AppName=Clip-CACHE
AppVersion=2.0.0
AppPublisher=(b'.')b - h4 - {{Be Your Best}}}
AppPublisherURL=https://github.com/m3rr
AppSupportURL=https://github.com/m3rr
AppUpdatesURL=https://github.com/m3rr
DefaultDirName={autopf}\Clip-CACHE
DisableProgramGroupPage=yes
DisableDirPage=no
UsePreviousAppDir=no
LicenseFile=D:\PROJECTS\TOOLS\SmartBoard\assets\legal\EULA.txt
InfoBeforeFile=D:\PROJECTS\TOOLS\SmartBoard\assets\legal\PRIVACY.txt
; "Deep Void" / Slate Theme Integration
WizardStyle=modern
; WizardImageFile=compiler:WizModernImage-IS.bmp
; WizardSmallImageFile=compiler:WizModernSmallImage-IS.bmp
OutputDir=D:\PROJECTS\TOOLS\SmartBoard\output
OutputBaseFilename=Clip-CACHE_Setup_v2.0
SetupIconFile=D:\PROJECTS\TOOLS\SmartBoard\assets\image_assets\icon.ico
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest
UninstallDisplayIcon={app}\Clip-CACHE.exe

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startwindows"; Description: "Start with Windows"; GroupDescription: "Startup Options"; Flags: unchecked
Name: "startbackground"; Description: "Start in Background (System Tray)"; GroupDescription: "Startup Options"; Flags: unchecked

[Files]
Source: "D:\PROJECTS\TOOLS\SmartBoard\dist\Clip-CACHE\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\Clip-CACHE"; Filename: "{app}\Clip-CACHE.exe"
Name: "{autodesktop}\Clip-CACHE"; Filename: "{app}\Clip-CACHE.exe"; Tasks: desktopicon

[Run]
; Run with start in background flag if selected
Filename: "{app}\Clip-CACHE.exe"; Description: "{cm:LaunchProgram,Clip-CACHE}"; Flags: nowait postinstall skipifsilent

[Registry]
; Start With Windows Logic (If Task Selected) - TRIPLE QUOTE FIX APPLIED
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "Clip-CACHE"; ValueData: """{app}\Clip-CACHE.exe"""; Flags: uninsdeletevalue; Tasks: startwindows

[Code]
// --- Advanced Installer Logic ---
// 1. Detect if App is already installed.
// 2. If yes, ask user: Update/Repair or Uninstall?
// 3. If Uninstall, run the uninstaller silently then proceed (or exit).

function GetUninstallString(): String;
var
  sUnInstPath: String;
  sUnInstPathExe: String;
begin
  sUnInstPath := '';
  sUnInstPathExe := '';
  // Check HKCU (Since PrivilegesRequired=lowest)
  if RegQueryStringValue(HKCU, 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{Clip-CACHE_H4}_is1', 'UninstallString', sUnInstPath) then
    Result := sUnInstPath
  else
    Result := '';
end;

function InitializeSetup(): Boolean;
var
  V: Integer;
  iResultCode: Integer;
  sUnInstallString: String;
begin
  Result := True; // Default proceed
  
  sUnInstallString := GetUninstallString();
  
  if sUnInstallString <> '' then begin
    // Remove Quotes
    StringChange(sUnInstallString, '"', '');
    
    // App is installed. Ask user.
    V := MsgBox('Clip-CACHE is already installed.' + #13#10 + #13#10 +
                'Click "Yes" to REMOVE (Uninstall).' + #13#10 +
                'Click "No" to MODIFY (Change Location) or REPAIR (Reinstall).' + #13#10 +
                'Click "Cancel" to DO NOTHING (Exit Setup).', mbInformation, MB_YESNOCANCEL);
                
    if V = IDYES then begin
      // Run Uninstaller
      sUnInstallString := RemoveQuotes(sUnInstallString);
      Exec(sUnInstallString, '/SILENT', '', SW_SHOW, ewWaitUntilTerminated, iResultCode);
      
      // If user wants full nuke, we assume uninstaller did its job. 
      // Do we allow them to reinstall immediately? Yes.
      // Result := True; 
    end
    else if V = IDNO then begin
      // Update / Repair
      // Just proceed with installation over top.
      Result := True;
    end
    else begin
      // Cancel
      Result := False;
    end;
  end;
end;

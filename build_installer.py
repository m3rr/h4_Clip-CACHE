import os
import sys
import subprocess
import shutil

# --- CONFIGURATION ---
APP_NAME = "Clip-CACHE"
MAIN_SCRIPT = os.path.join("src", "main.py")
LAUNCHER_SCRIPT = "ClipCache_Launcher.py"
ICON_PATH = os.path.join("assets", "image_assets", "icon.ico")
DIST_DIR = "dist"
BUILD_DIR = "build"
WORK_DIR = os.getcwd()

# Ensure we have the icon
if not os.path.exists(ICON_PATH):
    print(f"ERROR: Icon not found at {ICON_PATH}")
    # Try using generated one or warn
    
def clean_build():
    print("[BUILD] Cleaning previous build artifacts...")
    if os.path.exists(DIST_DIR): shutil.rmtree(DIST_DIR)
    if os.path.exists(BUILD_DIR): shutil.rmtree(BUILD_DIR)
    # Clean spec files
    for f in os.listdir("."):
        if f.endswith(".spec"):
            os.remove(f)

def run_pyinstaller():
    print("[BUILD] Running PyInstaller...")
    
    # We use --onedir for "Zero Memory" optimization (shared pages)
    # We use --noconsole to hide the terminal
    # We include the 'assets' directory
    
    cmd = [
        "pyinstaller",
        "--noconsole",
        "--clean",
        "--onedir",
        f"--name={APP_NAME}",
        f"--icon={ICON_PATH}",
        f"--add-data=assets;assets", # Include assets folder
        f"--add-data=src;src",       # Include src folder (Python need code structure sometimes if not fully compiled)
        # Actually for --onedir we just need entry point imports. 
        # But since we do dynamic imports in styles/etc, keeping structure is safer or we let pyinstaller find it.
        # Let's trust PyInstaller's import analysis but ensure assets are there.
        LAUNCHER_SCRIPT 
    ]
    
    # IMPORTANT: We use the LAUNCHER as entry point because it sets up the path correctly!
    
    print(f"Command: {' '.join(cmd)}")
    subprocess.check_call(cmd)

def create_inno_script():
    print("[BUILD] Generating Inno Setup Script...")
    
    # Absolute paths for Inno Setup
    dist_path = os.path.join(WORK_DIR, "dist", APP_NAME)
    output_path = os.path.join(WORK_DIR, "output")
    license_path = os.path.join(WORK_DIR, "assets", "legal", "EULA.txt")
    privacy_path = os.path.join(WORK_DIR, "assets", "legal", "PRIVACY.txt")
    icon_abs_path = os.path.abspath(ICON_PATH)
    
    if not os.path.exists(output_path): os.makedirs(output_path)
    
    # Branding
    publisher = "(b'.')b - h4 - {Be Your Best}"
    url = "https://github.com/m3rr"
    
    q = '"'
    iss_content = f"""
[Setup]
AppId={{{APP_NAME}_H4}}
AppName={APP_NAME}
AppVersion=1.0.0
AppPublisher={publisher}
AppPublisherURL={url}
AppSupportURL={url}
AppUpdatesURL={url}
DefaultDirName={{autopf}}\\{APP_NAME}
DisableProgramGroupPage=yes
LicenseFile={license_path}
InfoBeforeFile={privacy_path}
; "Deep Void" / Slate Theme Integration
WizardStyle=modern
; WizardImageFile=compiler:WizModernImage-IS.bmp
; WizardSmallImageFile=compiler:WizModernSmallImage-IS.bmp
OutputDir={output_path}
OutputBaseFilename={APP_NAME}_Setup_v1.0
SetupIconFile={icon_abs_path}
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest
UninstallDisplayIcon={{app}}\\{APP_NAME}.exe

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked
Name: "startwindows"; Description: "Start with Windows"; GroupDescription: "Startup Options"; Flags: unchecked
Name: "startbackground"; Description: "Start in Background (System Tray)"; GroupDescription: "Startup Options"; Flags: unchecked

[Files]
Source: "{dist_path}\\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{{autoprograms}}\\{APP_NAME}"; Filename: "{{app}}\\{APP_NAME}.exe"
Name: "{{autodesktop}}\\{APP_NAME}"; Filename: "{{app}}\\{APP_NAME}.exe"; Tasks: desktopicon

[Run]
; Run with start in background flag if selected
Filename: "{{app}}\\{APP_NAME}.exe"; Description: "{{cm:LaunchProgram,{APP_NAME}}}"; Flags: nowait postinstall skipifsilent

[Registry]
; Start With Windows Logic (If Task Selected) - TRIPLE QUOTE FIX APPLIED
Root: HKCU; Subkey: "Software\\Microsoft\\Windows\\CurrentVersion\\Run"; ValueType: string; ValueName: "{APP_NAME}"; ValueData: {q}{q}{q}{{app}}\\{APP_NAME}.exe{q}{q}{q}; Flags: uninsdeletevalue; Tasks: startwindows

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
  if RegQueryStringValue(HKCU, 'Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{{{APP_NAME}_H4}}_is1', 'UninstallString', sUnInstPath) then
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
    V := MsgBox('Clp-CACHE is already installed.' + #13#10 + #13#10 +
                'Click "Yes" to UNINSTALL standard version.' + #13#10 +
                'Click "No" to UPDATE / REPAIR existing installation.', mbInformation, MB_YESNOCANCEL);
                
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
"""
    
    with open("setup_script.iss", "w") as f:
        f.write(iss_content)
    
    print("[BUILD] Inno Setup script 'setup_script.iss' created.")
    
    # Attempt to compile if ISCC is in path
    iscc_path = shutil.which("iscc")
    if iscc_path:
        print(f"[BUILD] Found Inno Setup Compiler at {iscc_path}. Compiling...")
        try:
            subprocess.check_call([iscc_path, "setup_script.iss"])
            print(f"[SUCCESS] Installer created at {output_path}")
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Inno Setup Compilation Failed: {e}")
    else:
        print("NOTE: 'iscc' (Inno Setup) not found in PATH. Please compile 'setup_script.iss' manually.")

if __name__ == "__main__":
    try:
        clean_build()
        run_pyinstaller()
        create_inno_script()
        print("\n[SUCCESS] Build process finished.")
    except Exception as e:
        print(f"\n[ERROR] Build failed: {e}")

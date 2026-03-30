# ------------------------------------------------------------------------------
# COPYRIGHT (C) 2026 h4. ALL RIGHTS RESERVED.
#
# This software is provided under a SOURCE-AVAILABLE COMMERCIAL LICENSE.
# You may view and use this code for personal, non-commercial purposes only.
#
# ANY COMMERCIAL USE, REDISTRIBUTION, OR DERIVATIVE WORK FOR FINANCIAL GAIN
# REQUIRES A 50% ROYALTY PAYMENT TO THE AUTHOR (h4) FROM THE FIRST DOLLAR EARNED.
#
# See LICENSE.md for full legal terms and royalty obligations.
# ------------------------------------------------------------------------------

import sys
import os
import subprocess

# --- GLOBAL STEALTH PATCH ---
# Forces any "nvidia-smi" call to use CREATE_NO_WINDOW and SW_HIDE
# This prevents flashing terminals from GPUtil or other libs.
if os.name == 'nt':
    _original_Popen = subprocess.Popen

    class SafePopen(subprocess.Popen):
        def __init__(self, *args, **kwargs):
            is_target = False
            # Check args for nvidia-smi
            cmd_args = args[0] if args else kwargs.get('args')
            if cmd_args:
                # Handle list or string
                if isinstance(cmd_args, list):
                    cmd_str = " ".join(str(x) for x in cmd_args).lower()
                else:
                    cmd_str = str(cmd_args).lower()
                
                if 'nvidia-smi' in cmd_str:
                    is_target = True

            if is_target:
                # 1. Creation Flags
                flags = kwargs.get('creationflags', 0)
                kwargs['creationflags'] = flags | 0x08000000 # CREATE_NO_WINDOW
                
                # 2. Startup Info (SW_HIDE)
                startupinfo = kwargs.get('startupinfo')
                if not startupinfo:
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    startupinfo.wShowWindow = subprocess.SW_HIDE
                kwargs['startupinfo'] = startupinfo
                
                # 3. Ensure shell=True doesn't override concealment if possible, 
                # but usually shell=True IS the cause of the window.
                # If we can run without shell, it's better. But GPUtil might rely on it.
                # CREATE_NO_WINDOW works with shell=True on modern Windows usually.

            super().__init__(*args, **kwargs)

    subprocess.Popen = SafePopen
# ----------------------------
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QFile, QTextStream

# Add src to path if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.database import DatabaseManager
from src.core.clipboard_manager import ClipboardManager
from src.core.monitor import SystemMonitor
from src.core.watchdog import MemoryWatchdog
from src.core.vault import VaultManager # Explicit import for PyInstaller
from src.ui.main_window import MainWindow
from src.ui.tray import SystemTray
from src.ui.theme_manager import ThemeManager

# Global Hotkey
from pynput import keyboard

from src.core.config import ConfigManager
from PyQt6.QtCore import QObject, pyqtSignal

class ClipCacheApp(QObject):
    # Signal to trigger window toggle from worker thread
    hotkey_signal = pyqtSignal()

    def __init__(self, start_in_background_override=False):
        super().__init__()
        
        # Windows Taskbar Icon Fix (AppUserModelID)
        try:
            import ctypes
            myappid = u'h4.clipcache.cyberpunk.v1' # arbitrary string
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

        print("[INIT] Creating QApplication...")
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        self.check_single_instance()
        
        self.last_hotkey_time = 0
        self.hotkey_signal.connect(self.toggle_window)
        
        def resolve_resource_path(relative_path):
            if hasattr(sys, '_MEIPASS'):
                return os.path.join(sys._MEIPASS, relative_path)
            
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            candidate = os.path.join(base_path, relative_path)
            if os.path.exists(candidate):
                return candidate
                
            if getattr(sys, 'frozen', False):
                base_path = os.path.dirname(sys.executable)
                candidate = os.path.join(base_path, relative_path)
                if os.path.exists(candidate):
                    return candidate
            
            return os.path.abspath(relative_path)
            
        self.resolve_resource_path = resolve_resource_path

        from PyQt6.QtGui import QIcon
        icon_path = self.resolve_resource_path(os.path.join("assets", "image_assets", "icon.ico"))
        if os.path.exists(icon_path):
            self.app.setWindowIcon(QIcon(icon_path))
        else:
            print(f"[ERROR] Icon not found at: {icon_path}")
        
        self.config = ConfigManager()
        
        print("[INIT] Loading Styles...")
        saved_theme = self.config.get_theme()
        self.load_stylesheet(saved_theme)
        
        print("[INIT] Applying Theme: " + saved_theme)
        
        print("[INIT] Initializing DB...")
        self.db = DatabaseManager() 
        print("[INIT] Initializing Clipboard...")
        self.clipboard = ClipboardManager(self.db)
        print("[INIT] Initializing Monitor (Threaded)...")
        self.monitor = SystemMonitor()
        print("[INIT] Initializing Watchdog...")
        self.watchdog = MemoryWatchdog()
        self.watchdog.start()
        
        print("[INIT] Initializing Themes...")
        self.themes = ThemeManager()
        print("[INIT] Initializing Main Window...")
        self.window = MainWindow(self.db, self.clipboard)
        
        print("[INIT] Initializing Tray...")
        self.tray = SystemTray(self.monitor, self)
        
        self.window.minimized.connect(self.on_window_minimized)
        
        print("[INIT] Starting Hotkey Listener...")
        from pynput.keyboard import Key, Listener, KeyCode
        
        self.ctrl_pressed = False
        self.shift_pressed = False
        
        def on_press(key):
            if key == Key.ctrl_l or key == Key.ctrl_r:
                self.ctrl_pressed = True
            elif key == Key.shift_l or key == Key.shift_r:
                self.shift_pressed = True
            elif hasattr(key, 'vk') and key.vk == 107:
                if self.ctrl_pressed and self.shift_pressed:
                    print("[HOTKEY] TRIGGERED! Emitting signal...")
                    self.on_hotkey()
        
        def on_release(key):
            if key == Key.ctrl_l or key == Key.ctrl_r:
                self.ctrl_pressed = False
            elif key == Key.shift_l or key == Key.shift_r:
                self.shift_pressed = False
        
        self.listener = Listener(on_press=on_press, on_release=on_release)
        self.listener.start()
        
        should_start_bg = start_in_background_override or self.config.get_start_in_background()
        
        if should_start_bg:
            print("[INIT] Starting in Background (minimized to tray)")
            if self.config.get_incognito_mode():
                self.tray.hide()
            else:
                self.tray.show()
        else:
            self.window.show()
            self.tray.show()
        
        print("[INIT] Ready to Run.")

    def on_window_minimized(self):
        is_incognito = self.config.get_incognito_mode()
        print(f"[MAIN] Window Minimized. Incognito Mode: {is_incognito}")
        
        self.window.hide()
        
        if is_incognito:
            self.tray.hide()
            print("[MAIN] Tray Hidden (Incognito).")
        else:
            self.tray.show()
            print("[MAIN] Tray Visible.")

    def load_stylesheet(self, theme_name="Cyberpunk Neon"):
        print(f"[INIT] Applying Theme: {theme_name}")
        stylesheet = ThemeManager.get_stylesheet(theme_name)
        self.app.setStyleSheet(stylesheet)

    def on_hotkey(self):
        import time
        current_time = time.time()
        if current_time - self.last_hotkey_time < 0.5:
             print("[HOTKEY] Ignored (Debounce)")
             return
        self.last_hotkey_time = current_time
        
        self.hotkey_signal.emit()

    def toggle_window(self):
        print(f"[HOTKEY] toggle_window called. isVisible: {self.window.isVisible()}, isMinimized: {self.window.isMinimized()}")
        
        if self.window.isVisible() and not self.window.isMinimized():
            self.window.hide()
            if self.config.get_incognito_mode():
                self.tray.hide()
                print("[HOTKEY] Window Hidden + Tray Hidden (Incognito)")
            else:
                self.tray.show()
                print("[HOTKEY] Window Hidden + Tray Visible")
        else:
            self.window.show()
            self.window.showNormal()
            self.tray.show()
            
            try:
                import win32gui
                import win32con
                
                hwnd = int(self.window.winId())
                
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
                win32gui.BringWindowToTop(hwnd)
                
                print(f"[HOTKEY] Window forced to foreground via win32 (hwnd: {hwnd})")
            except Exception as e:
                print(f"[HOTKEY] Win32 foreground failed: {e}")
                self.window.activateWindow()
                self.window.raise_()
            
            self.window.setFocus()
            print("[HOTKEY] Window shown and activated")

    def show_about(self):
        from src.ui.about_window import AboutWindow
        self.about_win = AboutWindow()
        self.about_win.show() 

    def show_help(self):
        from src.ui.help_window import HelpWindow
        self.help_win = HelpWindow()
        self.help_win.show()

    def quit_app(self):
        self.listener.stop()
        self.app.quit()
        
    def quit_and_purge(self):
        self.db.clear_history()
        self.quit_app()

    def check_single_instance(self):
        import psutil
        import os
        
        current_pid = os.getpid()
        found_proc = None
        
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                if proc.info['pid'] == current_pid:
                    continue
                
                proc_exe = proc.info.get('exe')
                
                if proc_exe and sys.executable and os.path.normpath(proc_exe) == os.path.normpath(sys.executable):
                    found_proc = proc
                    break
                    
                if getattr(sys, 'frozen', False):
                     if proc.info['name'] and "Clip-CACHE" in proc.info['name']:
                         found_proc = proc
                         break
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
                
        if found_proc:
            print(f"[INIT] SingleInstance: Found duplicate PID {found_proc.pid}")
            
            msg = QMessageBox()
            msg.setWindowTitle("Duplicate Instance Detected")
            msg.setText(f"Another instance of Clip-CACHE is already running (PID {found_proc.pid}).\n\nWhat would you like to do?")
            msg.setIcon(QMessageBox.Icon.Warning)
            
            btn_stop = msg.addButton("Stop Opening", QMessageBox.ButtonRole.RejectRole)
            btn_close_run = msg.addButton("Close Running", QMessageBox.ButtonRole.DestructiveRole)
            btn_nothing = msg.addButton("Do Nothing", QMessageBox.ButtonRole.ActionRole)
            
            msg.exec()
            
            if msg.clickedButton() == btn_stop:
                print("[INIT] User selected STOP. Exiting.")
                sys.exit(0)
            elif msg.clickedButton() == btn_nothing:
                print("[INIT] User selected DO NOTHING. Exiting.")
                sys.exit(0)
            elif msg.clickedButton() == btn_close_run:
                print(f"[INIT] User selected CLOSE RUNNING. Terminating PID {found_proc.pid}...")
                try:
                    found_proc.terminate()
                    found_proc.wait(timeout=3)
                except Exception as e:
                    print(f"Failed to terminate: {e}")
                    QMessageBox.critical(None, "Error", f"Failed to close running instance:\n{e}")
                    sys.exit(1)

    def run(self):
        sys.exit(self.app.exec())

def main(start_in_background=False):
    app = ClipCacheApp(start_in_background_override=start_in_background)
    
    if start_in_background:
        print("[INIT] Forced Background Start via Argument")
    
    app.run()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        import datetime
        
        desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop') 
        crash_file = os.path.join(desktop, "ClipCACHE_CRASH_LOG.txt")
        
        with open(crash_file, "w") as f:
            f.write(f"CRASH TIME: {datetime.datetime.now()}\n")
            f.write(f"ERROR: {str(e)}\n")
            f.write("-" * 50 + "\n")
            f.write(traceback.format_exc())
            
        # Also try to show a message box if possible
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, f"Critical Crash! Log saved to Desktop: {crash_file}\n\nError: {e}", "Clip-CACHE Crash", 0x10)
        except:
            pass
        sys.exit(1)

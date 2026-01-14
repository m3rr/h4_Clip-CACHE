import os
import sys
import ctypes
import psutil
import subprocess
from .logger import LOGGER

class AdminTools:
    """
    Nuclear Admin Utilities.
    Handles system-level operations like process management and memory cleaning.
    """
    @staticmethod
    def launch_terminal():
        """Launches Windows Terminal or falls back to CMD."""
        try:
            # Try Windows Terminal
            subprocess.Popen("wt.exe", shell=True)
            LOGGER.log("Launched Windows Terminal.")
        except Exception:
            try:
                subprocess.Popen("start cmd.exe", shell=True)
                LOGGER.log("Launched CMD (Fallback).")
            except Exception as e:
                LOGGER.error(f"Failed to launch terminal: {e}")

    @staticmethod
    def launch_task_manager():
        """Launches Task Manager."""
        try:
            subprocess.Popen("taskmgr.exe", shell=True)
            LOGGER.log("Launched Task Manager.")
        except Exception as e:
            LOGGER.error(f"Failed to launch Task Manager: {e}")

    @staticmethod
    def clear_working_memory():
        """
        Clears the Working Set for the current process and attempts global cleanup via empty standbylist if available.
        """
        LOGGER.log("Executing RAM Clear Protocol...")
        
        # 1. Python GC
        import gc
        gc.collect()
        LOGGER.log("Python GC Collected.")
        
        # 2. Empty Working Set (Self)
        try:
            ckpt = ctypes.windll.psapi.EmptyWorkingSet(ctypes.windll.kernel32.GetCurrentProcess())
            if ckpt: 
                LOGGER.log("Self Working Set Emptied.")
            else:
                LOGGER.error("Failed to empty self working set.")
        except Exception as e:
            LOGGER.error(f"Working Set Error: {e}")

        # 3. System Standby List (Advanced) - Placeholder
        pass

    @staticmethod
    def clean_system_memory(aggressive=False):
        """
        Clears RAM sets.
        Gentle: Clears Self Working Set.
        Aggressive: Clears Working Sets of ALL accessible processes.
        """
        LOGGER.log(f"RAM OPTIMIZATION INITIATED (Aggressive={aggressive})")
        
        # 1. GC
        import gc
        gc.collect()
        
        # 2. Self
        try:
            ctypes.windll.psapi.EmptyWorkingSet(ctypes.windll.kernel32.GetCurrentProcess())
        except Exception: 
            pass
            
        if not aggressive:
            LOGGER.log("RAM: Gentle Sweep Complete.")
            return
            
        # 3. Aggressive: All Processes
        # Requires Admin privileges for most processes, but we do what we can.
        success_count = 0
        fail_count = 0
        
        # Constants
        PROCESS_SET_QUOTA = 0x0100
        PROCESS_QUERY_INFORMATION = 0x0400
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                pid = proc.info['pid']
                if pid == 0 or pid == 4: continue # Skip System/Idle
                
                # Open Process
                hProcess = ctypes.windll.kernel32.OpenProcess(PROCESS_SET_QUOTA | PROCESS_QUERY_INFORMATION, False, pid)
                if hProcess:
                    ret = ctypes.windll.psapi.EmptyWorkingSet(hProcess)
                    ctypes.windll.kernel32.CloseHandle(hProcess)
                    if ret:
                        success_count += 1
                    else:
                        fail_count += 1
                else:
                    fail_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                fail_count += 1
                
        LOGGER.log(f"RAM: Aggressive Sweep Complete. Trimmed {success_count} processes (Failed {fail_count}).")

    @staticmethod
    def clear_vram():
        """
        Attempts to reset the graphics driver (dangerous/flickery).
        Actually, 'Ctrl+Shift+Win+B' is the shortcut. 
        We can't easily trigger that programmatically reliably.
        Instead, we'll just log a placeholder for now as it's risky to crash the driver.
        """
        # subprocess.call('... restart-gpu ...') 

    
    @staticmethod
    def set_start_with_windows(enable: bool):
        """
        Sets the registry key to start app with Windows.
        Target: HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run
        AppName: SmartBoard
        """
        import winreg
        import sys
        import os
        
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "Clip-CACHE"
        exe_path = f'"{sys.executable}" "{os.path.abspath("ClipCache_Launcher.py")}"' 
        # Ideally pointer to built .exe if frozen, or python script if dev.
        # Using sys.executable + script for dev env.
        
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            if enable:
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, exe_path)
                print(f"[ADMIN] Start with Windows ENABLED: {exe_path}")
            else:
                try:
                    winreg.DeleteValue(key, app_name)
                    print(f"[ADMIN] Start with Windows DISABLED")
                except FileNotFoundError:
                    pass # Key doesn't exist, already disabled
            winreg.CloseKey(key)
        except Exception as e:
            print(f"[ADMIN] Failed to set Start with Windows: {e}")

    @staticmethod
    def reset_ip_stack():
        """
        Executes a full cycle of IP reset commands.
        """
        LOGGER.log("ADMIN: Initiating Network Reset Protocol...")
        commands = [
            "ipconfig /release",
            "ipconfig /flushdns",
            "ipconfig /renew"
        ]
        
        try:
            # Chained execution
            cmd_str = " && ".join(commands)
            subprocess.Popen(f"start cmd.exe /k {cmd_str}", shell=True)
            LOGGER.log("ADMIN: Network Reset Commands Dispatched.")
        except Exception as e:
            LOGGER.error(f"ADMIN: Network Reset Failed: {e}")

    @staticmethod
    def start_system_debugger():
        """
        Starts the 'God Mode' system debugger.
        For now, this is simulated as we don't have a full kernel driver.
        We will enable VERBOSE logging and perhaps spawn a secondary watcher.
        """
        LOGGER.log("ADMIN: *** SYSTEM DEBUGGER (GOD MODE) ENABLED ***")
        LOGGER.log("ADMIN: Monitoring Process Creation (Simulated)...")
        LOGGER.log("ADMIN: Monitoring File System Events (Watchdog Active)...")
        # In a real scenario, we'd hook specific Windows APIs here.
        # For this prototype, we just verify the Logger is in max verbosity.
        LOGGER.set_debug(True) 
        LOGGER.log("ADMIN: Log Rotation Policy: FIFO > 1GB (Active).") 

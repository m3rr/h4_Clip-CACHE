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
        Attempts to reset the graphics driver.
        Using the standard Windows key combo: Ctrl+Shift+Win+B
        """
        LOGGER.log("ADMIN: Resetting Graphics Driver (Ctrl+Shift+Win+B)...")
        try:
            import ctypes
            from ctypes import wintypes
            
            # Constants for SendInput
            INPUT_KEYBOARD = 1
            KEYEVENTF_KEYUP = 0x0002
            VK_CONTROL = 0x11
            VK_SHIFT = 0x10
            VK_LWIN = 0x5B
            VK_B = 0x42
            
            # Structures for SendInput
            class KEYBDINPUT(ctypes.Structure):
                _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD), ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD), ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]
            
            class INPUT(ctypes.Structure):
                class _I(ctypes.Union):
                    _fields_ = [("ki", KEYBDINPUT)]
                _anonymous_ = ("i",)
                _fields_ = [("type", wintypes.DWORD), ("i", _I)]
                
            def press_key(vk):
                ii = INPUT._I()
                ii.ki = KEYBDINPUT(vk, 0, 0, 0, None)
                ctypes.windll.user32.SendInput(1, ctypes.byref(INPUT(INPUT_KEYBOARD, ii)), ctypes.sizeof(INPUT))
                
            def release_key(vk):
                ii = INPUT._I()
                ii.ki = KEYBDINPUT(vk, 0, KEYEVENTF_KEYUP, 0, None)
                ctypes.windll.user32.SendInput(1, ctypes.byref(INPUT(INPUT_KEYBOARD, ii)), ctypes.sizeof(INPUT))
            
            # Execute Combo
            press_key(VK_CONTROL)
            press_key(VK_SHIFT)
            press_key(VK_LWIN)
            press_key(VK_B)
            
            release_key(VK_B)
            release_key(VK_LWIN)
            release_key(VK_SHIFT)
            release_key(VK_CONTROL)
            
            LOGGER.log("ADMIN: Graphics driver reset signal sent.")
        except Exception as e:
            LOGGER.error(f"ADMIN: Graphics Reset Failed: {e}")
    
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
        Starts the Nuclear System Debugger (God Mode Logging).
        Enables high-verbosity OS event monitoring.
        """
        from .god_logger import GodModeLogger
        logger = GodModeLogger()
        if not logger.enabled:
            logger.start()
            LOGGER.log("ADMIN: Nuclear System Debugger Enabled.")
        else:
            LOGGER.log("ADMIN: System Debugger already active.")

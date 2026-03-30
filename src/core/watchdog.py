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

import psutil
import os
import sys
import time
import threading
from PyQt6.QtCore import QObject, pyqtSignal

class MemoryWatchdog(QObject):
    """
    Monitors the APPLICATION'S OWN memory usage.
    Triggers 'warning' @ 1GB.
    Triggers 'restart' @ 1.2GB.
    """
    memory_warning = pyqtSignal(float) # Emits MB usage
    
    def __init__(self, interval=2.0):
        super().__init__()
        self.interval = interval
        self.process = psutil.Process(os.getpid())
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)

    @staticmethod
    def simulate_bloat():
        """
        Intentionally bloats memory to test the watchdog/failsafe.
        Allocates ~1.5GB of data.
        """
        print("[WATCHDOG] SIMULATING BLOAT... HOLD ON.")
        global _bloat_list
        _bloat_list = []
        try:
            # allocate 100MB chunks until death
            for i in range(15):
                _bloat_list.append(bytearray(1024 * 1024 * 100)) # 100MB
                print(f"[WATCHDOG] Bloat: {len(_bloat_list)*100} MB")
        except Exception as e:
            print(f"[WATCHDOG] Bloat stopped: {e}")

    def start(self):
        self.thread.start()

    def _monitor_loop(self):
        while self.running:
            try:
                # RSS (Resident Set Size) is the non-swapped physical memory a process has used.
                mem_bytes = self.process.memory_info().rss
                mem_mb = mem_bytes / (1024 * 1024)
                
                # Logic: Warn @ 1000MB (1GB), Restart @ 1200MB (1.2GB)
                if mem_mb > 1200:
                    print(f"[WATCHDOG] CRITICAL: Memory usage {mem_mb:.2f}MB > 1200MB. RESTARTING...")
                    self._restart_application()
                elif mem_mb > 1000:
                    print(f"[WATCHDOG] WARNING: Memory usage {mem_mb:.2f}MB > 1000MB.")
                    self.memory_warning.emit(mem_mb)
                
            except Exception as e:
                print(f"[WATCHDOG] Error: {e}")
            
            time.sleep(self.interval)

    def _restart_application(self):
        """
        Restarts the current application instance.
        """
        try:
            print("[WATCHDOG] Initiating Nuclear Restart...")
            python = sys.executable
            os.execl(python, python, *sys.argv)
        except Exception as e:
            print(f"[WATCHDOG] Restart Failed: {e}")
            sys.exit(1)

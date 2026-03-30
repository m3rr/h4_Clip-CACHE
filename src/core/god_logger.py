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

import logging
import os
import sys
import datetime
import time
import threading
import psutil
from logging.handlers import RotatingFileHandler

# Try importing win32 for window monitoring
try:
    import win32gui
    import win32process
except ImportError:
    win32gui = None

class GodModeLogger:
    """
    NUCLEAR-LEVEL DEBUGGER (God Mode)
    - Captures everything: System events, Exceptions, Process Activity, Window Focus.
    - Rotating Logs: 5 Files x 500MB.
    - Format: ASCII Art Headers, Contextual Tags, High Verbosity.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GodModeLogger, cls).__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.enabled = False
        self.logger = logging.getLogger("GodMode")
        self.logger.setLevel(logging.DEBUG)
        self.log_dir = os.path.join(os.getcwd(), "logs")
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            
        self.setup_handlers()
        
        # Monitoring State
        self.monitor_thread = None
        self.stop_event = threading.Event()
        
        # Cache for diffing
        self.known_pids = set()
        self.last_window = None

    def setup_handlers(self):
        # Format: h4_ClipCACH-LOGS(#).log
        log_file = os.path.join(self.log_dir, "h4_ClipCACH-LOGS.log")
        
        # 500 MB = 500 * 1024 * 1024 bytes
        max_bytes = 500 * 1024 * 1024 
        
        handler = RotatingFileHandler(
            log_file, 
            maxBytes=max_bytes, 
            backupCount=5,
            encoding='utf-8'
        )
        
        # Custom Formatter for ASCII/Context
        formatter = GodFormatter()
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)

    def start(self):
        if self.enabled: return
        self.enabled = True
        self.log_ascii_header()
        self.log_system("GOD MODE ENABLED", "NUCLEAR MONITORING ACTIVE")
        
        # Hook Exceptions
        sys.excepthook = self.handle_exception
        
        # Start OS Monitoring Thread
        self.stop_event.clear()
        self.monitor_thread = threading.Thread(target=self._os_monitor_loop, daemon=True)
        self.monitor_thread.start()

    def stop(self):
        if not self.enabled: return
        self.log_system("GOD MODE DISABLED", "Monitoring Stopped")
        self.enabled = False
        if self.monitor_thread:
            self.stop_event.set()
            self.monitor_thread.join(timeout=2.0)
            self.monitor_thread = None

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        if not self.enabled:
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        import traceback
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        tb_text = "".join(tb_lines)
        
        self.log_error("UNCAUGHT EXCEPTION", f"{exc_type.__name__}: {exc_value}\n{tb_text}")
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    def _os_monitor_loop(self):
        """
        Background loop for OS monitoring.
        """
        self.known_pids = set(psutil.pids())
        self.log_system("OS SNAPSHOT", f"Initial Process Count: {len(self.known_pids)}")
        
        frame_count = 0
        
        while not self.stop_event.is_set():
            try:
                self._check_window_focus()
                
                if frame_count % 4 == 0:
                    self._check_processes()
                
                if frame_count % 10 == 0:
                    self._check_telemetry()
                
                frame_count += 1
                time.sleep(0.5)
                
            except Exception as e:
                self.log_error("MONITOR THREAD ERROR", str(e))
                time.sleep(1)

    def _check_window_focus(self):
        if not win32gui: return
        
        try:
            hwnd = win32gui.GetForegroundWindow()
            if hwnd != self.last_window:
                self.last_window = hwnd
                title = win32gui.GetWindowText(hwnd)
                
                # Get PID of window
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                try:
                    proc = psutil.Process(pid)
                    proc_name = proc.name()
                except:
                    proc_name = "Unknown"
                
                if title:
                    self.log_system("WINDOW FOCUS", f"'{title}' ({proc_name} : {pid})")
        except Exception:
            pass

    def _check_processes(self):
        current_pids = set(psutil.pids())
        
        # New Processes
        new_pids = current_pids - self.known_pids
        for pid in new_pids:
            try:
                p = psutil.Process(pid)
                self.log_app("PROCESS STARTED", f"{p.name()} (PID: {pid})")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Dead Processes
        dead_pids = self.known_pids - current_pids
        for pid in dead_pids:
            # We can't get name of dead process usually, unless we cached it.
            # For now just logging PID is fine or "Process Terminated"
            self.log_app("PROCESS ENDED", f"PID: {pid}")
            
        self.known_pids = current_pids

    def _check_telemetry(self):
        # Disk IO
        io = psutil.disk_io_counters()
        if io:
            self.log_system("DISK I/O", f"Read: {io.read_bytes // 1024 // 1024} MB | Write: {io.write_bytes // 1024 // 1024} MB")

    def log_ascii_header(self):
        header = r"""
  ___________________________________________________________
 /                                                           \
|    _____  ____  _____     __  __  ____  ____  ______        |
|   / ____|/ __ \|  __ \   |  \/  |/ __ \|  _ \|  ____|       |
|  | |  __| |  | | |  | |  | \  / | |  | | | | | |__          |
|  | | |_ | |  | | |  | |  | |\/| | |  | | | | |  __|         |
|  | |__| | |__| | |__| |  | |  | | |__| | |_| | |____        |
|   \_____|\____/|_____/   |_|  |_|\____/|____/|______|       |
|                                                             |
 \___________________________________________________________/
        """
        self.logger.info(header)

    # --- CATEGORIZED LOGGING METHODS ---
    
    def log_system(self, event, details=""):
        if not self.enabled: return
        self.logger.info(f"[SYSTEM]  :: {event:<20} :: {details}")

    def log_app(self, event, details=""):
        if not self.enabled: return
        self.logger.info(f"[APP]     :: {event:<20} :: {details}")
        
    def log_error(self, event, details=""):
        if not self.enabled: return
        self.logger.error(f"[ERROR]   :: {event:<20} :: {details}")
        
    def log_success(self, event, details=""):
        if not self.enabled: return
        self.logger.info(f"[SUCCESS] :: {event:<20} :: {details}")
        
    def log_warn(self, event, details=""):
        if not self.enabled: return
        self.logger.warning(f"[WARNING] :: {event:<20} :: {details}")


class GodFormatter(logging.Formatter):
    def format(self, record):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        return f"[{timestamp}] {record.msg}"

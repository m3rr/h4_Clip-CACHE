import psutil
import time
import threading
from .logger import LOGGER

# Try importing GPU libs, handle failure gracefully
try:
    import GPUtil
except ImportError:
    GPUtil = None

try:
    import wmi
except ImportError:
    wmi = None

import subprocess
import os


class SystemMonitor:

    """
    NUCLEAR LEVEL MONITORING (THREADED REFAC).
    Retrieves CPU, RAM, GPU, and Network statistics.
    Runs polling in a background thread to prevent UI hangs.
    """
    def __init__(self):
        LOGGER.log("SystemMonitor Initializing...")
        self.stats = {
            'cpu': 0.0, 'ram_percent': 0.0, 'ram_used_gb': 0.0,
            'gpu_temp': "N/A", 'net_down': "0 B/s", 'net_up': "0 B/s"
        }
        
        self.last_net_io = psutil.net_io_counters()
        self.last_net_time = time.time()
        
        # WMI init moved to thread
        self.wmi_interface = None

        self.running = True
        self.lock = threading.Lock()
        
        # Start Polling Thread
        self.thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.thread.start()
        LOGGER.log("SystemMonitor Polling Thread Started.")

    def get_stats(self):
        """Returns the cached stats instantly."""
        # Use simple acquire with timeout logic if crucial, but simple release is better.
        # We trust the thread not to hang holding the lock.
        if self.lock.acquire(blocking=True, timeout=0.1):
            try:
                return self.stats.copy()
            finally:
                self.lock.release()
        else:
            LOGGER.error("Monitor Lock Timeout!")
            return self.stats.copy() # Return stale data rather than hanging

    def _poll_loop(self):
        # Lazy Init WMI in thread
        if wmi and self.wmi_interface is None:
            try:
                LOGGER.log("Thread: Init WMI...")
                self.wmi_interface = wmi.WMI()
                LOGGER.log("Thread: WMI Ready.")
            except Exception as e:
                LOGGER.error(f"Thread: WMI Init Failed: {e}")

        while self.running:
            try:
                new_stats = {}
                
                # --- CPU ---
                try:
                    # Interval 0.1 allows it to blocking-measure for 100ms or so, 
                    # but inside a thread it's fine. 
                    # 'interval=None' is instant but requires previous calls.
                    # We want accurate load, so small interval is good.
                    new_stats['cpu'] = psutil.cpu_percent(interval=0.5)
                except Exception as e:
                    LOGGER.error(f"CPU Poll Error: {e}")
                    new_stats['cpu'] = 0.0

                # --- RAM ---
                try:
                    mem = psutil.virtual_memory()
                    new_stats['ram_percent'] = mem.percent
                    new_stats['ram_used_gb'] = round(mem.used / (1024**3), 2)
                    new_stats['ram_total_gb'] = round(mem.total / (1024**3), 1)
                except Exception as e:
                    LOGGER.error(f"RAM Poll Error: {e}")
                    new_stats['ram_percent'] = 0.0

                # --- GPU ---
                gpu_temp = "N/A"
                try:
                    if GPUtil:
                        gpus = GPUtil.getGPUs()
                        if gpus:
                            gpu_temp = gpus[0].temperature
                except Exception as e:
                    # GPUtil can throw on some systems
                    LOGGER.log(f"GPUtil Error (Non-Critical): {e}")

                if gpu_temp == "N/A" and self.wmi_interface:
                    # WMI calls can be VERY slow, hence why we thread this.
                    try:
                        # Placeholder for WMI temp check logic if we want to risk it
                        # For now, skipping to avoid "Hanging" unless explicitly requested
                        pass 
                    except Exception:
                        pass
                
                new_stats['gpu_temp'] = gpu_temp

                # --- NETWORK ---
                try:
                    current_net_io = psutil.net_io_counters()
                    current_time = time.time()
                    dt = current_time - self.last_net_time
                    
                    if dt > 0:
                        bytes_recv = current_net_io.bytes_recv - self.last_net_io.bytes_recv
                        bytes_sent = current_net_io.bytes_sent - self.last_net_io.bytes_sent
                        
                        new_stats['net_down'] = self._format_bytes(bytes_recv / dt)
                        new_stats['net_up'] = self._format_bytes(bytes_sent / dt)
                    else:
                        new_stats['net_down'] = "0 B/s"
                        new_stats['net_up'] = "0 B/s"

                    self.last_net_io = current_net_io
                    self.last_net_time = current_time
                except Exception as e:
                     LOGGER.error(f"NET Poll Error: {e}")
                     new_stats['net_down'] = "N/A"
                     new_stats['net_up'] = "N/A"

                # Update Cache
                with self.lock:
                    self.stats.update(new_stats)
                
                LOGGER.log("Stats Updated", context=f"CPU: {new_stats.get('cpu')}%")

                # Extract for God Mode Logging
                cpu = new_stats.get('cpu', 0.0)
                ram_percent = new_stats.get('ram_percent', 0.0)
                ram_gb = new_stats.get('ram_used_gb', 0.0)

            except Exception as e:
                LOGGER.error(f"CRITICAL MONITOR LOOP ERROR: {e}")
            
            # Sleep a bit to not hammer CPU
            # --- GOD MODE LOGGING ---
            try:
                from .god_logger import GodModeLogger
                logger = GodModeLogger()
                if logger.enabled:
                    # Log RAM Spikes > 80%
                    if ram_percent > 80.0:
                        logger.log_warn("HIGH MEMORY USAGE", f"{ram_percent}% Used ({ram_gb:.2f} GB)")
                    
                    # Log CPU Spikes > 90%
                    if cpu > 90.0:
                        logger.log_warn("HIGH CPU LOAD", f"Load: {cpu}%")
                        
                    # Periodic Heartbeat (every ~60 polls = ~60s)
                    if not hasattr(self, '_poll_count'): self._poll_count = 0
                    self._poll_count += 1
                    if self._poll_count % 60 == 0:
                        logger.log_system("MONITOR HEARTBEAT", f"CPU: {cpu}% | RAM: {ram_percent}%")
            except Exception:
                pass # Fail silently in poll loop
                
            time.sleep(1) # 1s Polling Rate

    def _format_bytes(self, size):
        power = 2**10
        n = 0
        power_labels = {0 : '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
        while size > power:
            size /= power
            n += 1
        return f"{size:.1f} {power_labels[n]}B/s"

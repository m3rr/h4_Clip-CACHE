import logging
import os
import sys
from datetime import datetime

class NuclearLogger:
    """
    NUCLEAR LEVEL LOGGING.
    Writes to console and file with extreme prejudice.
    """
    _instance = None
    
    @classmethod
    def get(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.debug_mode = False
        
        # Resolve to AppData
        app_data = os.getenv('LOCALAPPDATA')
        base_dir = os.path.join(app_data, 'h4', 'Clip-CACHE')
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        self.log_file = os.path.join(base_dir, "clipcache_nuclear.log")
        
        # Setup basic logging config
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(self.log_file, mode='w'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger("Nuclear")

    def set_debug(self, enabled: bool):
        self.debug_mode = enabled
        if enabled:
            self.log("NUCLEAR DEBUG MODE ENGAGED.")
        else:
            self.log("Nuclear Debug Mode Standby.")

    def log(self, message, context=None):
        if not self.debug_mode:
            return
            
        full_msg = f"{message}"
        if context:
            full_msg += f" | CTX: {context}"
            
        self.logger.debug(full_msg)

    def error(self, message):
        self.logger.error(message)

# Global accessor
LOGGER = NuclearLogger.get()

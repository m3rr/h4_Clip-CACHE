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
import shutil
import time
from datetime import datetime
from PyQt6.QtWidgets import QMessageBox
from .config import ConfigManager

class VaultManager:
    """
    The Bunker.
    Handles physical storage of Pinned items to %LOCALAPPDATA%/h4/Clip-CACHE/vault/.
    """
    
    def __init__(self):
        self.config = ConfigManager()
        
        # Base Path: %LOCALAPPDATA%/h4/Clip-CACHE/vault
        self.base_dir = os.path.join(os.getenv('LOCALAPPDATA'), 'h4', 'Clip-CACHE', 'vault')
        
        self.dirs = {
            'text': os.path.join(self.base_dir, 'text'),
            'image': os.path.join(self.base_dir, 'images'),
            'file': os.path.join(self.base_dir, 'files')
        }
        
        self._init_bunker()

    def _init_bunker(self):
        """Ensure the physical structure exists."""
        for path in self.dirs.values():
            if not os.path.exists(path):
                os.makedirs(path)

    def _get_timestamp(self):
        """Returns [DD-MM-YYYY_HHMMSS]"""
        return datetime.now().strftime("[%d-%m-%Y_%H%M%S]")

    def store_item(self, item_type, content):
        """
        Physically stores the item in the Vault.
        Returns the new absolute path to the stored item.
        """
        timestamp = self._get_timestamp()
        
        if item_type == 'text':
            # Create a text file
            filename = f"Snippet_{timestamp}.txt"
            target_path = os.path.join(self.dirs['text'], filename)
            
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            return target_path

        elif item_type == 'image':
            # Content is path to temp image
            if not os.path.exists(content):
                return None
                
            ext = os.path.splitext(content)[1] or ".png"
            filename = f"Img_{timestamp}{ext}"
            target_path = os.path.join(self.dirs['image'], filename)
            
            shutil.copy2(content, target_path)
            return target_path

        elif item_type == 'file':
            # Content is path to original file
            if not os.path.exists(content):
                return None
            
            # Size Check (500MB Limit Warning is handled by UI before calling this, 
            # or we enforce hard limit here? User said "Warn", implies we might proceed if user insists.
            # But let's assume this method is called AFTER confirmation).
            
            # Naming: <OriginalName>_[TIMESTAMP].<ext>
            base_name = os.path.basename(content)
            name, ext = os.path.splitext(base_name)
            
            # "superawesomefileextension" logic
            filename = f"{name}_{timestamp}{ext}"
            target_path = os.path.join(self.dirs['file'], filename)
            
            shutil.copy2(content, target_path)
            return target_path
            
        return None

    def delete_item(self, vault_path):
        """
        Destroy the physical copy.
        """
        if vault_path and os.path.exists(vault_path):
            try:
                os.remove(vault_path)
                return True
            except Exception as e:
                print(f"[VAULT] Failed to delete {vault_path}: {e}")
                return False
        return False

    def get_file_size_mb(self, file_path):
        if os.path.exists(file_path):
            return os.path.getsize(file_path) / (1024 * 1024)
        return 0

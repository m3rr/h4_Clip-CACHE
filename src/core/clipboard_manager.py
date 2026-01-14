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

from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QClipboard
import hashlib
import os
from .database import DatabaseManager

class ClipboardManager(QObject):
    """
    Monitors system clipboard and saves history to Database.
    Inherits QObject for signals.
    """
    history_updated = pyqtSignal() # Signal to UI to refresh

    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db = db_manager
        self.clipboard = QApplication.clipboard()
        
        # Debounce Timer to prevent duplicate signals/fires
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.setInterval(250) # 250ms delay
        self.debounce_timer.timeout.connect(self._process_clipboard)
        
        self.clipboard.dataChanged.connect(self._on_data_changed)
        self.last_hash = None 

    def _on_data_changed(self):
        """Called when system clipboard changes. Restart debounce."""
        self.debounce_timer.start()

    def _process_clipboard(self):
        """Actual processing after debounce."""
        mime_data = self.clipboard.mimeData()
        
        if mime_data.hasUrls():
            self._handle_files(mime_data)
        elif mime_data.hasImage():
            self._handle_image(mime_data)
        elif mime_data.hasText():
            self._handle_text(mime_data)

    def _handle_text(self, mime_data):
        text = mime_data.text()
        if not text.strip(): 
            return

        # Hash check to avoid duplicates/loops
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        if text_hash == self.last_hash:
            return
        self.last_hash = text_hash

        meta = {
            "char_count": len(text),
            "preview": text[:50] + "..." if len(text) > 50 else text
        }
        self.db.add_item("text", text, meta)
        self.history_updated.emit()
        print("[CLIPBOARD] Captured Text")

    def _handle_files(self, mime_data):
        urls = mime_data.urls()
        if not urls: return
        
        for url in urls:
            local_path = url.toLocalFile()
            if local_path and os.path.exists(local_path):
                # Hash check (simple path hash for files)
                file_hash = hashlib.md5(local_path.encode('utf-8')).hexdigest()
                if file_hash == self.last_hash:
                    continue
                self.last_hash = file_hash
                
                meta = {
                    "extension": os.path.splitext(local_path)[1],
                    "size_bytes": os.path.getsize(local_path)
                }
                self.db.add_item("file", local_path, meta)
        
        self.history_updated.emit()
        print(f"[CLIPBOARD] Captured {len(urls)} Files")

    def add_item(self, item_type, content):
        """
        Manual injection of item.
        Updates DB and internal hash state (to avoid loops if set to clipboard later).
        """
        # Calculate hash to sync state
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        self.last_hash = content_hash
        
        meta = {}
        if item_type == 'text':
            meta = {"char_count": len(content), "manual_entry": True}
        elif item_type == 'file':
            if os.path.exists(content):
                meta = {"extension": os.path.splitext(content)[1], "size_bytes": os.path.getsize(content), "manual_entry": True}
            else:
                meta = {"manual_entry": True, "error": "File not found"}
        
        self.db.add_item(item_type, content, meta)
        self.history_updated.emit()
        print(f"[CLIPBOARD] Manually Added {item_type}: {content[:30]}...")

    def _handle_image(self, mime_data):
        from PyQt6.QtCore import QBuffer, QIODevice
        image = self.clipboard.image()
        if image.isNull():
            return

        # Hash Image Bits to prevent duplicates
        ba = QBuffer()
        ba.open(QIODevice.OpenModeFlag.ReadWrite)
        image.save(ba, "PNG")
        data = ba.data()
        img_hash = hashlib.md5(data).hexdigest()
        
        if img_hash == self.last_hash:
            print("[CLIPBOARD] Duplicate Image Ignored")
            return
            
        self.last_hash = img_hash
        
        # Save to cache
        import time
        filename = f"img_{int(time.time()*1000)}.png"
        cache_dir = os.path.join("assets", "cache")
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)
            
        full_path = os.path.abspath(os.path.join(cache_dir, filename))
        image.save(full_path, "PNG")

        meta = {
            "width": image.width(),
            "height": image.height(),
            "size_bytes": os.path.getsize(full_path)
        }

        self.db.add_item("image", full_path, meta)
        self.history_updated.emit()
        print(f"[CLIPBOARD] Captured Image: {full_path}")

    def _handle_files(self, mime_data):
        urls = mime_data.urls()
        if not urls:
            return
            
        paths = [u.toLocalFile() for u in urls if u.isLocalFile()]
        if not paths:
            return

        # Hash path list to detect if this exact SET of files was just processed
        # Join sorted paths to ensure order doesn't matter
        paths_str = ";".join(sorted(paths))
        files_hash = hashlib.md5(paths_str.encode('utf-8')).hexdigest()
        
        if files_hash == self.last_hash:
            return
        self.last_hash = files_hash
        
        # Requirement: "keeps a history" - Do we want 1 item or N items?
        # User complained about "MULTIPLE entries". Let's group them into 1 item if > 1 file.
        # Or add them individually but ensure the SET check prevents re-adding.
        
        # Taking "MULTIPLE entries" complaint seriously -> Group them.
        
        full_path_str = ";".join(paths)
        meta = {
            "file_count": len(paths),
            "ext": os.path.splitext(paths[0])[1] if paths else "",
            "is_multiple": len(paths) > 1
        }
        
        self.db.add_item("file", full_path_str, meta)
        self.history_updated.emit()
        print(f"[CLIPBOARD] Captured {len(paths)} File(s)")

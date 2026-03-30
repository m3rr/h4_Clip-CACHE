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

import sqlite3
import os
import json
from datetime import datetime

class DatabaseManager:
    """
    Manages the SQLite database for clipboard history.
    Enforces a strict FIFO limit of 100 items.
    """
    def __init__(self, db_path=None):
        if db_path is None:
            # Resolve to AppData
            app_data = os.getenv('LOCALAPPDATA')
            base_dir = os.path.join(app_data, 'h4', 'Clip-CACHE')
            if not os.path.exists(base_dir):
                os.makedirs(base_dir)
            self.db_path = os.path.join(base_dir, "clipboard_history.db")
        else:
            self.db_path = db_path
            
        self._init_db()

    def _init_db(self):
        """Initialize the database tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # History Table
        # id: Auto increment
        # type: 'text', 'image', 'file'
        # content: The text content, or path to image/file, or bytes for small images (stored as blob if needed, but path pref)
        # timestamp: ISO format
        # pinned: 0 or 1
        # metadata: JSON string with extra details (size, hash, dimensions)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                content TEXT,
                timestamp TEXT,
                pinned INTEGER DEFAULT 0,
                metadata TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def add_item(self, item_type, content, metadata=None):
        """
        Add a new item to history.
        Prunes old items if count > 100 (excluding pinned).
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        meta_json = json.dumps(metadata) if metadata else "{}"

        # Insert new item
        cursor.execute('''
            INSERT INTO history (type, content, timestamp, metadata)
            VALUES (?, ?, ?, ?)
        ''', (item_type, content, timestamp, meta_json))
        
        conn.commit()
        
        # Prune Logic
        self._prune(cursor)
        
        conn.commit()
        conn.close()

    def _prune(self, cursor):
        """
        Ensure only 100 non-pinned items exist.
        Deletes the oldest non-pinned items.
        """
        # Count non-pinned items
        cursor.execute('SELECT COUNT(*) FROM history WHERE pinned = 0')
        count = cursor.fetchone()[0]
        
        if count > 100:
            limit = count - 100
            # Delete the oldest N items that are NOT pinned
            # SQLite supports LIMIT in DELETE if enabled, but standard SQL:
            # DELETE FROM history WHERE id IN (SELECT id FROM history WHERE pinned=0 ORDER BY id ASC LIMIT N)
            cursor.execute(f'''
                DELETE FROM history 
                WHERE id IN (
                    SELECT id FROM history 
                    WHERE pinned = 0 
                    ORDER BY id ASC 
                    LIMIT {limit}
                )
            ''')
            print(f"[DATABASE] Pruned {limit} old items.")

    def get_history(self, filter_type=None):
        """Fetch history, optionally filtered by type."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM history"
        params = []
        
        if filter_type:
            if filter_type == "pinned":
                query += " WHERE pinned = 1"
            else:
                query += " WHERE type = ?"
                params.append(filter_type)
        
        query += " ORDER BY id DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        # Format rows
        formatted_rows = []
        for row in rows:
            r = list(row)
            if len(r) > 5 and r[5]:
                try:
                    r[5] = json.loads(r[5])
                except:
                    r[5] = {}
            else:
                if len(r) > 5: r[5] = {} 
                
            formatted_rows.append(tuple(r))
            
        return formatted_rows

    def toggle_pin(self, item_id):
        """Toggle pinned status."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check current status
        cursor.execute('SELECT pinned FROM history WHERE id = ?', (item_id,))
        res = cursor.fetchone()
        if res:
            new_status = 0 if res[0] == 1 else 1
            cursor.execute('UPDATE history SET pinned = ? WHERE id = ?', (new_status, item_id))
            conn.commit()
        
        conn.close()

    def delete_item(self, item_id):
        """Explicitly delete an item."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM history WHERE id = ?', (item_id,))
        conn.commit()
        conn.close()

    def update_item_metadata(self, item_id, new_meta):
        """Update metadata for an item (e.g. rename)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        meta_json = json.dumps(new_meta)
        cursor.execute('UPDATE history SET metadata = ? WHERE id = ?', (meta_json, item_id))
        
        conn.commit()
        conn.close()

    def clear_history(self, keep_pinned=True):
        """Wipe history. If keep_pinned is True, pinned items are preserved."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if keep_pinned:
            cursor.execute('DELETE FROM history WHERE pinned = 0')
        else:
            cursor.execute('DELETE FROM history') # Nuke everything
            
        conn.commit()
        conn.close()

    def get_pinned_count(self):
        """Return total number using pinned items."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM history WHERE pinned = 1')
        count = cursor.fetchone()[0]
        conn.close()
        return count

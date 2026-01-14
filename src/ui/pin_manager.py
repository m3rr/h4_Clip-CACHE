from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QPushButton, QLabel, QMessageBox, QListWidgetItem, QMenu)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPainter, QLinearGradient, QColor
from .theme_manager import ThemeManager
from .widgets.neon_button import NeonButton
from .widgets.history_item import HistoryItem
import os

class PinManagerWindow(QWidget):
    """
    Dedicated Window for managing Pinned Items.
    "Neat and Beautiful".
    """
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(400, 600)
        self.setup_ui()
        self.refresh_pins()

    def _get_theme(self):
        # We can fetch via ThemeManager using a default or known key if config isn't passed
        # Ideally we pass config, but for now let's use 'Deep Void' logic or fetch global
        # We'll assume ConfigManager can be instantiated to get current theme
        from ..core.config import ConfigManager
        cfg = ConfigManager()
        return ThemeManager.get_theme(cfg.get_theme())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        t = self._get_theme()
        
        bg_color = QColor(t['bg'])
        darker_bg = bg_color.darker(120)
        grad = QLinearGradient(0, 0, self.width(), self.height())
        grad.setColorAt(0.0, bg_color)
        grad.setColorAt(1.0, darker_bg)
        painter.setBrush(grad)
        
        accent = QColor(t['accent'])
        painter.setPen(accent)
        painter.drawRoundedRect(self.rect().adjusted(1,1,-1,-1), 8, 8)

    def setup_ui(self):
        t = self._get_theme()
        l = QVBoxLayout(self)
        l.setContentsMargins(20, 20, 20, 20)
        
        # Header
        h_layout = QHBoxLayout()
        header = QLabel("PIN MANAGER")
        header.setStyleSheet(f"color: {t['accent']}; font-weight: bold; font-size: 14pt;")
        h_layout.addWidget(header)
        h_layout.addStretch()
        
        close = QPushButton("✕")
        close.setFixedSize(25,25)
        close.clicked.connect(self.close)
        close.setStyleSheet(f"color: {t['fg']}; background: transparent; border: none; font-weight: bold;")
        h_layout.addWidget(close)
        l.addLayout(h_layout)
        
        # List
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("background: transparent; border: none;")
        self.list_widget.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        self.list_widget.setSpacing(5)
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        l.addWidget(self.list_widget)
        
        # Actions
        controls = QHBoxLayout()
        
        btn_remove = NeonButton("UNPIN SELECTED", "#FF5555")
        btn_remove.clicked.connect(self.unpin_selected)
        
        btn_goto = NeonButton("OPEN / GOTO", t['accent'])
        btn_goto.clicked.connect(self.goto_selected)
        
        controls.addWidget(btn_remove)
        controls.addWidget(btn_goto)
        l.addLayout(controls)
        
    def refresh_pins(self):
        self.list_widget.clear()
        # Fetch all items, verify pinned status locally?
        # DB unfortunately returns ALL items in get_history via filter.
        # But we need ONLY pinned. 
        # Database.get_history supports "pinned" string?
        # Let's check database.py Step 2247:
        # if filter_type == "pinned": query += " WHERE pinned = 1"
        # Yes, it supports 'pinned'
        
        items = self.db.get_history("pinned")
        
        if not items:
            lbl = QLabel("No Pinned Items Found")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            t = self._get_theme()
            lbl.setStyleSheet(f"color: {t['fg']}; font-style: italic;")
            item = QListWidgetItem()
            item.setSizeHint(QSize(300, 50))
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, lbl)
            return

        for row in items:
            # Row structure: id, type, content, timestamp, pinned, metadata
            data = {'id': row[0], 'type': row[1], 'content': row[2], 'timestamp': row[3], 'pinned': row[4], 'metadata': row[5]}
            
            # Use HistoryItem but maybe simplified? HistoryItem is fine.
            item_widget = HistoryItem(data)
            list_item = QListWidgetItem(self.list_widget)
            list_item.setSizeHint(item_widget.sizeHint())
            self.list_widget.addItem(list_item)
            self.list_widget.setItemWidget(list_item, item_widget)
            
    def on_item_clicked(self, list_item):
        # Reset selection visual check on all items
        for i in range(self.list_widget.count()):
            it = self.list_widget.item(i)
            w = self.list_widget.itemWidget(it)
            if w:
                w.setProperty("selected", False)
                w.update() # Force repaint
                
        # Set selected on clicked
        widget = self.list_widget.itemWidget(list_item)
        if widget:
            widget.setProperty("selected", True)
            widget.update()
            
    def unpin_selected(self):
        item = self.list_widget.currentItem()
        if not item: return
        
        # Also check if visually selected just in case
        # (currentItem should track selection but property is visual)
        
        w = self.list_widget.itemWidget(item)
        if w and hasattr(w, 'data'):
            # Unpin
            self.db.toggle_pin(w.data['id'])
            # Refresh list
            self.refresh_pins()
            
    def goto_selected(self):
        item = self.list_widget.currentItem()
        if not item: return
        
        w = self.list_widget.itemWidget(item)
        if w and hasattr(w, 'data'):
            content = w.data['content']
            dtype = w.data['type']
            
            if dtype == 'file' or dtype == 'image':
                if os.path.exists(content):
                    os.startfile(content)
                else:
                    print("[ERROR] File not found.")
            elif dtype == 'text':
                # Maybe copy to clipboard?
                QApplication.clipboard().setText(content)
                print("[INFO] Copied to clipboard.")

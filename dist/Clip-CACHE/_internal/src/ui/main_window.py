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
import json
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QListWidget, QListWidgetItem, QLabel, QSplitter, 
                             QScrollArea, QSizeGrip, QTabWidget, QPushButton, QFrame, QMessageBox)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QSettings, QPoint
from PyQt6.QtGui import QIcon, QPixmap, QColor
from .widgets.neon_button import NeonButton
from .widgets.history_item import HistoryItem
from .settings_window import SettingsWindow
from ..core.logger import LOGGER
from ..core.admin_tools import AdminTools

from ..core.config import ConfigManager

class MainWindow(QMainWindow):
    """
    Main Cyberpunk Interface (REFRESHED).
    - Tabbed Interface (All, Text, Images, Files, Admin).
    - Persistence (Geometry).
    - Nuclear Admin Controls.
    """
    def __init__(self, db_manager, clipboard_manager):
        super().__init__()
        self.db = db_manager
        self.clipboard = clipboard_manager
        
        # Persistence Init
        self.config = ConfigManager()
        
        # Window Flags - Frameless but visible on Taskbar and Alt+Tab
        # Removed Qt.WindowType.Tool so it shows on taskbar
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Set Window Icon for Taskbar and Alt+Tab
        import os
        from PyQt6.QtGui import QIcon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "image_assets", "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Set Window Title for Task Manager
        self.setWindowTitle("Clip-CACHE")

        # Pulse Animation State
        from PyQt6.QtCore import QTimer
        self.pulse_timer = QTimer(self)
        self.pulse_timer.timeout.connect(self._update_pulse)
        self.pulse_timer.start(50) # 20fps
        self.pulse_val = 0
        self.pulse_dir = 1
        
        # Load Geometry
        self.restore_geometry()
        self.setMinimumSize(800, 500)
        self.setMaximumSize(1280, 720) # Enforce 720p Max
        
        self.active_item_id = None
        
        # Connect signals
        self.clipboard.history_updated.connect(self.refresh_history)
        
        self.setup_ui()
        
        # Settings Window (Lazy load or init hidden)
        self.settings_window = SettingsWindow(self.db, self.config)
        self.settings_window.theme_changed.connect(self.update_theme)
        self.settings_window.debug_toggled.connect(self.set_debug_mode)
        
        # Connect Power Tools
        self.settings_window.purge_requested.connect(self.handle_purge)
        self.settings_window.manage_pins_requested.connect(self.switch_to_pins)
        self.settings_window.creation_requested.connect(self.show_creation_window)
        self.settings_window.tabula_rasa_requested.connect(self.handle_tabula_rasa)
        self.settings_window.hide()

        self.refresh_history()
        
        # Default Debug State
        self.debug_mode = False
        self._update_admin_visibility()

    def update_theme(self, theme_name):
        """Update window theme dynamically."""
        # ThemeManager already updates QApplication stylesheet via SettingsWindow.
        # We just need to update any manual colors or cached values.
        LOGGER.log(f"UI: MainWindow Updating Theme to {theme_name}")
        self.current_theme_cache_name = theme_name
        self.current_theme_data = ThemeManager.get_theme(theme_name)
        
        # Force pulse update to pick up new accent color immediately
        self._update_pulse()
        
        # Update specific elements that might not autosync (like icons if they were dynamic)
        # But mostly QSS handles it.
        
        # Ensure SettingsWindow gets updated style if it's open (it emits this so it knows, but good measure)
        pass

    def restore_geometry(self):
        geom = self.config.get_window_geometry()
        if geom:
            self.restoreGeometry(geom)
        else:
            self.resize(1000, 600)
            
    # closeEvent moved to bottom of class to merge with existing logic

    def _update_pulse(self):
        """Simulates a breathing glow effect."""
        from .theme_manager import ThemeManager
        # Get current theme accent
        cfg = self.config
        t_name = cfg.get_theme() 
        # Optimize: Don't fetch theme every frame. Store in self.current_theme_cache
        
        if not hasattr(self, 'current_theme_cache_name') or self.current_theme_cache_name != t_name:
             self.current_theme_cache_name = t_name
             self.current_theme_data = ThemeManager.get_theme(t_name)
        
        accent_hex = self.current_theme_data.get('accent', '#FFD700')
        c = QColor(accent_hex)
        
        # Oscillate Alpha
        self.pulse_val += self.pulse_dir * 5
        if self.pulse_val >= 200: self.pulse_dir = -1
        if self.pulse_val <= 50: self.pulse_dir = 1
        
        c.setAlpha(self.pulse_val)
        self.glow_effect.setColor(c)
        self.glow_effect.setBlurRadius(10 + (self.pulse_val / 10))

    # Signal for Main App to handle Tray visibility
    minimized = pyqtSignal()

    def changeEvent(self, event):
        # Detect Minimization
        if event.type() == event.Type.WindowStateChange:
            if self.isMinimized():
                self.minimized.emit()
                
        super().changeEvent(event)

    def closeEvent(self, event):
        self.pulse_timer.stop()
        self.settings_window.close()
        self.config.set_window_geometry(self.saveGeometry())
        super().closeEvent(event)
        
    def hideEvent(self, event):
        self.settings_window.hide()
        self.config.set_window_geometry(self.saveGeometry())
        
        # Trigger Incognito Logic / Tray Handling
        # This covers self.hide() calls from Custom Minimize button
        self.minimized.emit()
        
        super().hideEvent(event)

    def showEvent(self, event):
        # Force refresh theme on show to ensure SettingsWindow gets the update
        # This handles the case where ThemeManager initialized with default (Yellow) 
        # but Config loaded Amethyst, and SettingsWindow wasn't repolished.
        try:
            from .theme_manager import ThemeManager
            t_name = self.config.get_theme()
            ss = ThemeManager.get_stylesheet(t_name)
            self.settings_window.setStyleSheet(ss)
        except Exception as e:
            print(f"Error refreshing settings theme: {e}")
        super().showEvent(event)

    def setup_ui(self):
        # Central Widget
        self.central_widget = QWidget()
        self.central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(self.central_widget)
        
        # Glow Effect (Pulse)
        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        self.glow_effect = QGraphicsDropShadowEffect()
        self.glow_effect.setBlurRadius(15)
        self.glow_effect.setOffset(0, 0)
        self.glow_effect.setColor(QColor("#FFD700")) # Default, will update
        self.central_widget.setGraphicsEffect(self.glow_effect)
        
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        
        # --- Top Bar ---
        self.top_bar = QHBoxLayout()
        self.lbl_title = QLabel("Clip-CACHE // h4 - {Be Your Best}")
        self.lbl_title.setObjectName("AppTitle")
        # Removed hardcoded stylesheet; handled by ThemeManager
        # self.lbl_title.setStyleSheet("font-weight: bold; color: #FFD700; letter-spacing: 2px;") 
        
        self.top_bar.addWidget(self.lbl_title)
        self.top_bar.addStretch()

        # Settings Button - Using clearer symbols
        self.btn_settings = NeonButton("☰", "#FFD700")  # Menu/Settings symbol
        self.btn_settings.setFixedSize(36, 36)
        self.btn_settings.clicked.connect(self.open_settings)
        
        self.btn_min = NeonButton("─", "#888888")  # Horizontal line for minimize
        self.btn_min.setFixedSize(36, 36)
        self.btn_min.clicked.connect(self.hide)
        
        self.btn_close = NeonButton("✕", "#FF5555")  # Clear X symbol
        self.btn_close.setFixedSize(36, 36)
        self.btn_close.clicked.connect(self.close_app)  # Nuclear Exit
        
        self.top_bar.addWidget(self.btn_settings)
        self.top_bar.addWidget(self.btn_min)
        self.top_bar.addWidget(self.btn_close)
        
        self.main_layout.addLayout(self.top_bar)
        
        # --- Splitter Content ---
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Pane 1: Tabbed History
        self.tabs = QTabWidget()
        self.tabs.setFixedWidth(400)
        self.tabs.currentChanged.connect(self.refresh_history)
        
        # Create Lists for Tabs
        self.list_pinned = self._create_list_widget() # New Pinned List
        self.list_pinned.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_pinned.customContextMenuRequested.connect(self.show_pinned_context_menu)
        
        self.list_all = self._create_list_widget()
        self.list_text = self._create_list_widget()
        self.list_images = self._create_list_widget()
        self.list_files = self._create_list_widget()
        
        self.tabs.addTab(self.list_pinned, "PINNED") # Index 0
        self.tabs.addTab(self.list_all, "ALL") # Index 1
        self.tabs.addTab(self.list_text, "TEXT") # Index 2
        self.tabs.addTab(self.list_images, "IMG") # Index 3
        self.tabs.addTab(self.list_files, "FILES") # Index 4
        
        # Admin Tab (Index 5)
        self.admin_container = QWidget()
        self.setup_admin_tab()
        self.tabs.addTab(self.admin_container, "ADMIN")
        
        # Pane 2: Preview
        self.preview_container = QWidget()
        self.preview_layout = QVBoxLayout(self.preview_container)
        self.lbl_preview_img = QLabel("Select Item")
        self.lbl_preview_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_preview_img.setStyleSheet("background: rgba(0,0,0,100); border: 1px dashed #444; color: #888;")
        self.preview_layout.addWidget(self.lbl_preview_img)
        
        # Pane 3: Controls
        self.setup_controls_pane()
        
        # Add to Splitter
        self.splitter.addWidget(self.tabs)
        self.splitter.addWidget(self.preview_container)
        self.splitter.addWidget(self.controls_container)
        self.splitter.setStretchFactor(1, 2)
        
        self.main_layout.addWidget(self.splitter)
        
        # --- Bottom Grip ---
        self.bottom_layout = QHBoxLayout()
        self.bottom_layout.addStretch()
        self.size_grip = QSizeGrip(self.central_widget)
        self.bottom_layout.addWidget(self.size_grip)
        self.main_layout.addLayout(self.bottom_layout)
        
        self.old_pos = None

    def _create_list_widget(self):
        from PyQt6.QtWidgets import QAbstractItemView, QScroller
        lw = QListWidget()
        lw.setStyleSheet("background: transparent; border: none;")
        lw.setFlow(QListWidget.Flow.TopToBottom)
        lw.itemClicked.connect(self.on_item_clicked)
        
        # Carousel / Kinetic Scrolling
        lw.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        lw.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        lw.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Enable Kinetic Scroller (Touch Only - Left Mouse is for clicking items)
        # Using TouchGesture instead of LeftMouseButtonGesture to preserve click handling
        QScroller.grabGesture(lw.viewport(), QScroller.ScrollerGestureType.TouchGesture)
        
        # Spacing - Minimal gap between items
        lw.setSpacing(0)
        return lw

    def setup_controls_pane(self):
        self.controls_container = QWidget()
        self.controls_layout = QVBoxLayout(self.controls_container)
        self.controls_layout.setSpacing(10)
        
        self.lbl_details = QLabel("METADATA:\nNone")
        self.lbl_details.setWordWrap(True)
        self.lbl_details.setStyleSheet("font-family: Consolas; font-size: 9pt; color: #BBB;")
        
        self.btn_active = NeonButton("MAKE ACTIVE")
        self.btn_active.clicked.connect(self.make_active)
        
        self.btn_pin = NeonButton("PIN ITEM")
        self.btn_pin.clicked.connect(self.toggle_pin)
        
        self.btn_delete = NeonButton("DELETE", "#FF5555")
        self.btn_delete.clicked.connect(self.delete_item)
        
        self.controls_layout.addWidget(QLabel("DETAILS"))
        self.controls_layout.addWidget(self.lbl_details)
        self.controls_layout.addWidget(QLabel("ACTIONS"))
        self.controls_layout.addWidget(self.btn_active)
        self.controls_layout.addWidget(self.btn_pin)
        self.controls_layout.addWidget(self.btn_delete)
        
        # DEBUG: Verify buttons exist
        print(f"[DEBUG] btn_active created: {self.btn_active}, text: {self.btn_active.text()}, visible: {self.btn_active.isVisible()}")
        print(f"[DEBUG] btn_pin created: {self.btn_pin}, text: {self.btn_pin.text()}, visible: {self.btn_pin.isVisible()}")
        print(f"[DEBUG] btn_delete created: {self.btn_delete}, text: {self.btn_delete.text()}, visible: {self.btn_delete.isVisible()}")
        
        # Debug Button Moved to Settings Overlay
        self.controls_layout.addStretch()

    def setup_admin_tab(self):
        layout = QVBoxLayout(self.admin_container)
        layout.setSpacing(10)
        
        lbl = QLabel("NUCLEAR ADMIN PANEL")
        lbl.setStyleSheet("color: red; font-weight: bold; font-size: 12pt;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl)
        
        btn_term = NeonButton("LAUNCH TERMINAL", "#00AA00")
        btn_term.clicked.connect(AdminTools.launch_terminal)
        
        btn_task = NeonButton("TASK MANAGER", "#0088AA")
        btn_task.clicked.connect(AdminTools.launch_task_manager)
        
        btn_ram = NeonButton("CLEAR WORKING RAM", "#FFAA00")
        btn_ram.clicked.connect(self.show_admin_ram_optimizer)
        
        btn_vram = NeonButton("RESET VRAM (RISK)", "#FF0000")
        btn_vram.clicked.connect(AdminTools.clear_vram)
        
        # New Network Tools
        btn_ip = NeonButton("RESET IP STACK", "#00FFFF")
        btn_ip.clicked.connect(AdminTools.reset_ip_stack)
        
        layout.addWidget(btn_term)
        layout.addWidget(btn_task)
        layout.addWidget(btn_ip) # Added
        layout.addWidget(btn_ram)
        layout.addWidget(btn_vram)
        layout.addStretch()

    def show_admin_ram_optimizer(self):
        from PyQt6.QtWidgets import QMessageBox, QApplication
        
        # 1. Choice Dialog
        msg = QMessageBox(self)
        msg.setWindowTitle("RAM OPTIMIZATION PROTOCOL")
        msg.setText("Select Memory Cleaning Intensity")
        msg.setInformativeText("GENTLE: Clears this app's Working Set.\nAGGRESSIVE: Trims Working Sets for ALL accessible processes.")
        
        btn_gentle = msg.addButton("GENTLE CLEAN", QMessageBox.ButtonRole.ActionRole)
        btn_aggressive = msg.addButton("AGGRESSIVE CLEAN", QMessageBox.ButtonRole.ActionRole)
        btn_cancel = msg.addButton(QMessageBox.StandardButton.Cancel)
        
        # Theme Styling
        from .theme_manager import ThemeManager
        t_name = self.config.get_theme()
        t = ThemeManager.get_theme(t_name)
        
        style = f"""
            QMessageBox {{ background-color: {t['bg']}; color: {t['fg']}; }}
            QLabel {{ color: {t['fg']}; }}
            QPushButton {{ background-color: {t['border']}; color: {t['fg']}; padding: 5px 15px; border: 1px solid {t['accent']}; }}
            QPushButton:hover {{ background-color: {t['accent']}; color: {t['bg']}; }}
        """
        msg.setStyleSheet(style)
        
        msg.exec()
        clicked = msg.clickedButton()
        
        if clicked == btn_cancel or not clicked:
            return
            
        aggressive = (clicked == btn_aggressive)
        method_name = "AGGRESSIVE CLEAN" if aggressive else "GENTLE CLEAN"
        
        # 2. Warning / Progress Dialog
        warn = QMessageBox(self)
        warn.setWindowTitle("EXECUTING PROTOCOL")
        warn.setStyleSheet(style)
        
        body = f"{method_name} trying to Clear memory - Please wait at least 2min."
        if aggressive:
            body += "\n\nChoosing AGGRESSIVE means you are purging the ram- this may cause apps or other functions to fail to work, and may require a system restart."
            
        warn.setText(body)
        warn.setStandardButtons(QMessageBox.StandardButton.Ok)
        
        if warn.exec() == QMessageBox.StandardButton.Ok:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            QApplication.processEvents()
            try:
                # Run Logic
                AdminTools.clean_system_memory(aggressive=aggressive)
            finally:
                QApplication.restoreOverrideCursor()
            LOGGER.log(f"RAM Optimization ({method_name}) Finished.")

    def refresh_history(self):
        # 1. Manage Pinned Tab Visibility (Index 0)
        pinned_count = self.db.get_pinned_count()
        
        # If we have pins, show the tab
        if pinned_count > 0:
            self.tabs.setTabVisible(0, True)
        else:
            self.tabs.setTabVisible(0, False)
            # If we were on Pinned tab and it disappeared, switch to ALL
            if self.tabs.currentIndex() == 0:
                self.tabs.setCurrentIndex(1)

        # 2. Determine active list based on Tab
        idx = self.tabs.currentIndex()
        tab_text = self.tabs.tabText(idx)
        
        if tab_text == "ADMIN":
            return # Static content
            
        target_list = self.tabs.currentWidget()
        target_list.clear() # Clear specific list
        
        # Get all history
        items = self.db.get_history()
        
        for row in items:
            data = {'id': row[0], 'type': row[1], 'content': row[2], 'timestamp': row[3], 'pinned': row[4], 'metadata': row[5]}
            
            # Filter logic
            if tab_text == "PINNED" and not data['pinned']: continue
            if tab_text == "TEXT" and data['type'] != 'text': continue
            if tab_text == "IMG" and data['type'] != 'image': continue
            if tab_text == "FILES" and data['type'] != 'file': continue
            
            # Note: "ALL" shows everything, including pinned. "PINNED" shows only pinned.
            
            item_widget = HistoryItem(data)
            list_item = QListWidgetItem(target_list)
            list_item.setSizeHint(item_widget.sizeHint())
            target_list.addItem(list_item)
            target_list.setItemWidget(list_item, item_widget)
            
    def set_debug_mode(self, enabled):
        LOGGER.log(f"UI: Debug Mode Toggled to {enabled}")
        # Toggle Admin Tab visibility (Index 5 now)
        self.tabs.setTabVisible(5, enabled)
        
    def _update_admin_visibility(self):
        self.tabs.setTabVisible(5, False)

    # --- Power Tool Handlers ---
    def handle_purge(self):
        # Purge all EXCEPT pinned
        self.db.clear_history(keep_pinned=True)
        self.refresh_history()
        # Notify
        LOGGER.log(f"MEMORY: History Purged (Pins Preserved).")
        
    def switch_to_pins(self):
        # Index 0 is 'PINNED'
        # If visible...
        if self.tabs.isTabVisible(0):
            self.tabs.setCurrentIndex(0)
        else:
            # If not visible (count=0), maybe warn? or just go to ALL
            LOGGER.log("UI: Requested Pinned Tab but it is hidden (0 pins).")
            self.tabs.setCurrentIndex(1) # ALL
            
        self.show()
        self.activateWindow()

    def on_item_clicked(self, list_item):
        target_list = list_item.listWidget()
        
        # Deselect/Reset all visual states in this list
        for i in range(target_list.count()):
            it = target_list.item(i)
            w = target_list.itemWidget(it)
            if w:
                w.setProperty("selected", False)
                w.update()

        # Set Selected on clicked
        widget = target_list.itemWidget(list_item)
        if widget:
            widget.setProperty("selected", True)
            widget.update()
            
            self.update_details(widget.data)

    def update_details(self, data):
        # COPY data prevents mutating the original ListWidget item permanently if we didn't want to
        # But here we want self.current_data to represent the "Effective" item.
        # So we will copy it to safe_data.
        safe_data = data.copy()
        
        meta = safe_data.get('metadata', {})
        if not isinstance(meta, dict): meta = {}
        
        vault_path = meta.get('vault_path')
        is_vaulted = False
        
        if vault_path and os.path.exists(vault_path):
            # OVERRIDE CONTENT WITH VAULT PATH
            safe_data['content'] = vault_path
            is_vaulted = True
        
        meta_str = f"ID: {safe_data['id']}\nTime: {safe_data['timestamp']}\nType: {safe_data['type']}\nPinned: {bool(safe_data['pinned'])}"
        
        if is_vaulted:
            meta_str += "\n🔒 [SECURED IN VAULT]"
        
        if meta:
            # Format metadata nicely
            meta_str += "\n\nMETADATA:\n"
            for k, v in meta.items():
                meta_str += f"{k}: {v}\n"
        else:
            meta_str += "\n\nMETADATA: None"
            
        self.lbl_details.setText(meta_str)
        self.btn_pin.setText("UNPIN ITEM" if safe_data['pinned'] else "PIN ITEM")
        
        # Use safe_data for everything below
        data = safe_data
        
        # ... (rest of function uses 'data')
        
        # Clear Previous
        self.lbl_preview_img.setPixmap(QPixmap())
        self.lbl_preview_img.setText("")
        self.lbl_preview_img.setStyleSheet("border: none; background: transparent; color: #FFD700; font-size: 14pt;")
        self.lbl_preview_img.setOpenExternalLinks(False)  # We handle links manually
        
        if data['type'] == 'image':
            path = data['content']
            if os.path.exists(path):
                pix = QPixmap(path)
                scaled = pix.scaled(self.lbl_preview_img.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.lbl_preview_img.setPixmap(scaled)
            else:
                self.lbl_preview_img.setText("Image Missing")
        elif data['type'] == 'file':
            # Rich File Properties Preview
            file_path = data['content']
            self.lbl_preview_img.setWordWrap(True)
            
            if os.path.exists(file_path):
                import stat
                from datetime import datetime
                
                file_stat = os.stat(file_path)
                file_name = os.path.basename(file_path)
                folder_path = os.path.dirname(file_path)
                file_ext = os.path.splitext(file_path)[1].upper() or "N/A"
                
                # File Size Formatting
                size_bytes = file_stat.st_size
                if size_bytes < 1024:
                    size_str = f"{size_bytes} B"
                elif size_bytes < 1024 * 1024:
                    size_str = f"{size_bytes / 1024:.2f} KB"
                elif size_bytes < 1024 * 1024 * 1024:
                    size_str = f"{size_bytes / (1024*1024):.2f} MB"
                else:
                    size_str = f"{size_bytes / (1024*1024*1024):.2f} GB"
                
                # Dates
                created = datetime.fromtimestamp(file_stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
                modified = datetime.fromtimestamp(file_stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                accessed = datetime.fromtimestamp(file_stat.st_atime).strftime("%Y-%m-%d %H:%M:%S")
                
                # Attributes
                is_readonly = not os.access(file_path, os.W_OK)
                is_hidden = bool(file_stat.st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN) if hasattr(file_stat, 'st_file_attributes') else False
                
                # Build Preview HTML with clickable folder link
                preview_html = f"""
<html>
<head><style>
    body {{ color: #CCCCCC; font-family: Consolas; font-size: 10pt; }}
    .header {{ color: #FFD700; font-size: 12pt; font-weight: bold; margin-bottom: 10px; }}
    .label {{ color: #888888; }}
    .value {{ color: #FFFFFF; }}
    .link {{ color: #00FFFF; text-decoration: underline; }}
</style></head>
<body>
    <div class="header">📁 FILE PROPERTIES</div>
    <table>
        <tr><td class="label">Name:</td><td class="value">{file_name}</td></tr>
        <tr><td class="label">Type:</td><td class="value">{file_ext} File</td></tr>
        <tr><td class="label">Size:</td><td class="value">{size_str}</td></tr>
        <tr><td class="label">Created:</td><td class="value">{created}</td></tr>
        <tr><td class="label">Modified:</td><td class="value">{modified}</td></tr>
        <tr><td class="label">Accessed:</td><td class="value">{accessed}</td></tr>
        <tr><td class="label">Read-only:</td><td class="value">{'Yes' if is_readonly else 'No'}</td></tr>
        <tr><td class="label">Hidden:</td><td class="value">{'Yes' if is_hidden else 'No'}</td></tr>
    </table>
    <br/>
    <a href="file:///{folder_path}" class="link">📂 Open Containing Folder</a>
</body>
</html>
"""
                self.lbl_preview_img.setTextFormat(Qt.TextFormat.RichText)
                self.lbl_preview_img.setText(preview_html)
                self.lbl_preview_img.setOpenExternalLinks(True)
            else:
                self.lbl_preview_img.setText("FILE NOT FOUND")
        else:
            # Text Preview
            self.lbl_preview_img.setWordWrap(True)
            self.lbl_preview_img.setTextFormat(Qt.TextFormat.PlainText)
            txt = data['content']
            
            # --- VAULT TEXT HANDLING ---
            # If type is text but content is a file path (Vaulted), read it!
            if is_vaulted and os.path.exists(txt) and os.path.isfile(txt):
                try:
                    with open(txt, 'r', encoding='utf-8', errors='ignore') as f:
                        txt = f.read()
                except Exception as e:
                    txt = f"[ERROR READING VAULT TEXT]: {e}"
            # ---------------------------

            if len(txt) > 500: txt = txt[:500] + "\n...[TRUNCATED]"
            self.lbl_preview_img.setText(txt)
                
        self.current_data = data

        self._update_active_btn()

    def _update_active_btn(self):
        if not hasattr(self, 'current_data'): return
        
        is_active = (self.active_item_id == self.current_data['id'])
        from .theme_manager import ThemeManager
        t_colors = ThemeManager.get_theme(self.config.get_theme())
        
        if is_active:
            self.btn_active.setText("ACTIVE")
            self.btn_active.setStyleSheet(f"background-color: {t_colors['glass']}; color: #00FF00; border: 1px solid #00FF00; font-weight: bold;")
        else:
            self.btn_active.setText("MAKE ACTIVE")
            self.btn_active.setStyleSheet("") # Clear override
            self.btn_active.update()

    def make_active(self):
        if hasattr(self, 'current_data'):
            from PyQt6.QtWidgets import QApplication
            from PyQt6.QtCore import QMimeData, QUrl
            from PyQt6.QtGui import QImage
            
            cb = QApplication.clipboard()
            data = self.current_data
            
            if data['type'] == 'text':
                content = data['content']
                # Check for Vaulted Text File
                if os.path.exists(content) and os.path.isfile(content):
                     # It's likely a Vault Path
                     try:
                         with open(content, 'r', encoding='utf-8', errors='ignore') as f:
                             content = f.read()
                     except Exception as e:
                         print(f"Error reading vaulted text for clipboard: {e}")
                         # Fallback to copy path if read fails? No, better to fail text copy or copy error.
                         
                cb.setText(content)
            
            elif data['type'] == 'image':
                img = QImage(data['content'])
                if not img.isNull():
                    cb.setImage(img)
                else:
                    LOGGER.log(f"ERROR: Failed to load image for clipboard: {data['content']}")
            
            elif data['type'] == 'file':
                mime = QMimeData()
                mime.setUrls([QUrl.fromLocalFile(data['content'])])
                cb.setMimeData(mime)
                
            # Set Active State
            self.active_item_id = data['id']
            # Re-update button immediately
            self._update_active_btn()
            LOGGER.log(f"CLIPBOARD: Set Active Item {data['id']}")

    def toggle_pin(self):
        try:
            if not hasattr(self, 'current_data'):
                return

            item = self.current_data
            item_id = item['id']
            is_pinned = item['pinned']
            
            # Initialize Vault
            from ..core.vault import VaultManager
            vault = VaultManager()
            
            # --- UNPINNING LOGIC (DESTRUCTION) ---
            if is_pinned:
                # 1. Warn User (Destructive Action)
                msg = QMessageBox(self)
                msg.setWindowTitle("DESTROY MEMORY?")
                msg.setText("Unpinning this item will PERMANENTLY DELETE the Vault copy.\n\nAre you sure?")
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                
                if msg.exec() == QMessageBox.StandardButton.Yes:
                     # Check Metadata for vault path
                     meta = item.get('metadata', {})
                     if not isinstance(meta, dict): meta = {} # Force Dict
                     
                     vault_path = meta.get('vault_path')
                     
                     if vault_path:
                         try:
                             vault.delete_item(vault_path)
                         except Exception as e:
                             print(f"Vault Delete Error: {e}")
                             
                         meta['vault_path'] = None # Clear it
                         self.db.update_item_metadata(item_id, meta)
                         
                     self.db.toggle_pin(item_id)
                     
                     # UPDATE LOCAL STATE TO PREVENT STALE LOGIC
                     self.current_data['pinned'] = 0
                     self.update_details(self.current_data)
                     
                     self.refresh_history()

            # --- PINNING LOGIC (CREATION) ---
            else:
                # 1. Size Check (If File)
                if item['type'] == 'file':
                    try:
                        f_size = vault.get_file_size_mb(item['content'])
                        if f_size > 500:
                            msg = QMessageBox(self)
                            msg.setWindowTitle("MASSIVE OBJECT DETECTED")
                            msg.setText(f"This file is {f_size:.2f} MB.\n\nCopying it to the Vault might take space.\nProceed?")
                            msg.setIcon(QMessageBox.Icon.Question)
                            msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                            if msg.exec() != QMessageBox.StandardButton.Yes:
                                return
                    except:
                        pass # Ignore size check error

                # 2. Store in Vault
                new_path = vault.store_item(item['type'], item['content'])
                
                if new_path:
                    # 3. Update DB
                    meta = item.get('metadata', {})
                    if not isinstance(meta, dict): meta = {} # Safety
                    meta['vault_path'] = new_path
                    self.db.update_item_metadata(item_id, meta)
                    
                    self.db.toggle_pin(item_id)
                    
                    # UPDATE LOCAL STATE
                    self.current_data['pinned'] = 1
                    self.update_details(self.current_data)
                    
                    self.refresh_history()
                else:
                    QMessageBox.warning(self, "Vault Error", "Failed to store item in Vault.")
                    
        except Exception as e:
            import traceback
            err = traceback.format_exc()
            print(f"[ERROR] Toggle Pin Failed: {e}\n{err}")
            QMessageBox.critical(self, "Critical Error", f"Failed to toggle pin:\n{e}")

    def delete_item(self):
        if hasattr(self, 'current_data'):
             self.db.delete_item(self.current_data['id'])
             self.refresh_history()
             self.lbl_preview_img.setText("Deleted")
             self.lbl_details.setText("")

    def open_settings(self):
        # Reposition settings window relative to main window
        # Center it
        geo = self.geometry()
        x = geo.x() + (geo.width() - 600) // 2
        y = geo.y() + (geo.height() - 400) // 2
        self.settings_window.move(x, y)
        self.settings_window.show()
        self.settings_window.raise_()

    def set_debug_mode(self, enabled):
        LOGGER.log(f"UI: Debug Mode Toggled to {enabled}")
        # Toggle Admin Tab visibility (Index 5)
        self.tabs.setTabVisible(5, enabled)
        
    def _update_admin_visibility(self):
        self.tabs.setTabVisible(5, False)

    # --- Power Tool Handlers ---
    def handle_purge(self):
        # Purge all EXCEPT pinned
        self.db.clear_history(keep_pinned=True)
        self.refresh_history()
        # Notify
        LOGGER.log(f"MEMORY: History Purged (Pins Preserved).")
        
    def handle_tabula_rasa(self):
        # NUCLEAR WIPE
        self.db.clear_history(keep_pinned=False)
        self.refresh_history()
        LOGGER.log("MEMORY: TABULA RASA EXECUTED. ALL DATA WIPED.")

    def switch_to_pins(self):
        # Index 0 is 'PINNED'
        # If visible...
        if self.tabs.isTabVisible(0):
            self.tabs.setCurrentIndex(0)
        else:
            LOGGER.log("UI: Requested Pinned Tab but it is hidden (0 pins).")
            self.tabs.setCurrentIndex(1) # ALL
            
        self.show()
        self.activateWindow()
        
    def show_creation_window(self):
        from .creation_window import CreationWindow
        self.creation_win = CreationWindow(self.clipboard)
        self.creation_win.show()

    def show_pinned_context_menu(self, pos):
        # Position menu correctly
        global_pos = self.list_pinned.mapToGlobal(pos)
        
        item = self.list_pinned.itemAt(pos)
        if not item: return
        
        widget = self.list_pinned.itemWidget(item)
        if not widget: return
        
        from PyQt6.QtWidgets import QMenu, QInputDialog, QLineEdit
        menu = QMenu()
        menu.setStyleSheet("QMenu { background-color: #222; color: #FFF; border: 1px solid #555; } QMenu::item:selected { background-color: #444; }")
        
        rename_action = menu.addAction("RENAME PIN")
        
        action = menu.exec(global_pos)
        
        if action == rename_action:
            # Show Dialog
            current_name = getattr(widget, 'display_title', "Item")
            
            new_name, ok = QInputDialog.getText(self, "RENAME PIN", "Enter new name:", QLineEdit.EchoMode.Normal, current_name)
            
            if ok and new_name:
                data = widget.data
                meta = data.get('metadata', {})
                if not isinstance(meta, dict): meta = {}
                
                meta['display_name'] = new_name
                
                # Update DB
                self.db.update_item_metadata(data['id'], meta)
                
                # Refresh
                self.refresh_history()
                LOGGER.log(f"PIN: Renamed item {data['id']} to '{new_name}'")

    def closeEvent(self, event):
        # Save Geometry on Close
        self.config.set_window_geometry(self.saveGeometry())
        # Ensure child windows close
        self.settings_window.close()
        super().closeEvent(event)

    def close_app(self):
        """Nuclear Exit"""
        LOGGER.log("Nuclear Quit Initiated.")
        # Save geometry
        self.config.set_window_geometry(self.saveGeometry())
        from PyQt6.QtWidgets import QApplication
        QApplication.instance().quit()

    # Dragging
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()
    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()
    def mouseReleaseEvent(self, event):
        self.old_pos = None

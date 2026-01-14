from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QListWidget, 
                             QStackedWidget, QLabel, QFrame, QListWidgetItem, QPushButton, QMessageBox)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QUrl
from PyQt6.QtGui import QColor, QPainter, QLinearGradient, QPen, QFont, QDesktopServices
from .widgets.neon_button import NeonButton
from .theme_manager import ThemeManager
from ..core.logger import LOGGER
from ..core.admin_tools import AdminTools
from ..core.config import ConfigManager

class SettingsWindow(QWidget):
    """
    Settings 2.0: Cyberpunk Side-Nav Layout.
    - Left: Navigation List
    - Right: Stacked Content
    - 100% Theme Aware - NO HARDCODED COLORS
    """
    theme_changed = pyqtSignal(str)
    debug_toggled = pyqtSignal(bool)
    tabula_rasa_requested = pyqtSignal()

    def __init__(self, db, config, parent=None):
        super().__init__(parent)
        self.db = db
        self.config = config
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setObjectName("SettingsWindow")
        self.setFixedSize(600, 400)
        
        # Theme Cache
        self._cached_theme = None
        self._cached_theme = None
        
        self.setup_ui()
        self.easter_egg_state = 0
        
    def _get_theme(self):
        """Get current theme colors."""
        theme_name = self.config.get_theme()
        return ThemeManager.get_theme(theme_name)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        t = self._get_theme()
        
        # Background: Deep Tech Gradient using theme bg color
        bg_color = QColor(t['bg'])
        darker_bg = bg_color.darker(120)
        
        grad = QLinearGradient(0, 0, self.width(), self.height())
        grad.setColorAt(0.0, bg_color)
        grad.setColorAt(1.0, darker_bg)
        painter.setBrush(grad)
        
        # Border using theme accent
        accent = QColor(t['accent'])
        painter.setPen(QPen(accent, 2))
        painter.drawRoundedRect(self.rect().adjusted(1,1,-1,-1), 10, 10)
        
        # Grid Overlay using theme accent with low alpha
        grid_color = QColor(accent)
        grid_color.setAlpha(15)
        painter.setPen(grid_color)
        for x in range(0, self.width(), 40):
            painter.drawLine(x, 0, x, self.height())
        for y in range(0, self.height(), 40):
            painter.drawLine(0, y, self.width(), y)

    def setup_ui(self):
        t = self._get_theme()
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # --- LEFT: Side Nav ---
        self.nav_list = QListWidget()
        self.nav_list.setFixedWidth(150)
        self._apply_nav_style()
        
        items = ["GENERAL", "VISUALS", "POWER USER", "ABOUT"]
        for i in items:
            self.nav_list.addItem(i)
            
        self.nav_list.currentRowChanged.connect(self.change_page)
        
        # --- RIGHT: Content Stack ---
        self.stack = QStackedWidget()
        
        self.page_general = self._create_general_page()
        self.stack.addWidget(self.page_general)
        
        self.page_visuals = self._create_visuals_page()
        self.stack.addWidget(self.page_visuals)
        
        self.page_power = self._create_power_page()
        self.stack.addWidget(self.page_power)
        
        self.page_about = self._create_about_page()
        self.stack.addWidget(self.page_about)
        
        main_layout.addWidget(self.nav_list)
        
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        right_layout.addWidget(self.stack)
        
        # Close Button - uses theme accent
        btn_close = NeonButton("CLOSE", self._get_theme()['accent'])
        btn_close.clicked.connect(self.hide)
        right_layout.addWidget(btn_close)
        
        main_layout.addWidget(right_container)
    
    def _apply_nav_style(self):
        """Apply theme-aware styling to nav list."""
        t = self._get_theme()
        self.nav_list.setStyleSheet(f"""
            QListWidget {{
                background: rgba(0,0,0,50);
                border: none;
                color: {t['fg']};
                font-family: 'Segoe UI';
                font-size: 11pt;
                outline: none;
            }}
            QListWidget::item {{
                padding: 10px;
                border-left: 2px solid transparent;
            }}
            QListWidget::item:selected {{
                color: {t['accent']};
                background: {t['glass']};
                border-left: 2px solid {t['accent']};
            }}
            QListWidget::item:hover {{
                color: {t['accent']};
                background: {t['glass']};
            }}
        """)

    def change_page(self, index):
        self.stack.setCurrentIndex(index)
    
    def refresh_theme(self):
        """Refresh all theme-aware components."""
        self._apply_nav_style()
        self.update()  # Trigger repaint

    def _create_general_page(self):
        t = self._get_theme()
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel("GENERAL SETTINGS"))
        
        # Start with Windows toggle
        self.btn_startup = NeonButton("Start with Windows: OFF", t['border'])
        self.btn_startup.clicked.connect(self.toggle_startup)
        l.addWidget(self.btn_startup)
        
        # Start in Background toggle (minimize to tray on launch)
        bg_enabled = self.config.get_start_in_background()
        self.btn_background = NeonButton(f"Start in Background: {'ON' if bg_enabled else 'OFF'}", t['accent'] if bg_enabled else t['border'])
        self.btn_background.clicked.connect(self.toggle_background_start)
        l.addWidget(self.btn_background)

        # Incognito Mode toggle (No Tray Icon when minimized)
        incog_enabled = self.config.get_incognito_mode()
        self.btn_incognito = NeonButton(f"Incognito Mode: {'ON' if incog_enabled else 'OFF'}", t['accent'] if incog_enabled else t['border'])
        self.btn_incognito.clicked.connect(self.toggle_incognito)
        l.addWidget(self.btn_incognito)
        
        l.addStretch()
        return w

    def _create_visuals_page(self):
        from PyQt6.QtWidgets import QComboBox
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel("VISUAL CUSTOMIZATION"))
        
        l.addWidget(QLabel("Select Theme:"))
        self.combo_themes = QComboBox()
        self.combo_themes.addItems(ThemeManager.get_theme_names())
        
        saved_theme = self.config.get_theme()
        self.combo_themes.setCurrentText(saved_theme)
        
        self.combo_themes.currentTextChanged.connect(self.change_theme)
        l.addWidget(self.combo_themes)
        
        l.addStretch()
        return w
        
    def toggle_startup(self):
        t = self._get_theme()
        text = self.btn_startup.text()
        if "OFF" in text:
            self.btn_startup.setText("Start with Windows: ON")
            # Use accent for ON state
            self.btn_startup.accent_color = t['accent']
            AdminTools.set_start_with_windows(True)
        else:
            self.btn_startup.setText("Start with Windows: OFF")
            self.btn_startup.accent_color = t['border']
            AdminTools.set_start_with_windows(False)

    def toggle_background_start(self):
        """Toggle whether app starts minimized to system tray."""
        t = self._get_theme()
        text = self.btn_background.text()
        if "OFF" in text:
            self.btn_background.setText("Start in Background: ON")
            self.btn_background.accent_color = t['accent']
            self.config.set_start_in_background(True)
        else:
            self.btn_background.setText("Start in Background: OFF")
            self.btn_background.accent_color = t['border']
            self.config.set_start_in_background(False)

    def toggle_incognito(self):
        t = self._get_theme()
        text = self.btn_incognito.text()
        if "OFF" in text:
            self.btn_incognito.setText("Incognito Mode: ON")
            self.btn_incognito.accent_color = t['accent']
            self.config.set_incognito_mode(True)
        else:
            self.btn_incognito.setText("Incognito Mode: OFF")
            self.btn_incognito.accent_color = t['border']
            self.config.set_incognito_mode(False)
            # If we turn it OFF, we should ensure tray is visible immediately if user minimized?
            # User will likely change this while window is open, so it's fine.
            # But we might want to emit a signal to 'refresh_tray_visibility' if we want instant feedback.
            # For now, it will take effect next time strict logic is applied (minimize/restore).
            
    def change_theme(self, theme_name):
        self.config.set_theme(theme_name)
        stylesheet = ThemeManager.get_stylesheet(theme_name)
        
        from PyQt6.QtWidgets import QApplication
        if QApplication.instance():
            QApplication.instance().setStyleSheet(stylesheet)
            LOGGER.log(f"Theme changed to {theme_name}")
        
        self.refresh_theme()

    # New signals for Power Tools
    purge_requested = pyqtSignal()
    manage_pins_requested = pyqtSignal()
    creation_requested = pyqtSignal()

    def _create_power_page(self):
        t = self._get_theme()
        w = QWidget()
        l = QVBoxLayout(w)
        
        # Section 1: Debugger
        l.addWidget(QLabel("SYSTEM DEBUGGER"))
        self.btn_debug = NeonButton("GOD MODE: DEACTIVATED", t['border'])
        self.btn_debug.clicked.connect(self.toggle_debug)
        l.addWidget(self.btn_debug)
        
        l.addSpacing(20)
        
        # Section 2: Memory Tools
        l.addWidget(QLabel("MEMORY OPERATIONS"))
        
        btn_create = NeonButton("CREATE MEMORY", t['accent'])
        btn_create.clicked.connect(lambda: self.creation_requested.emit())
        l.addWidget(btn_create)
        
        btn_manage = NeonButton("MANAGE PINS", t['border'])
        btn_manage.clicked.connect(self.open_pin_manager)
        l.addWidget(btn_manage)
        
        btn_purge = NeonButton("PURGE MEMORY (KEEP PINS)", "#FF4444")
        btn_purge.clicked.connect(self.request_purge)
        btn_purge.setStyleSheet(f"color: #FF4444; border: 1px solid #FF4444; background: transparent;")
        l.addWidget(btn_purge)
        
        l.addSpacing(10)
        
        btn_nuke = NeonButton("TABULA RASA (NUKE ALL)", "#FF00FF") # Magenta Nuclear
        btn_nuke.clicked.connect(self.request_tabula_rasa)
        # Intense style
        btn_nuke.setStyleSheet("color: #FF00FF; border: 1px solid #FF00FF; background: transparent; font-weight: bold;")
        l.addWidget(btn_nuke)
        
        l.addSpacing(10)
        
        btn_optimize = NeonButton("OPTIMIZE SYSTEM RAM", "#00FFFF") # Cyan
        btn_optimize.clicked.connect(self.show_ram_optimizer)
        btn_optimize.setStyleSheet("color: #00FFFF; border: 1px solid #00FFFF; background: transparent;")
        l.addWidget(btn_optimize)
        
        l.addStretch()
        
        # Easter Egg - uses dim theme color
        h = QHBoxLayout()
        h.addStretch()
        self.easter_btn = QPushButton("(b'.')b")
        self.easter_btn.setFlat(True)
        self.easter_btn.setStyleSheet(f"color: {t['border']}; font-weight: bold; border: none;")
        self.easter_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.easter_btn.clicked.connect(self.trigger_easter_egg)
        h.addWidget(self.easter_btn)
        l.addLayout(h)
        
        return w

    def _create_about_page(self):
        t = self._get_theme()
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Why I Built This")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        # Use stylesheet for text wrapping if needed, but Label is standard
        title.setStyleSheet(f"color: {t['accent']}; background: transparent;")
        l.addWidget(title)
        
        l.addSpacing(10)
        
        # Body
        body_text = """
I made this app because the current options out there just didn’t cut it. Windows’ built-in memory is shifty as hell, constantly trying to ship your data off to Microsoft. Why the fuck do they need to know what I copy and paste? Seriously. They can fuck right off.

So I built the solution. This is a simple, standalone smart clipboard. It keeps your data local and packs the advanced features I actually need to get work done. No spying. Just efficiency.
"""
        body = QLabel(body_text.strip())
        body.setWordWrap(True)
        body.setFont(QFont("Segoe UI", 10))
        body.setStyleSheet(f"color: {t['fg']}; background: transparent; line-height: 1.4;")
        l.addWidget(body)
        
        l.addStretch()
        
        # Signature & Link
        sig_layout = QHBoxLayout()
        sig_layout.addStretch()
        
        sig_btn = QPushButton("(b',')b - h4 - { Be Your Best }")
        sig_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        sig_btn.setFlat(True)
        sig_btn.setStyleSheet(f"""
            QPushButton {{
                color: {t['accent']};
                font-weight: bold;
                text-align: right;
                border: none;
                background: transparent;
                font-family: 'Consolas', monospace;
            }}
            QPushButton:hover {{
                text-decoration: underline;
                color: {t['fg']};
            }}
        """)
        sig_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/m3rr")))
        sig_layout.addWidget(sig_btn)
        
        l.addLayout(sig_layout)
        
        return w

    def open_pin_manager(self):
        from .pin_manager import PinManagerWindow
        self.pin_win = PinManagerWindow(self.db)
        self.pin_win.show()

    def request_purge(self):
        # We can implement a confirmation here or just emit
        from PyQt6.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setWindowTitle("NUCLEAR PURGE")
        msg.setText("Are you sure you want to PURGE all unpinned history?")
        msg.setInformativeText("This action cannot be undone.")
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        # Style the popup a bit (basic styling, proper theming would be better but this is quick)
        t = self._get_theme()
        msg.setStyleSheet(f"background-color: {t['bg']}; color: {t['fg']};")
        
        if msg.exec() == QMessageBox.StandardButton.Yes:
            self.purge_requested.emit()

    def request_tabula_rasa(self):
        from PyQt6.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setWindowTitle("TABULA RASA")
        msg.setText("WARNING: TABULA RASA DETECTED.")
        msg.setInformativeText("This will wipe EVERYTHING. Including Pinned items.\n\nAre you absolutely sure?")
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        t = self._get_theme()
        msg.setStyleSheet(f"background-color: {t['bg']}; color: #FF00FF;")
        
        if msg.exec() == QMessageBox.StandardButton.Yes:
            self.tabula_rasa_requested.emit()

    def show_ram_optimizer(self):
        """Displays RAM Optimization Dialog."""
        msg = QMessageBox(self)
        msg.setWindowTitle("RAM OPTIMIZATION PROTOCOL")
        msg.setText("Select Memory Cleaning Intensity")
        msg.setInformativeText("GENTLE: Clears this app's Working Set.\nAGGRESSIVE: Trims Working Sets for ALL accessible processes (System Wide).")
        
        # Custom Buttons
        btn_gentle = msg.addButton("GENTLE CLEAN", QMessageBox.ButtonRole.ActionRole)
        btn_aggressive = msg.addButton("AGGRESSIVE CLEAN", QMessageBox.ButtonRole.ActionRole)
        btn_cancel = msg.addButton(QMessageBox.StandardButton.Cancel)
        
        t = self._get_theme()
        # Ensure buttons have visible text
        msg.setStyleSheet(f"""
            QMessageBox {{ background-color: {t['bg']}; color: {t['fg']}; }}
            QLabel {{ color: {t['fg']}; }}
            QPushButton {{ background-color: {t['border']}; color: {t['fg']}; padding: 5px 15px; border: 1px solid {t['accent']}; }}
            QPushButton:hover {{ background-color: {t['accent']}; color: {t['bg']}; }}
        """)
        
        msg.exec()
        
        clicked = msg.clickedButton()
        if clicked == btn_gentle:
             AdminTools.clean_system_memory(aggressive=False)
             # Optional: Show result or silent? User likes feedback.
             # Use LOGGER. Info box might be annoying if used often.
             # Maybe status bar or just log.
             LOGGER.log("User triggered Gentle RAM Clean.")
        elif clicked == btn_aggressive:
             AdminTools.clean_system_memory(aggressive=True)
             LOGGER.log("User triggered Aggressive RAM Clean.")

    def toggle_debug(self):
        t = self._get_theme()
        if "DEACTIVATED" in self.btn_debug.text() or "OFF" in self.btn_debug.text():
            self.btn_debug.setText("GOD MODE: ACTIVATED")
            self.btn_debug.setStyleSheet(f"""
                QPushButton {{
                    background-color: {t['accent']};
                    color: {t['bg']};
                    border: 2px solid {t['accent']};
                    border-radius: 4px; padding: 8px; font-weight: bold;
                }}
            """)
            print("[DEBUG] NUCLEAR DEBUG MODE ENGAGED.")
            
            # Start God Mode Logger
            from ..core.god_logger import GodModeLogger
            GodModeLogger().start()
            
            # Show Admin Tab
            self.debug_toggled.emit(True)
            
        else:
            self.btn_debug.setText("GOD MODE: DEACTIVATED")
            self.btn_debug.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {t['fg']};
                    border: 1px solid {t['border']};
                    border-radius: 4px; padding: 8px;
                }}
            """)
            print("[DEBUG] Debug Mode Disengaged.")
            
            # Stop God Mode Logger
            from ..core.god_logger import GodModeLogger
            GodModeLogger().stop()
            
            # Hide Admin Tab
            self.debug_toggled.emit(False)

    def _god_mode_click(self):
        AdminTools.start_system_debugger()
        
    def trigger_easter_egg(self):
        if self.easter_egg_state == 0:
            self.easter_btn.setText("d('.'d)")
            self.easter_egg_state = 1
            self.show_bloat_warning()
        else:
            self.easter_btn.setText("(b'.')b")
            self.easter_egg_state = 0

    def show_bloat_warning(self):
        """Themed easter egg popup with cyberpunk aesthetic."""
        t = self._get_theme()
        msg = QMessageBox(self)
        msg.setWindowTitle("⚠ NUCLEAR WARNING ⚠")
        msg.setText("What you're about to do is simulate MEMORY BLOAT.\n\nThe app will restart when it hits 1.2GB of RAM usage.\n\nThis is for stress-testing only.")
        msg.setIcon(QMessageBox.Icon.Warning)
        
        # Cyberpunk styled popup
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {t['bg']};
                border: 2px solid {t['accent']};
                border-radius: 8px;
            }}
            QMessageBox QLabel {{
                color: {t['fg']};
                font-family: 'Consolas', monospace;
                font-size: 10pt;
                padding: 10px;
            }}
            QMessageBox QPushButton {{
                background-color: {t['glass']};
                color: {t['fg']};
                border: 1px solid {t['accent']};
                border-radius: 4px;
                padding: 8px 16px;
                font-family: 'Segoe UI';
                font-weight: 600;
                min-width: 100px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: {t['glass']};
                color: {t['accent']};
            }}
            QMessageBox QPushButton:pressed {{
                background-color: {t['accent']};
                color: {t['bg']};
            }}
        """)
        
        btn_do = msg.addButton("☢ DO IT!", QMessageBox.ButtonRole.ActionRole)
        btn_debug_do = msg.addButton("🔧 DEBUG + BLOAT", QMessageBox.ButtonRole.ActionRole)
        btn_cancel = msg.addButton("✕ CANCEL", QMessageBox.ButtonRole.RejectRole)
        
        msg.exec()
        
        if msg.clickedButton() == btn_do:
            from ..core.watchdog import MemoryWatchdog
            MemoryWatchdog.simulate_bloat()
        elif msg.clickedButton() == btn_debug_do:
            self.toggle_debug()
            from ..core.watchdog import MemoryWatchdog
            MemoryWatchdog.simulate_bloat()

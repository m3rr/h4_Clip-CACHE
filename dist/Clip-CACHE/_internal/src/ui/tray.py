from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QTimer
import os

class SystemTray(QSystemTrayIcon):
    """
    System Tray Icon.
    - Shows System Stats in Tooltip.
    - Context Menu: About, Help, Exit, Purge.
    """
    def __init__(self, monitor, app_manager, parent=None):
        super().__init__(parent)
        self.monitor = monitor
        self.app_manager = app_manager # Access to main app logic for Exit/Purge
        
        # Resource Path Helper
        def resolve_resource_path(relative_path):
            import sys
            if hasattr(sys, '_MEIPASS'):
                return os.path.join(sys._MEIPASS, relative_path)
            
            # Dev Mode (Relative to Source Root)
            # This file is in src/ui/tray.py. Root is ../../
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            candidate = os.path.join(base_path, relative_path)
            if os.path.exists(candidate):
                return candidate

            # PyInstaller OneDir (Root is executable dir)
            if getattr(sys, 'frozen', False):
                base_path = os.path.dirname(sys.executable)
                candidate = os.path.join(base_path, relative_path)
                if os.path.exists(candidate):
                    return candidate
            
            return os.path.abspath(relative_path)

        # Load Icon
        icon_path = resolve_resource_path(os.path.join("assets", "image_assets", "icon.ico"))
        if os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
        else:
            print(f"[TRAY] Icon not found at: {icon_path}")
            # Fallback icon logic if needed, or it will just be blank

        # Menu
        self.menu = QMenu()
        self._init_menu()
        self.setContextMenu(self.menu)

        # Timer for Tooltip updates
        self.stats_timer = QTimer(self)
        self.stats_timer.timeout.connect(self._update_tooltip)
        self.stats_timer.start(2000) # Update every 2 seconds
        
        # Double Click Action
        self.activated.connect(self.on_activated)

        self.setVisible(True)
        self.show()

    def on_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.app_manager.toggle_window()

    def _init_menu(self):
        # Theme-aware menu styling
        from .theme_manager import ThemeManager
        from ..core.config import ConfigManager
        t = ThemeManager.get_theme(ConfigManager().get_theme())
        
        self.menu.setStyleSheet(f"""
            QMenu {{
                background-color: {t['bg']};
                color: {t['accent']};
                border: 1px solid {t['accent']};
            }}
            QMenu::item:selected {{
                background-color: {t['accent']};
                color: {t['bg']};
            }}
        """)

        # Actions
        about_action = QAction("About", self)
        about_action.triggered.connect(self.app_manager.show_about)
        
        help_action = QAction("Help", self)
        help_action.triggered.connect(self.app_manager.show_help)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.app_manager.quit_app)

        purge_action = QAction("Exit and Purge", self)
        purge_action.triggered.connect(self.app_manager.quit_and_purge)

        self.menu.addAction(about_action)
        self.menu.addAction(help_action)
        self.menu.addSeparator()
        self.menu.addAction(exit_action)
        self.menu.addAction(purge_action)

    def _update_tooltip(self):
        # Get stats from Monitor
        stats = self.monitor.get_stats()
        
        # CPU Temp GPU RAM NET
        # Format:
        # CPU: 12% | RAM: 4.5G
        # GPU: 65C | D:1.2M U:0.4M
        
        tooltip = (f"CPU: {stats.get('cpu')}% | RAM: {stats.get('ram_used_gb')}GB\n"
                   f"GPU: {stats.get('gpu_temp')}C | D:{stats.get('net_down')} U:{stats.get('net_up')}")
        
        self.setToolTip(tooltip)

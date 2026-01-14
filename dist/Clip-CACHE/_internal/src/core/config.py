from PyQt6.QtCore import QSettings

class ConfigManager:
    """
    Manages application settings persistence using QSettings.
    Stores: Theme, Window Geometry, Window State.
    """
    def __init__(self):
        self.settings = QSettings("H4_Tools", "Clip-CACHE")

    def get_theme(self):
        return self.settings.value("theme", "Deep Void")

    def set_theme(self, theme_name):
        self.settings.setValue("theme", theme_name)

    def get_window_geometry(self):
        return self.settings.value("geometry")

    def set_window_geometry(self, geometry):
        self.settings.setValue("geometry", geometry)

    def get_window_state(self):
        return self.settings.value("window_state")

    def set_window_state(self, state):
        self.settings.setValue("window_state", state)

    def get_start_in_background(self):
        """Returns True if app should start minimized to tray."""
        return self.settings.value("start_in_background", False, type=bool)

    def set_start_in_background(self, enabled):
        self.settings.setValue("start_in_background", enabled)

    def get_incognito_mode(self):
        """Returns True if Incognito Mode is ON (No Tray Icon when minimized)."""
        return self.settings.value("incognito_mode", False, type=bool)

    def set_incognito_mode(self, enabled):
        self.settings.setValue("incognito_mode", enabled)

    def get(self, key, default=None):
        return self.settings.value(key, default)

    def set(self, key, value):
        self.settings.setValue(key, value)

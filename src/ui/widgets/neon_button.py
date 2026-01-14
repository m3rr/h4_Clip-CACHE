from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt

class NeonButton(QPushButton):
    """
    Cyberpunk Glassmorphism Button - 100% THEME AWARE.
    - NO HARDCODED COLORS (styling handled by theme_manager.py)
    - Sets ObjectName for global QSS matching
    """
    def __init__(self, text, accent_color=None, parent=None):
        super().__init__(text, parent)
        self.accent_color = accent_color  # Optional override (unused - global styles apply)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("NeonButtonWidget")  # For global theme styling via theme_manager.py
        # Note: ALL styling is handled by theme_manager.py global stylesheet
        # This class has ZERO hardcoded colors

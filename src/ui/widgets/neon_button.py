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

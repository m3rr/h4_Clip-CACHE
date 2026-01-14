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

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices, QPainter, QLinearGradient, QPen, QColor, QFont
from .theme_manager import ThemeManager
from ..core.config import ConfigManager

class AboutWindow(QWidget):
    """
    Theme-Aware About Popup
    - User specified copy
    - Github Link
    - Custom painted border/background (no hardcoded colors)
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(500, 350)
        self.setObjectName("AboutWindow")
        self.config = ConfigManager()
        self.setup_ui()
    
    def _get_theme(self):
        return ThemeManager.get_theme(self.config.get_theme())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        t = self._get_theme()
        
        # Background: Gradient
        bg_color = QColor(t['bg'])
        darker_bg = bg_color.darker(120)
        grad = QLinearGradient(0, 0, self.width(), self.height())
        grad.setColorAt(0.0, bg_color)
        grad.setColorAt(1.0, darker_bg)
        painter.setBrush(grad)
        
        # Border
        accent = QColor(t['accent'])
        painter.setPen(QPen(accent, 2))
        painter.drawRoundedRect(self.rect().adjusted(2,2,-2,-2), 8, 8)
        
        # Grid overlay (subtle)
        grid_color = QColor(accent)
        grid_color.setAlpha(15)
        painter.setPen(grid_color)
        for x in range(0, self.width(), 40):
            painter.drawLine(x, 0, x, self.height())
        for y in range(0, self.height(), 40):
            painter.drawLine(0, y, self.width(), y)

    def setup_ui(self):
        t = self._get_theme()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("Why I Built This")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {t['accent']}; background: transparent;")
        layout.addWidget(title)
        
        layout.addSpacing(10)
        
        # Body Text
        body_text = """
I made this app because the current options out there just didn’t cut it. Windows’ built-in memory is shifty as hell, constantly trying to ship your data off to Microsoft. Why the fuck do they need to know what I copy and paste? Seriously. They can fuck right off.

So I built the solution. This is a simple, standalone smart clipboard. It keeps your data local and packs the advanced features I actually need to get work done. No spying. Just efficiency.
"""
        body = QLabel(body_text.strip())
        body.setWordWrap(True)
        body.setFont(QFont("Segoe UI", 10))
        body.setStyleSheet(f"color: {t['fg']}; background: transparent; line-height: 1.4;")
        layout.addWidget(body)
        
        layout.addStretch()
        
        # Signature & Link
        sig_layout = QHBoxLayout()
        sig_layout.addStretch()
        
        sig_btn = QPushButton("(b',')b - h4 - { Be Your Best }")
        sig_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        sig_btn.setFlat(True)
        # Theme aware link style
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
        sig_btn.clicked.connect(self.open_github)
        sig_layout.addWidget(sig_btn)
        
        layout.addLayout(sig_layout)
        
        # Close on click outside (handled by focus or explicit close btn if needed, 
        # but user asked for popup. Let's add a small close X top right or just click to close?)
        # Let's add a close button for clarity/usability
        close_btn = QPushButton("✕", self)
        close_btn.setGeometry(self.width() - 30, 10, 20, 20)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{ color: {t['fg']}; background: transparent; border: none; font-weight: bold; }}
            QPushButton:hover {{ color: {t['accent']}; }}
        """)
        close_btn.clicked.connect(self.close)

    def open_github(self):
        QDesktopServices.openUrl(QUrl("https://github.com/m3rr"))
    
    def mousePressEvent(self, event):
        # Allow dragging window
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QLinearGradient
from .widgets.neon_button import NeonButton
from ..core.logger import LOGGER

class SettingsOverlay(QWidget):
    """
    Modal-like overlay for Settings.
    - Debug Mode Toggle.
    - Theme Selector.
    - Cyberpunk Aesthetic (Grid Background).
    """
    debug_toggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(300, 300) # Slightly taller for themes
        
        # Style controls only - Background handled in PaintEvent
        self.setStyleSheet("""
            QLabel {
                color: #FFD700;
                font-family: 'Segoe UI';
                font-weight: bold;
                border: none;
                background: transparent;
            }
        """)
        
        self.setup_ui()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 1. Background Gradient (Dark Tech)
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0.0, QColor(15, 15, 20, 250))
        grad.setColorAt(1.0, QColor(5, 5, 10, 250))
        painter.setBrush(grad)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 10, 10)
        
        # 2. Grid Pattern
        grid_color = QColor(255, 215, 0, 20) # Faint Gold
        painter.setPen(grid_color)
        grid_size = 20
        
        for x in range(0, self.width(), grid_size):
            painter.drawLine(x, 0, x, self.height())
            
        for y in range(0, self.height(), grid_size):
            painter.drawLine(0, y, self.width(), y)
            
        # 3. Border
        painter.setPen(QPen(QColor("#FFD700"), 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(self.rect().adjusted(1,1,-1,-1), 10, 10)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        lbl_title = QLabel("SYSTEM CONFIG")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_title.setStyleSheet("font-size: 14pt; letter-spacing: 2px; border-bottom: 1px solid #444; padding-bottom: 5px;")
        layout.addWidget(lbl_title)
        
        # Debug Mode
        self.btn_debug = NeonButton("DEBUG MODE: OFF", "#555")
        self.btn_debug.clicked.connect(self.toggle_debug)
        layout.addWidget(QLabel("DIAGNOSTICS"))
        layout.addWidget(self.btn_debug)
        
        # Power User / God Mode
        self.btn_sys_debug = NeonButton("SYSTEM DEBUGGER (GOD MODE)", "#FF00FF") 
        self.btn_sys_debug.clicked.connect(self.toggle_sys_debug)
        layout.addWidget(self.btn_sys_debug)
        
        # Theme (Placeholder -> Real later)
        layout.addWidget(QLabel("VISUAL THEME"))
        self.btn_theme = NeonButton("CYBERPUNK (DEFAULT)", "#00FFFF")
        layout.addWidget(self.btn_theme)
        
        layout.addStretch()
        
        # Close
        btn_close = NeonButton("CLOSE OVERLAY", "#FF3333")
        btn_close.clicked.connect(self.hide)
        layout.addWidget(btn_close)

    def toggle_debug(self):
        # Toggle UI state
        if "OFF" in self.btn_debug.text():
            self.btn_debug.setText("DEBUG MODE: ON")
            self.btn_debug.setStyleSheet("background-color: #FF0000; color: white; border: 1px solid white;")
            LOGGER.set_debug(True)
            self.debug_toggled.emit(True)
        else:
            self.btn_debug.setText("DEBUG MODE: OFF")
            self.btn_debug.setStyleSheet("") # Reset (relies on NeonButton default or re-apply)
            # Re-apply base neon style for consistent look if reset fails
            self.btn_debug.accent_color = "#555"
            # We'll just re-set text, let logic handle calling LOGGER
            LOGGER.set_debug(False)
            self.debug_toggled.emit(False)

    def toggle_sys_debug(self):
        # Import here to avoid circular dependency if needed, or rely on global import
        from ..core.admin_tools import AdminTools
        
        if "OFF" in self.btn_debug.text(): 
            # Force standard debug on if God Mode is requested
            self.toggle_debug()
            
        AdminTools.start_system_debugger()
        self.btn_sys_debug.setText("GOD MODE: ACTIVE (LOGGING)")
        self.btn_sys_debug.setStyleSheet("background-color: #FF00FF; color: white;")

    def show_centered(self, parent_geo):
        # Center on parent window
        x = parent_geo.x() + (parent_geo.width() - self.width()) // 2
        y = parent_geo.y() + (parent_geo.height() - self.height()) // 2
        self.move(x, y)
        self.show()
        self.raise_()

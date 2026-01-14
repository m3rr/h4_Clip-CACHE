from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTextEdit, QFileDialog, QTabWidget, QLineEdit)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPainter, QLinearGradient, QColor
from .theme_manager import ThemeManager
from ..core.config import ConfigManager
from .widgets.neon_button import NeonButton

class CreationWindow(QWidget):
    """
    Dialog to manually create memory items (Text/File).
    """
    def __init__(self, clipboard_manager, parent=None):
        super().__init__(parent)
        self.clipboard_manager = clipboard_manager
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(500, 400)
        self.config = ConfigManager()
        self.setup_ui()

    def _get_theme(self):
        return ThemeManager.get_theme(self.config.get_theme())
    
    def paintEvent(self, event):
        # Custom Paint like other popups
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
        header = QLabel("CREATE MEMORY")
        header.setStyleSheet(f"color: {t['accent']}; font-weight: bold; font-size: 14pt;")
        h_layout.addWidget(header)
        h_layout.addStretch()
        
        close = QPushButton("✕")
        close.setFixedSize(25,25)
        close.clicked.connect(self.close)
        close.setStyleSheet(f"color: {t['fg']}; background: transparent; border: none; font-weight: bold;")
        h_layout.addWidget(close)
        l.addLayout(h_layout)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border: 1px solid {t['border']}; }}
            QTabBar::tab {{
                background: {t['bg']};
                color: {t['fg']};
                padding: 8px 12px;
                border: 1px solid {t['border']};
                border-bottom: none;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background: {t['glass']};
                color: {t['accent']};
                border-top: 2px solid {t['accent']};
            }}
        """)
        
        # Text Tab
        self.text_tab = QWidget()
        tl = QVBoxLayout(self.text_tab)
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Type your memory here...")
        self.text_input.setStyleSheet(f"background: rgba(0,0,0,50); color: {t['fg']}; border: none;")
        tl.addWidget(self.text_input)
        
        submit_text = NeonButton("INJECT TEXT", t['accent'])
        submit_text.clicked.connect(self.inject_text)
        tl.addWidget(submit_text)
        
        self.tabs.addTab(self.text_tab, "TEXT / CODE")
        
        # File Tab
        self.file_tab = QWidget()
        fl = QVBoxLayout(self.file_tab)
        
        self.file_path = QLineEdit()
        self.file_path.setPlaceholderText("No file selected...")
        self.file_path.setStyleSheet(f"background: rgba(0,0,0,50); color: {t['fg']}; border: 1px solid {t['border']}; padding: 5px;")
        fl.addWidget(self.file_path)
        
        browse = NeonButton("BROWSE FILE", t['border'])
        browse.clicked.connect(self.browse_file)
        fl.addWidget(browse)
        
        submit_file = NeonButton("INJECT FILE", t['accent'])
        submit_file.clicked.connect(self.inject_file)
        fl.addWidget(submit_file)
        
        self.tabs.addTab(self.file_tab, "FILE PATH")
        
        l.addWidget(self.tabs)
        
    def browse_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if path:
            self.file_path.setText(path)
            
    def inject_text(self):
        text = self.text_input.toPlainText()
        if text:
            # Manually add to clipboard manager
            # We treat it as 'text'
            self.clipboard_manager.add_item('text', text)
            print("[CREATION] Injected Text Memory")
            self.close()
            
    def inject_file(self):
        path = self.file_path.text()
        if path:
            self.clipboard_manager.add_item('file', path)
            print("[CREATION] Injected File Memory")
            self.close()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

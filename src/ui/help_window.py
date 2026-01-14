from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTextBrowser, QLineEdit, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QLinearGradient, QPen, QColor, QFont, QTextDocument
from .theme_manager import ThemeManager
from ..core.config import ConfigManager
from .widgets.neon_button import NeonButton

class HelpWindow(QWidget):
    """
    Theme-Aware Help Manual with Search.
    - Verbose documentation
    - Search functionality (Find Next/Prev)
    - 100% Theme Aware (No hardcoded colors)
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(700, 600)
        self.setObjectName("HelpWindow")
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
        pen = QPen(accent, 2)
        painter.setPen(pen)
        painter.drawRoundedRect(self.rect().adjusted(1,1,-1,-1), 8, 8)
        
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
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # --- HEADER ---
        header_layout = QHBoxLayout()
        title = QLabel("CLIP-CACHE MANUAL v1.0")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        # Theme aware styling
        title.setStyleSheet(f"color: {t['accent']}; background: transparent; letter-spacing: 2px;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Close Button
        btn_close = QPushButton("✕")
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setFixedSize(30, 30)
        btn_close.clicked.connect(self.close)
        btn_close.setStyleSheet(f"""
            QPushButton {{ 
                color: {t['fg']}; 
                background: transparent; 
                border: none; 
                font-size: 14pt;
                font-weight: bold;
            }}
            QPushButton:hover {{ color: {t['accent']}; }}
        """)
        header_layout.addWidget(btn_close)
        layout.addLayout(header_layout)
        
        # --- SEARCH BAR ---
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search Manual...")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background: {t['glass']};
                color: {t['fg']};
                border: 1px solid {t['border']};
                border-radius: 4px;
                padding: 6px;
                font-family: 'Segoe UI';
            }}
            QLineEdit:focus {{
                border: 1px solid {t['accent']};
            }}
        """)
        self.search_input.returnPressed.connect(self.find_next)
        search_layout.addWidget(self.search_input)
        
        btn_prev = NeonButton("PREV", t['border'])
        btn_prev.setFixedSize(60, 30)
        btn_prev.clicked.connect(self.find_prev)
        search_layout.addWidget(btn_prev)
        
        btn_next = NeonButton("NEXT", t['border'])
        btn_next.setFixedSize(60, 30)
        btn_next.clicked.connect(self.find_next)
        search_layout.addWidget(btn_next)
        
        layout.addLayout(search_layout)
        
        # --- CONTENT AREA ---
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(False) # Keep it contained
        # Theme aware scrollbar & content
        self.browser.setStyleSheet(f"""
            QTextBrowser {{
                background-color: rgba(0,0,0,50);
                color: {t['fg']};
                border: 1px solid {t['border']};
                border-radius: 4px;
                padding: 10px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 10pt;
                line-height: 1.5;
            }}
            QScrollBar:vertical {{
                border: none;
                background: {t['bg']};
                width: 10px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {t['border']};
                min-height: 20px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {t['accent']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        
        self.set_content(t)
        layout.addWidget(self.browser)
        
        # Resize handle hint (bottom right)
        # For now fixed size window as requested by "popup", but draggable

        # Signature & Link (Bottom Right)
        sig_layout = QHBoxLayout()
        sig_layout.addStretch()
        
        from PyQt6.QtCore import QUrl
        from PyQt6.QtGui import QDesktopServices

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
        sig_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/m3rr")))
        sig_layout.addWidget(sig_btn)
        
        layout.addLayout(sig_layout)

    def set_content(self, t):
        """Generates HTML content with theme colors."""
        accent = t['accent']
        fg = t['fg']
        border = t['border']
        
        html = f"""
        <html>
        <head>
            <style>
                h1 {{ color: {accent}; font-size: 18pt; margin-bottom: 5px; }}
                h2 {{ color: {accent}; font-size: 14pt; margin-top: 15px; margin-bottom: 5px; border-bottom: 1px solid {border}; }}
                h3 {{ color: {fg}; font-size: 12pt; font-weight: bold; margin-top: 10px; }}
                p {{ color: {fg}; margin-bottom: 10px; }}
                li {{ color: {fg}; margin-bottom: 5px; }}
                .highlight {{ color: {accent}; font-weight: bold; }}
                .key {{ background-color: {border}; color: {fg}; padding: 2px 5px; border-radius: 3px; font-family: monospace; }}
            </style>
        </head>
        <body>
            <h1>WELCOME TO CLIP-CACHE</h1>
            <p>Clip-CACHE is a standalone, secure, and efficient clipboard manager designed to keep your data local while providing advanced tools for power users.</p>
            
            <h2>CORE CONCEPTS</h2>
            <ul>
                <li><strong>Local History:</strong> Everything you copy is stored locally in an encrypted database. Nothing leaves your machine.</li>
                <li><strong>Smart Types:</strong> Automatically distinguishes between Text, Images, and Files.</li>
                <li><strong>Theme Aware:</strong> Fits seamlessly into your workflow with customizable cyberpunk themes.</li>
            </ul>

            <h2>INTERFACE & BUTTONS</h2>
            
            <h3>1. The Search Bar</h3>
            <p>Located at the top. Simply start typing to filter your clipboard history instantly. It supports partial matching for text and file paths.</p>
            
            <h3>2. History List (Left Pane)</h3>
            <p>Displays your recent clipboard items. Icons indicate the type:</p>
            <ul>
                <li>📝 <strong>Text:</strong> Code snippets, plain text, URLs.</li>
                <li>🖼️ <strong>Image:</strong> Screenshots, copied photos.</li>
                <li>📁 <strong>File:</strong> Copied file paths/properties.</li>
            </ul>
            
            <h3>3. Preview Pane (Right Pane)</h3>
            <p>Shows a detailed view of the selected item. Code syntax highlighting is automatic. Images are displayed with aspect ratio preserved.</p>
            
            <h3>4. Action Buttons</h3>
            <ul>
                <li><span class="highlight">MAKE ACTIVE</span>: Copies the selected item back to your system clipboard, ready to paste.</li>
                <li><span class="highlight">PIN ITEM</span>: Locks the item in your history. It will NOT be removed when the history limit is reached or during cleanup.</li>
                <li><span class="highlight">DELETE</span>: Permanently removes the item from the database.</li>
            </ul>

            <h2>SETTINGS & CONFIGURATION</h2>
            <p>Access settings via the 'Gear' icon or Tray menu.</p>
            
            <h3>General</h3>
            <ul>
                <li><strong>Start with Windows:</strong> Automatically launch Clip-CACHE on login.</li>
                <li><strong>Start in Background:</strong> Launch minimized to the system tray, keeping your desktop clean.</li>
            </ul>
            
            <h3>Visuals</h3>
            <p>Select from various themes (Cyberpunk Neon, Deep Void, Ash Grey, etc.). The interface updates instantly.</p>
            
            <h3>Power User</h3>
            <ul>
                <li><strong>Debug Mode:</strong> Enables detailed logging for troubleshooting.</li>
                <li><strong>God Mode:</strong> System debugger (Use with caution).</li>
            </ul>

            <h2>TROUBLESHOOTING & COMMON ERRORS</h2>
            
            <h3>Global Hotkey Not Working</h3>
            <p>The default hotkey is <span class="key">CTRL</span> + <span class="key">SHIFT</span> + <span class="key">NUMPAD +</span>.</p>
            <ul>
                <li>Ensure you are using the PLUS key on the number pad, not the main keyboard.</li>
                <li>If the window doesn't appear, check if it's minimized in the tray.</li>
                <li>Try restarting the app as Administrator if global keys are blocked by another elevated app.</li>
            </ul>
            
            <h3>Images Not Saving</h3>
            <p>Clip-CACHE caches images locally. If your disk is full or permissions are denied in the output folder, images might not appear.</p>
            
            <h3>"Nuclear" Memory Warnings</h3>
            <p>This is a safety feature. If the app detects memory leaks (simulated or real) > 1.2GB, it may restart to protect system stability.</p>

            <h2>WHY EVERYTHING?</h2>
            <p>Windows Clipboard Manager sends telemetry. Third-party tools are often bloated or cloud-connected. Clip-CACHE exists to be the <strong>opposite</strong>:</p>
            <ul>
                <li><strong>Privacy First:</strong> No cloud. No telemetry.</li>
                <li><strong>Efficiency:</strong> Keyboard driven, fast search.</li>
                <li><strong>Aesthetics:</strong> Because tools shouldn't look boring.</li>
            </ul>
            
            <p>Enjoy efficiency.</p>
        </body>
        </html>
        """
        self.browser.setHtml(html)

    def find_next(self):
        text = self.search_input.text()
        if not text: return
        self.browser.find(text)

    def find_prev(self):
        text = self.search_input.text()
        if not text: return
        self.browser.find(text, QTextDocument.FindFlag.FindBackward)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

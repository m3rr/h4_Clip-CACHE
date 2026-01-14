from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient, QIcon, QPixmap, QPainterPath
import os

class HistoryItem(QWidget):
    clicked = pyqtSignal(dict)
    
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.setFixedSize(260, 75)  # W:260, H:75 (tighter)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.hover = False
        
        # Determine Icon/Type
        self.type = data.get('type', 'text')
        self.preview = data.get('preview', '')
        self.content = data.get('content', '')
        self.metadata = data.get('metadata', {})
        if not isinstance(self.metadata, dict): self.metadata = {}

        # Default Title (What to show in large font)
        # Priority: Custom Name > Filename (for files) > Content Snippet (for text)
        
        custom_name = self.metadata.get('display_name')
        
        if custom_name:
            self.display_title = custom_name
        else:
            if self.type == 'image' or self.type == 'file':
                # Show Filename
                self.display_title = os.path.basename(self.content) if self.content else "Unknown File"
            else:
                # Text: Show snippet
                clean_text = self.content.replace("\n", " ").strip()
                self.display_title = (clean_text[:25] + '...') if len(clean_text) > 25 else clean_text
                if not self.display_title: self.display_title = "Empty Text"
                
        self.setup_ui()
        
    def setup_ui(self):
        # We handle painting in paintEvent
        pass
    
    def sizeHint(self):
        """Return proper size hint - match fixed size."""
        return QSize(260, 75)

    def enterEvent(self, event):
        self.hover = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.hover = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.data)
        # CRITICAL: Call super to allow event to propagate to QListWidget
        # This enables itemClicked signal to fire on the parent list
        super().mousePressEvent(event)
            
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Colors (Dynamic based on theme eventually, hardcoded for now or use global QSS variables if set)
        accent = QColor("#FFD700") 
        if self.type == 'image': accent = QColor("#00FFFF")
        if self.type == 'file': accent = QColor("#FF00FF")
        
        bg_col = QColor(20, 20, 25, 180)
        border_col = QColor(60, 60, 70, 150)
        
        if self.property("selected"):
            # Strong Highlight
            bg_col = QColor(40, 40, 50, 240)
            border_col = accent
        elif self.hover:
             bg_col = QColor(40, 40, 50, 220)
             border_col = accent
        
        # 1. Main Container
        rect = QRectF(5, 5, self.width()-10, self.height()-10)
        path = QPainterPath() 
        path.addRoundedRect(rect, 10, 10)
        
        painter.setBrush(QBrush(bg_col))
        painter.setPen(QPen(border_col, 2 if self.property("selected") else 1))
        painter.drawPath(path)
        
        # 2. Icon Container (The requested Rounded Square)
        # Transformation for "Swivel" effect?
        scale_factor = 1.0
        if self.property("selected"):
            scale_factor = 1.2
            
        # Calc Centered Scaled Rect
        base_w, base_h = 50, 50
        w, h = base_w * scale_factor, base_h * scale_factor
        cx, cy = 15 + 25, 15 + 25 # Center of original box (15+50/2)
        # 2. Icon (Shrunk to 40x40 to prevent overlap)
        icon_rect = QRectF(15, 20, 40, 40)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 0, 0, 80))
        painter.drawRoundedRect(icon_rect, 8, 8)
        
        font = painter.font()
        font.setBold(True)
        font.setPointSize(16)
        painter.setFont(font)
        painter.setPen(QColor(0, 255, 255))
        
        icon_char = "T"
        if self.type == 'image': icon_char = "I"
        if self.type == 'file': icon_char = "F"
        
        painter.drawText(icon_rect, Qt.AlignmentFlag.AlignCenter, icon_char)
        
        # 3. Content Text
        painter.setPen(QPen(QColor(220, 220, 220), 1))
        font.setPointSize(10)
        font.setBold(False)
        painter.setFont(font)
        
        # Moved text slightly right due to icon margin (15+40+15 = 70)
        text_rect = QRectF(70, 15, self.width()-80, 25)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self.display_title)
        
        # Preview Text
        painter.setPen(QPen(QColor(150, 150, 150), 1))
        font.setPointSize(9)
        painter.setFont(font)
        
        preview_rect = QRectF(70, 40, self.width()-80, 25)
        preview_text = self.data.get('preview', '...')
        
        # Metadata Handling
        meta = self.data.get('metadata', {})
        if not isinstance(meta, dict): 
            meta = {}

        if self.type == 'image':
            w_px = meta.get('width', 0)
            h_px = meta.get('height', 0)
            
            if w_px and h_px:
                txt_preview = f"{w_px} x {h_px} px"
            else:
                txt_preview = "Image"
            
            painter.setPen(QColor(150, 150, 150))
            painter.drawText(preview_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, txt_preview)
            
        elif self.type == 'file':
            count = meta.get('file_count', 1)
            f_ext = meta.get('ext', 'Files')
            painter.setPen(QColor(150, 150, 150))
            painter.drawText(preview_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, f"{count} {f_ext}")
            
        else:
            # Text Preview (Default)
            painter.setPen(QColor(150, 150, 150))
            painter.drawText(preview_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, preview_text)
        
        # Reset Font/Pen just in case
        painter.setPen(QPen(QColor(255, 255, 255), 1))

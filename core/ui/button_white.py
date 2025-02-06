from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QGraphicsDropShadowEffect, QHBoxLayout, QWidget
from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtGui import QColor, QDesktopServices
from core.font.font_manager import FontManager
from core.font.font_pages_manager import FontPagesManager
from core.log.log_manager import log
from core.utils.notif import Notification, NotificationType

class WhiteButton(QFrame):
    clicked = Signal()
    
    def __init__(self, 
                 title="",
                 icon="",
                 parent=None):
        super().__init__(parent)
        self.title = title
        self.icon = icon
        
        self.font_manager = FontManager()
        self.font_pages_manager = FontPagesManager()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)
        
        layout.addStretch()
        
        content_layout = QHBoxLayout()
        content_layout.setSpacing(8)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        if self.icon:
            self.icon_label = QLabel(self.icon)
            self.font_pages_manager.apply_icon_font(self.icon_label, 18)
            self.icon_label.setStyleSheet("""
                QLabel {
                    color: #333333;
                    background: transparent;
                }
            """)
            content_layout.addWidget(self.icon_label)
        
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet("""
            QLabel {
                color: #333333;
                background: transparent;
            }
        """)
        self.font_pages_manager.apply_normal_style(self.title_label)
        content_layout.addWidget(self.title_label)
        
        layout.addLayout(content_layout)
        
        layout.addStretch()
        
        self.setStyleSheet("""
            WhiteButton {
                background: white;
                border-radius: 6px;
                border: 1px solid #E0E0E0;
                min-width: 80px;
                max-width: 200px;
            }
            WhiteButton:hover {
                border: 1px solid #2196F3;
                background: rgba(33, 150, 243, 0.08);
            }
            WhiteButton:hover QLabel {
                color: #2196F3;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
            
    def update_title(self, title):
        self.title = title
        self.title_label.setText(title)
        
    def update_icon(self, icon):
        if hasattr(self, 'icon_label'):
            self.icon_label.setText(icon)
        else:
            self.icon = icon
            self.setup_ui() 
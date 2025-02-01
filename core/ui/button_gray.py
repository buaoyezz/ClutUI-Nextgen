from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt
from core.font.font_manager import FontManager

class ButtonGray(QPushButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.font_manager = FontManager()
        self.font_manager.apply_font(self)
        
        # 设置固定
        self.setFixedSize(200, 50)
        
        # 设置样式
        self.setStyleSheet("""
            QPushButton {
                background-color: #4A4A4A;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #5A5A5A;
            }
            QPushButton:pressed {
                background-color: #3A3A3A;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
                color: #888888;
            }
        """)
        
        self.setFocusPolicy(Qt.NoFocus)
        
    def set_small(self):
        self.setFixedSize(120, 36)
        self.setStyleSheet("""
            QPushButton {
                background-color: #4A4A4A;
                color: white;
                border: none;
                border-radius: 18px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5A5A5A;
            }
            QPushButton:pressed {
                background-color: #3A3A3A;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
                color: #888888;
            }
        """)
        
    def set_custom_size(self, width, height):
        self.setFixedSize(width, height)
        radius = height // 2
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: #4A4A4A;
                color: white;
                border: none;
                border-radius: {radius}px;
                font-size: {height // 3}px;
            }}
            QPushButton:hover {{
                background-color: #5A5A5A;
            }}
            QPushButton:pressed {{
                background-color: #3A3A3A;
            }}
            QPushButton:disabled {{
                background-color: #CCCCCC;
                color: #888888;
            }}
        """) 
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt
from core.font.font_manager import FontManager

class Button(QPushButton):
    def __init__(self, text="", parent=None, style="blue"):
        super().__init__(text, parent)
        # 创建字体管理器 
        self.font_manager = FontManager()
        self.font_manager.apply_font(self)
        
        # 设置固定大小 
        self.setFixedSize(200, 50)
        
        # 根据不同style设置样式 
        if style == "blue":
            self.setStyleSheet("""
                QPushButton {
                    background-color: #4A90E2;
                    color: white;
                    border-radius: 25px;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background-color: #357ABD;
                }
                QPushButton:pressed {
                    background-color: #2868A9;
                }
            """)
        
        # 设置文本对齐方式 
        self.setFocusPolicy(Qt.NoFocus)  # 去掉焦点框

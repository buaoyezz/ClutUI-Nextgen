from PySide6.QtWidgets import QWidget, QVBoxLayout

class BasePage(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.setStyleSheet("""
            QWidget {
                background: transparent;
            }
            QLabel {
                color: white;
            }
            QPushButton {
                background-color: #4A4A4A;
                border: none;
                border-radius: 5px;
                color: white;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #5A5A5A;
            }
        """)
        self.init_ui()
        
    def init_ui(self):
        pass 
        
    def on_language_changed(self):
        # 基类提供默认实现
        self.refresh_ui_texts()
        
    def refresh_ui_texts(self):
        # 子类需要重写此方法来更新具体的UI文本
        pass 
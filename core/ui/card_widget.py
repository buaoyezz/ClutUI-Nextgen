from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Signal, Qt

class CardWidget(QWidget):
    clicked = Signal(bool)
    doubleClicked = Signal()
    
    def __init__(self, title, value, parent=None):
        super().__init__(parent)
        self.selected = False
        self.setup_ui(title, value)
        
    def setup_ui(self, title, value):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.title_label = QLabel(title)
        self.title_label.setObjectName("cardTitle")
        
        self.value_label = QLabel(value)
        self.value_label.setObjectName("cardValue")
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addStretch()
        
        self.setStyleSheet("""
            QWidget#card {
                background-color: #f0f2f5;
                border: 1px solid #e9ecef;
                border-radius: 12px;
            }
            QWidget#card[selected="true"] {
                background-color: #e3f2fd;
                border: 2px solid #64B5F6;
            }
            QLabel#cardTitle {
                color: #6c757d;
                font-size: 15px;
            }
            QLabel#cardValue {
                color: #212529;
                font-size: 26px;
                font-weight: bold;
            }
        """)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.selected = not self.selected
            self.setProperty("selected", self.selected)
            self.style().unpolish(self)
            self.style().polish(self)
            self.clicked.emit(self.selected)
            
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.doubleClicked.emit() 
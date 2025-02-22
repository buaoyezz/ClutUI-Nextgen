from PySide6.QtWidgets import QComboBox, QStyledItemDelegate, QStyle, QListView
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPainter, QPalette, QColor
from core.font.font_manager import FontManager

class ComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 创建字体管理器喵
        self.font_manager = FontManager()
        self.font_manager.apply_font(self)
        
        # 禁用focus喵
        self.setFocusPolicy(Qt.NoFocus)
        
        # 设置视图模式为列表喵
        list_view = QListView()
        list_view.setFocusPolicy(Qt.NoFocus)
        list_view.setStyleSheet("""
            QListView {
                color: #333333;
            }
        """)
        self.setView(list_view)
        
        # 设置基本样式喵
        self.setStyleSheet("""
            QComboBox {
                border: 1px solid #E0E4E8;
                border-radius: 6px;
                padding: 5px 30px 5px 10px;
                min-width: 6em;
                background: #FFFFFF;
                color: #333333;
            }
            
            QComboBox * {
                color: #333333;
                background-color: #FFFFFF;
            }
            
            QComboBox:hover {
                background-color: #F5F5F5;
                border-color: #E0E4E8;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 20px;
                padding-right: 8px;
                background-color: transparent;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #666666;
                margin-right: 8px;
                background-color: transparent;
            }
            
            QComboBox:on {
                border-bottom-left-radius: 0;
                border-bottom-right-radius: 0;
            }
            
            QComboBox QListView {
                border: 1px solid #E0E4E8;
                border-top: none;
                background-color: #FFFFFF;
                color: #333333;
                outline: none;
                padding: 5px;
            }
            
            QComboBox QListView::item {
                min-height: 25px;
                padding: 5px;
                color: #333333;
                background-color: #FFFFFF;
            }
            
            QComboBox QListView::item:hover {
                background-color: #F5F5F5;
                color: #333333;
            }
            
            QComboBox QListView::item:selected {
                background-color: #F5F5F5;
                color: #333333;
            }
        """)
        
        # 设置代理以自定义下拉项样式喵
        delegate = QStyledItemDelegate()
        self.setItemDelegate(delegate)
        
        # 设置固定高度喵
        self.setFixedHeight(36)
        
    def showPopup(self):
        super().showPopup()
        popup = self.findChild(QListView)
        if popup:
            popup.setSpacing(2)
            popup.setFocusPolicy(Qt.NoFocus)
            # 确保弹出框中的文字颜色
            popup.setStyleSheet("""
                QListView {
                    color: #333333;
                    background-color: #FFFFFF;
                    outline: none;
                }
                QListView::item {
                    color: #333333;
                    background-color: #FFFFFF;
                }
                QListView::item:hover {
                    background-color: #F5F5F5;
                    color: #333333;
                }
                QListView::item:selected {
                    background-color: #F5F5F5;
                    color: #333333;
                }
            """)
            
    def sizeHint(self) -> QSize:
        return QSize(200, 36) 
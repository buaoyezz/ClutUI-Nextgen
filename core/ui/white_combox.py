from PySide6.QtWidgets import QComboBox
from PySide6.QtCore import Qt
from core.i18n import i18n
from core.font.font_pages_manager import FontPagesManager

class WhiteComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.NoFocus)
        
        # 初始化字体管理器
        self.font_pages_manager = FontPagesManager()
        
        self.setup_ui()
        
        # 注册语言变更回调
        i18n.add_language_change_callback(self.update_text)
        
    def setup_ui(self):
        # 应用字体
        self.font_pages_manager.apply_normal_style(self)
        
        self.setStyleSheet("""
            QComboBox {
                background: white;
                border: 2px solid #2196F3;
                border-radius: 8px;
                color: #333333;
                padding: 4px 12px;
                min-height: 32px;
                font-size: 14px;
                letter-spacing: 0.3px;
                outline: none;
            }
            QComboBox:focus {
                outline: none;
                border: 2px solid #2196F3;
            }
            QComboBox::drop-down {
                border: none;
                width: 24px;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
            QComboBox QAbstractItemView {
                background: white;
                border: 2px solid #2196F3;
                border-radius: 8px;
                outline: none;
                selection-background-color: rgba(33, 150, 243, 0.1);
                selection-color: #2196F3;
            }
            QComboBox QAbstractItemView::item {
                min-height: 32px;
                padding: 4px 12px;
                letter-spacing: 0.3px;
                outline: none;
            }
            QComboBox QAbstractItemView::item:hover {
                background: rgba(33, 150, 243, 0.05);
            }
        """)
        
    def update_text(self):
        current_data = self.currentData()
        for i in range(self.count()):
            item_data = self.itemData(i)
            if item_data:
                self.setItemText(i, i18n.get_text(f"lang_{item_data}" if "lang_" not in item_data else item_data))
        
        # 恢复之前选中的项
        if current_data:
            index = self.findData(current_data)
            if index >= 0:
                self.setCurrentIndex(index) 
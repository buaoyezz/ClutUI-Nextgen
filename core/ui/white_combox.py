from PySide6.QtWidgets import QComboBox, QLabel
from PySide6.QtCore import Qt
from core.i18n import i18n
from core.font.font_pages_manager import FontPagesManager

class WhiteComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.NoFocus)
        
        # 初始化字体管理器
        self.font_pages_manager = FontPagesManager()
        
        # 创建下拉箭头图标
        self.arrow_label = QLabel(self)
        self.arrow_label.setText(self.font_pages_manager.get_icon_text('expand_more'))
        self.font_pages_manager.apply_icon_font(self.arrow_label, 20)
        self.arrow_label.setStyleSheet("color: #757575;")
        
        self.setup_ui()
        
        # 连接语言变更信号
        i18n.language_changed.connect(self.update_text)
        
    def update_text(self):
        try:
            current_data = self.currentData()
            self.blockSignals(True)
            
            # 保存所有项的数据
            items_data = []
            for i in range(self.count()):
                item_data = self.itemData(i)
                if item_data:
                    items_data.append(item_data)
            
            # 清空并重新添加项
            self.clear()
            
            # 重新添加项并更新文本
            for item_data in items_data:
                display_text = i18n.get_text(f"lang_{item_data}" if "lang_" not in item_data else item_data)
                if "effect_" in item_data:
                    display_text = i18n.get_text(item_data)
                self.addItem(display_text, item_data)
            
            # 恢复之前选中的项
            if current_data:
                index = self.findData(current_data)
                if index >= 0:
                    self.setCurrentIndex(index)
            
            self.blockSignals(False)
            
            # 强制更新显示
            self.update()
            
        except Exception as e:
            print(f"更新下拉框文本时出错: {str(e)}")

    def setup_ui(self):
        # 应用字体
        self.font_pages_manager.apply_normal_style(self)
        
        self.setStyleSheet("""
            QComboBox {
                background: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                color: #333333;
                padding: 4px 12px;
                min-height: 32px;
                font-size: 14px;
                letter-spacing: 0.3px;
                outline: none;
            }
            QComboBox:hover {
                border: 1px solid #BDBDBD;
            }
            QComboBox:focus {
                border: 1px solid #757575;
                background: #FFFFFF;
            }
            QComboBox::drop-down {
                border: none;
                width: 24px;
                padding-right: 8px;
            }
            QComboBox::down-arrow {
                width: 0px;
            }
            QComboBox QAbstractItemView {
                background: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                outline: none;
                padding: 4px;
                margin: 0px;
            }
            QComboBox QAbstractItemView::item {
                min-height: 32px;
                padding: 4px 12px;
                letter-spacing: 0.3px;
                color: #333333;
                border-left: 3px solid transparent;
            }
            QComboBox QAbstractItemView::item:hover {
                background: #F5F5F5;
            }
            QComboBox QAbstractItemView::item:selected {
                background: #EEEEEE;
                border-left: 3px solid #757575;
            }
        """)
        
        # 调整箭头标签位置
        self.arrow_label.setFixedSize(20, 20)
        self.arrow_label.move(self.width() - 28, (self.height() - 20) // 2)
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # 当控件大小改变时，重新调整箭头位置
        self.arrow_label.move(self.width() - 28, (self.height() - 20) // 2)
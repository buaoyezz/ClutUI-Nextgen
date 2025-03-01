from PySide6.QtWidgets import QComboBox, QLabel
from PySide6.QtCore import Qt, QEvent
from core.i18n import i18n
from core.font.font_pages_manager import FontPagesManager
from core.animations.combobox_animations import ComboBoxAnimations

class WhiteComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)  # 允许获取焦点
        
        # 初始化字体管理器
        self.font_pages_manager = FontPagesManager()
        
        # 创建下拉箭头图标
        self.arrow_label = QLabel(self)
        self.arrow_label.setText(self.font_pages_manager.get_icon_text('expand_more'))
        self.font_pages_manager.apply_icon_font(self.arrow_label, 20)
        self.arrow_label.setStyleSheet("color: #757575;")
        
        # 初始化动画管理器
        self.animations = ComboBoxAnimations(self)
        
        self.setup_ui()
        
        # 连接语言变更信号
        i18n.language_changed.connect(self.update_text)
        
        # 确保事件过滤器正确安装
        self.installEventFilter(self)
        
    def update_text(self):
        try:
            current_data = self.currentData()
            self.blockSignals(True)
            
            # 保存所有项的数据和文本
            items_data = []
            for i in range(self.count()):
                item_data = self.itemData(i)
                if item_data:
                    items_data.append(item_data)
            
            # 清空并重新添加项
            self.clear()
            
            # 重新添加项并更新文本
            for item_data in items_data:
                # 根据数据类型选择不同的翻译方式
                if item_data in ["zh", "en", "zh_hk", "origin"]:
                    # 语言选项
                    display_text = i18n.get_text(f"lang_{item_data}")
                elif item_data.startswith("effect_"):
                    # 效果选项
                    display_text = i18n.get_text(item_data)
                elif item_data in ["debug", "info", "warning", "error", "critical"]:
                    # 日志级别选项
                    display_text = i18n.get_text(f"log_level_{item_data}")
                else:
                    # 其他选项，尝试直接翻译
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
        
        # 初始样式由动画管理器设置
        self.animations.update_style()
        
        # 调整箭头标签位置
        self.arrow_label.setFixedSize(20, 20)
        self.arrow_label.move(self.width() - 28, (self.height() - 20) // 2)
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # 当控件大小改变时，重新调整箭头位置
        self.arrow_label.move(self.width() - 28, (self.height() - 20) // 2)
        
    def mousePressEvent(self, event):
        # 确保鼠标点击事件正常处理
        super().mousePressEvent(event)
        
    def showPopup(self):
        try:
            # 先启动动画，然后调用父类方法显示下拉框
            self.animations.start_dropdown_animation(True)
            # 确保下拉框正常显示
            super().showPopup()
        except Exception as e:
            print(f"显示下拉框时出错: {str(e)}")
            # 确保下拉框显示，即使动画失败
            super().showPopup()
        
    def hidePopup(self):
        try:
            # 先启动动画
            self.animations.start_dropdown_animation(False)
            # 延迟一点时间再隐藏下拉框，确保动画效果可见
            super().hidePopup()
        except Exception as e:
            print(f"隐藏下拉框时出错: {str(e)}")
            # 确保下拉框隐藏，即使动画失败
            super().hidePopup()
        
    def eventFilter(self, obj, event):
        # 处理鼠标点击事件，确保下拉框可以正常展开
        if obj == self and event.type() == QEvent.MouseButtonPress:
            # 确保点击事件能够正常触发下拉框的展开和收起
            return False  # 不拦截事件，让事件继续传递
        
        # 处理焦点事件
        if obj == self and event.type() == QEvent.FocusIn:
            # 当获得焦点时，更新样式
            self.animations.update_style()
            return False
        
        # 处理基本事件
        return super().eventFilter(obj, event)
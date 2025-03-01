from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup, Property, QByteArray, QObject, QTimer
from PySide6.QtGui import QColor, QTransform
from PySide6.QtWidgets import QGraphicsOpacityEffect

class ComboBoxAnimations(QObject):
    
    def __init__(self, combo_box):
        super().__init__(combo_box)
        self.combo_box = combo_box
        self._arrow_rotation = 0
        self._background_color = QColor("#FFFFFF")
        
        # 创建箭头旋转动画
        self.arrow_animation = QPropertyAnimation(self, QByteArray(b"arrow_rotation"))
        self.arrow_animation.setDuration(300)
        self.arrow_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # 创建背景颜色动画
        self.background_animation = QPropertyAnimation(self, QByteArray(b"background_color"))
        self.background_animation.setDuration(250)
        self.background_animation.setEasingCurve(QEasingCurve.OutCubic)
    
    # 箭头旋转属性
    def get_arrow_rotation(self):
        return self._arrow_rotation
    
    def set_arrow_rotation(self, rotation):
        if self._arrow_rotation != rotation:
            self._arrow_rotation = rotation
            self.update_arrow()
    
    arrow_rotation = Property(float, get_arrow_rotation, set_arrow_rotation)
    
    # 背景颜色属性
    def get_background_color(self):
        return self._background_color
    
    def set_background_color(self, color):
        if self._background_color != color:
            self._background_color = color
            self.update_style()
    
    background_color = Property(QColor, get_background_color, set_background_color)
    
    def update_style(self):
        # 计算背景颜色
        background_color = QColor(
            int(self._background_color.red()),
            int(self._background_color.green()),
            int(self._background_color.blue())
        )
        
        # 应用样式
        self.combo_box.setStyleSheet(f"""
            QComboBox {{
                background: rgba({background_color.red()}, {background_color.green()}, {background_color.blue()}, 1.0);
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                color: #333333;
                padding: 4px 12px;
                min-height: 32px;
                font-size: 14px;
                letter-spacing: 0.3px;
                outline: none;
            }}
            QComboBox:hover {{
                border: 1px solid #BDBDBD;
            }}
            QComboBox:focus {{
                border: 1px solid #757575;
                background: #FFFFFF;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
                padding-right: 8px;
                subcontrol-origin: padding;
                subcontrol-position: right center;
            }}
            QComboBox::down-arrow {{
                width: 0px;
                height: 0px;
            }}
            QComboBox QAbstractItemView {{
                background: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                outline: none;
                padding: 4px;
                margin: 0px;
                selection-background-color: transparent;
            }}
            QComboBox QAbstractItemView::item {{
                min-height: 32px;
                padding: 4px 12px;
                letter-spacing: 0.3px;
                color: #333333;
                border-left: 3px solid transparent;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background: #F5F5F5;
            }}
            QComboBox QAbstractItemView::item:selected {{
                background: #EEEEEE;
                border-left: 3px solid #757575;
            }}
        """)
    
    def update_arrow(self):
        if hasattr(self.combo_box, 'arrow_label'):
            try:
                # 使用QTransform代替样式表中的transform
                transform = QTransform()
                transform.rotate(self._arrow_rotation)
                
                # 应用旋转变换 - 只设置颜色，不使用transform属性
                self.combo_box.arrow_label.setStyleSheet(f"""
                    color: #757575;
                """)
                
                # 使用图形变换实现旋转
                if hasattr(self.combo_box.arrow_label, 'setTransform'):
                    self.combo_box.arrow_label.setTransform(transform)
            except Exception as e:
                print(f"更新箭头旋转时出错: {str(e)}")
    
    def start_dropdown_animation(self, expanded):
        try:
            # 箭头旋转动画
            self.arrow_animation.stop()
            self.arrow_animation.setStartValue(self._arrow_rotation)
            self.arrow_animation.setEndValue(180 if expanded else 0)
            self.arrow_animation.start()
            
            # 背景色动画
            self.background_animation.stop()
            self.background_animation.setStartValue(self._background_color)
            target_color = QColor("#F5F5F5") if expanded else QColor("#FFFFFF")
            self.background_animation.setEndValue(target_color)
            self.background_animation.start()
            
            # 为下拉视图添加淡入淡出效果
            if expanded:
                # 延迟一点时间，确保下拉框已经显示
                QTimer.singleShot(10, self._apply_dropdown_fade_in)
        except Exception as e:
            print(f"启动下拉动画时出错: {str(e)}")
    
    def _apply_dropdown_fade_in(self):
        try:
            # 获取下拉视图
            view = self.combo_box.view()
            if view:
                # 确保视图可见
                view.setVisible(True)
                
                # 创建透明度效果
                opacity_effect = QGraphicsOpacityEffect(view)
                opacity_effect.setOpacity(1.0)  # 确保初始状态是完全可见的
                view.setGraphicsEffect(opacity_effect)
                
                # 创建透明度动画
                fade_animation = QPropertyAnimation(opacity_effect, QByteArray(b"opacity"))
                fade_animation.setDuration(200)
                fade_animation.setStartValue(0.7)  # 从较高的透明度开始，避免完全不可见
                fade_animation.setEndValue(1.0)
                fade_animation.setEasingCurve(QEasingCurve.OutCubic)
                fade_animation.start(QPropertyAnimation.DeleteWhenStopped)
        except Exception as e:
            print(f"应用下拉淡入效果时出错: {str(e)}")

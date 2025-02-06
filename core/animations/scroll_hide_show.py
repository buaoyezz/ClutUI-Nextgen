from PySide6.QtCore import QPropertyAnimation, QEasingCurve, Property, QTimer, QObject                          
from PySide6.QtWidgets import QScrollBar

class ScrollBarAnimation(QObject):
    def __init__(self, scrollbar: QScrollBar):
        super().__init__()
        self.scrollbar = scrollbar
        self._opacity = 0.0
        
        # 创建动画
        self.animation = QPropertyAnimation(self, b"opacity")
        self.animation.setDuration(200)  # 200ms 的动画时长
        self.animation.setEasingCurve(QEasingCurve.InOutCubic)
        
        # 创建隐藏计时器
        self.hide_timer = QTimer()
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide_animation)
        
        # 初始样式
        self._update_style()
    
    def _get_opacity(self):
        return self._opacity
    
    def _set_opacity(self, value):
        self._opacity = value
        self._update_style()
    
    # 定义不透明度属性
    opacity = Property(float, _get_opacity, _set_opacity)
    
    def _update_style(self):
        self.scrollbar.setStyleSheet(f"""
            QScrollBar:vertical {{
                border: none;
                background: transparent;
                width: 6px;
                margin: 0px;
            }}
            
            QScrollBar::handle:vertical {{
                background: rgba(0, 0, 0, {self._opacity * 0.2});
                border-radius: 3px;
                min-height: 30px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background: rgba(0, 0, 0, {self._opacity * 0.3});
            }}
            
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)
    
    def show_animation(self):
        self.hide_timer.stop()  # 停止隐藏计时器
        self.animation.stop()
        self.animation.setStartValue(self._opacity)
        self.animation.setEndValue(1.0)
        self.animation.start()
        
    def hide_animation(self):
        self.animation.stop()
        self.animation.setStartValue(self._opacity)
        self.animation.setEndValue(0.0)
        self.animation.start()
    
    def show_temporarily(self):
        self.show_animation()
        self.hide_timer.start(1000)  # 1秒后开始隐藏动画

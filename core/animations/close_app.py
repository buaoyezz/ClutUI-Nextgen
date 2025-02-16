from PySide6.QtCore import QPropertyAnimation, QEasingCurve, Property, QPoint, QParallelAnimationGroup
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QColor

class CloseAppAnimation(QWidget):
    def __init__(self, window):
        super().__init__()
        self.window = window
        self._opacity = 1.0
        self._scale = 1.0
        self._pos = window.pos()
        self._setup_animations()
    
    def _get_opacity(self):
        return self._opacity
    
    def _set_opacity(self, value):
        self._opacity = value
        self.window.setWindowOpacity(value)
    
    def _get_scale(self):
        return self._scale
    
    def _set_scale(self, value):
        self._scale = value
        # 保持窗口居中缩放
        current_geometry = self.window.geometry()
        center = current_geometry.center()
        new_width = int(current_geometry.width() * value)
        new_height = int(current_geometry.height() * value)
        new_x = center.x() - new_width // 2
        new_y = center.y() - new_height // 2
        self.window.setGeometry(new_x, new_y, new_width, new_height)
    
    opacity = Property(float, _get_opacity, _set_opacity)
    scale = Property(float, _get_scale, _set_scale)
    
    def _setup_animations(self):
        # 创建动画组
        self.animation_group = QParallelAnimationGroup()
        
        # 透明度动画
        self.opacity_anim = QPropertyAnimation(self, b"opacity")
        self.opacity_anim.setDuration(300)  # 缩短动画时间到300ms
        self.opacity_anim.setStartValue(1.0)
        self.opacity_anim.setEndValue(0.0)
        self.opacity_anim.setEasingCurve(QEasingCurve.OutQuad)  # 使用更自然的缓动曲线
        
        # 缩放动画
        self.scale_anim = QPropertyAnimation(self, b"scale")
        self.scale_anim.setDuration(300)  # 缩短动画时间到300ms
        self.scale_anim.setStartValue(1.0)
        self.scale_anim.setEndValue(0.95)  # 缩小幅度减小，更加细腻
        self.scale_anim.setEasingCurve(QEasingCurve.OutQuad)  # 使用更自然的缓动曲线
        
        # 添加到动画组
        self.animation_group.addAnimation(self.opacity_anim)
        self.animation_group.addAnimation(self.scale_anim)
        self.animation_group.finished.connect(self._on_animation_finished)
    
    def start(self):
        self.animation_group.start()
    
    def _on_animation_finished(self):
        self.window._cleanup_timer.start(50)  # 缩短清理延迟时间

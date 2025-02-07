from PySide6.QtCore import QPropertyAnimation, QEasingCurve, Property, QPoint, Signal, QParallelAnimationGroup
from PySide6.QtWidgets import QWidget, QApplication
from core.log.log_manager import log

class MessageBoxAnimation(QWidget):
    animation_finished = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._opacity = 0.0
        self._pos = QPoint()
        self._scale = 0.95
        self._is_closing = False
        
        self.show_animation_group = QParallelAnimationGroup(self)
        self.hide_animation_group = QParallelAnimationGroup(self)
        
        # 显示动画
        self.show_opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self.show_opacity_animation.setDuration(200)
        self.show_opacity_animation.setStartValue(0.0)
        self.show_opacity_animation.setEndValue(1.0)
        self.show_opacity_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # 隐藏动画
        self.hide_opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self.hide_opacity_animation.setDuration(150)
        self.hide_opacity_animation.setStartValue(1.0)
        self.hide_opacity_animation.setEndValue(0.0)
        self.hide_opacity_animation.setEasingCurve(QEasingCurve.InCubic)
        
        self.show_animation_group.addAnimation(self.show_opacity_animation)
        self.hide_animation_group.addAnimation(self.hide_opacity_animation)
        
        self.hide_animation_group.finished.connect(self._on_hide_finished)
        
    def show_with_animation(self):
        if self._is_closing:
            return
            
        # 获取屏幕几何信息
        screen = QApplication.primaryScreen().geometry()
        
        # 计算窗口位置
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        
        # 设置窗口位置
        self.move(x, y)
        
        self.setWindowOpacity(0.0)
        super().show()
        self.show_animation_group.start()
        log.debug("开始播放消息框显示动画")
        
    def hide_with_animation(self):
        if self._is_closing:
            return
        self._is_closing = True
        self.hide_animation_group.start()
        log.debug("开始播放消息框隐藏动画")
        
    def _on_hide_finished(self):
        if not self._is_closing:
            return
        super().close()
        self._is_closing = False
        self.animation_finished.emit()
        log.debug("消息框隐藏动画完成")
        
    def closeEvent(self, event):
        if not self._is_closing:
            event.ignore()
            self.hide_with_animation()
        else:
            event.accept()

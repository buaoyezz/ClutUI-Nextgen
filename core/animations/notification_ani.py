from PySide6.QtCore import QPropertyAnimation, QEasingCurve, Property, QPoint, Signal
from PySide6.QtWidgets import QWidget
from core.log.log_manager import log

class NotificationAnimation(QWidget):
    # 添加动画完成信号
    animation_finished = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._opacity = 0.0
        self._pos = QPoint()
        
        # 添加通知队列相关属性
        self.notification_height = 80  # 每个通知的高度
        self.spacing = 10  # 通知之间的间距
        self.current_index = 0  # 当前通知的索引
        
        # 创建位置动画
        self.pos_animation = QPropertyAnimation(self, b"pos")
        self.pos_animation.setDuration(400)
        self.pos_animation.setEasingCurve(QEasingCurve.OutBack)
        
        # 创建透明度动画
        self.opacity_animation = QPropertyAnimation(self, b"opacity") 
        self.opacity_animation.setDuration(350)
        self.opacity_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # 连接动画完成信号
        self.pos_animation.finished.connect(self._on_animation_finished)
        self.opacity_animation.finished.connect(self._on_animation_finished)
        
    def get_opacity(self):
        return self._opacity
        
    def set_opacity(self, opacity):
        self._opacity = opacity
        self.setWindowOpacity(opacity)
        
    opacity = Property(float, get_opacity, set_opacity)
    
    def show_animation(self, start_pos, end_pos):
        # 根据当前索引计算垂直偏移
        vertical_offset = self.current_index * (self.notification_height + self.spacing)
        adjusted_start_pos = QPoint(start_pos.x(), start_pos.y() + vertical_offset)
        adjusted_end_pos = QPoint(end_pos.x(), end_pos.y() + vertical_offset)
        
        # 设置初始位置和透明度
        self.move(adjusted_start_pos)
        self.setWindowOpacity(0)
        
        # 配置位置动画
        self.pos_animation.setStartValue(adjusted_start_pos)
        self.pos_animation.setEndValue(adjusted_end_pos)
        
        # 配置透明度动画
        self.opacity_animation.setStartValue(0.0)
        self.opacity_animation.setEndValue(1.0)
        
        # 开始动画
        self.show()
        self.pos_animation.start()
        self.opacity_animation.start()
        log.debug(f"通知显示动画开始 - 索引: {self.current_index}")
        
    def hide_animation(self, start_pos, end_pos):
        # 根据当前索引计算垂直偏移
        vertical_offset = self.current_index * (self.notification_height + self.spacing)
        adjusted_start_pos = QPoint(start_pos.x(), start_pos.y() + vertical_offset)
        adjusted_end_pos = QPoint(end_pos.x(), end_pos.y() + vertical_offset)
        
        # 配置位置动画
        self.pos_animation.setStartValue(adjusted_start_pos)
        self.pos_animation.setEndValue(adjusted_end_pos)
        
        # 配置透明度动画
        self.opacity_animation.setStartValue(1.0)
        self.opacity_animation.setEndValue(0.0)
        
        # 连接动画完成信号
        self.opacity_animation.finished.connect(self.cleanup)
        
        # 开始动画
        self.pos_animation.start()
        self.opacity_animation.start()
        log.debug(f"通知隐藏动画开始 - 索引: {self.current_index}")
        
    def cleanup(self):
        self.hide()
        self.current_index = max(0, self.current_index - 1)
        # 这里可以发送信号通知管理器更新其他通知的位置 

    def _on_animation_finished(self):
        # 当两个动画都完成时发出信号
        if (self.pos_animation.state() == QPropertyAnimation.Stopped and 
            self.opacity_animation.state() == QPropertyAnimation.Stopped):
            self.animation_finished.emit() 
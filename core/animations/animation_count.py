from PySide6.QtCore import QTimer, QObject, Signal, Property
from core.log.log_manager import log
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import QPropertyAnimation

class AnimationCounter(QObject):
    # 定义信号用于更新UI
    value_changed = Signal(float)
    animation_finished = Signal()
    
    def __init__(self, label, start_value, end_value, easing_curve=None, duration=500):
        super().__init__()
        self.label = label
        self.start_value = float(start_value)
        self.end_value = float(end_value)
        self.current_value = self.start_value
        self.animation = QPropertyAnimation(self, b"value", self)
        self.animation.setDuration(duration)
        self.animation.setStartValue(self.start_value)
        self.animation.setEndValue(self.end_value)
        
        if easing_curve:
            self.animation.setEasingCurve(easing_curve)
            
        self.value_changed.connect(self._update_label)
        
    def _update_label(self, value):
        # 根据大小选择合适的单位
        if value >= 1000:
            text = f"{value/1024:.1f} GB"
        else:
            text = f"{value:.1f} MB"
        self.label.setText(text)
        
    def get_value(self):
        return self.current_value
        
    def set_value(self, value):
        self.current_value = value
        self.value_changed.emit(value)
        
    value = Property(float, get_value, set_value)
    
    def start_animation(self):
        self.animation.start()
        
    def stop_animation(self):
        self.animation.stop()
        self.current_value = self.end_value
        self.value_changed.emit(self.end_value)
        self.animation_finished.emit()
        log.debug("数字动画结束")

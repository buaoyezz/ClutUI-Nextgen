from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCore import Qt, QPropertyAnimation, Property
from PySide6.QtGui import QPainter, QColor, QPainterPath

class ProgressBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(6)
        self._progress = 0
        self._animation = QPropertyAnimation(self, b"value", self)
        self._animation.setDuration(200)  # 减少动画时间使其更流畅
        
        self.setStyleSheet("""
            QWidget {
                background: #F0F0F0;
                border-radius: 3px;
            }
        """)

    def _get_value(self):
        return self._progress
        
    def _set_value(self, value):
        self._progress = max(0, min(value, 100))
        self.update()
        
    value = Property(float, _get_value, _set_value)
        
    def setProgress(self, value, animated=True):
        if self._animation.state() == QPropertyAnimation.Running:
            self._animation.stop()
            
        target_value = max(0, min(value, 100))
        if animated and abs(target_value - self._progress) > 0.1:
            self._animation.setStartValue(self._progress)
            self._animation.setEndValue(target_value)
            self._animation.start()
        else:
            self._set_value(target_value)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制背景
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 3, 3)
        painter.fillPath(path, QColor("#F0F0F0"))

        # 绘制进度（使用淡紫色）
        if self._progress > 0:
            progress_width = int(self.width() * self._progress / 100)
            progress_path = QPainterPath()
            progress_path.addRoundedRect(0, 0, progress_width, self.height(), 3, 3)
            painter.fillPath(progress_path, QColor("#B39DDB"))  # Material Design 淡紫色

        painter.end() 
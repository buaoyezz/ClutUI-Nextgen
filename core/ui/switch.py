from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QPropertyAnimation, QRectF, Property, Signal
from PySide6.QtGui import QPainter, QColor, QPainterPath

class QSwitch(QWidget):
    # 开关状态改变信号
    stateChanged = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 设置固定大小
        self.setFixedSize(50, 26)
        
        # 初始化属性
        self._checked = False
        self._margin = 3
        self._thumb_position = self._margin
        self._animation = QPropertyAnimation(self, b"thumbPosition", self)
        self._animation.setDuration(200)
        
        # 设置颜色
        self._track_color_on = QColor("#64B5F6")  # 蓝色轨道
        self._track_color_off = QColor("#CCCCCC")  # 灰色轨道
        self._thumb_color = QColor("#FFFFFF")  # 白色滑块
        
    def sizeHint(self):
        return self.minimumSizeHint()

    def minimumSizeHint(self):
        return self.size()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        # 绘制轨道
        track_opacity = 0.6 if not self.isEnabled() else 1.0
        track_color = self._track_color_on if self._checked else self._track_color_off
        track_color.setAlphaF(track_opacity)
        
        p.setBrush(track_color)
        p.setPen(Qt.NoPen)
        
        track_path = QPainterPath()
        track_rect = QRectF(0, 0, self.width(), self.height())
        track_path.addRoundedRect(track_rect, self.height() / 2, self.height() / 2)
        p.drawPath(track_path)
        
        # 绘制滑块
        p.setBrush(self._thumb_color)
        thumb_rect = QRectF(
            self._thumb_position,
            self._margin,
            self.height() - 2 * self._margin,
            self.height() - 2 * self._margin
        )
        p.drawEllipse(thumb_rect)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setChecked(not self._checked)
            event.accept()

    def enterEvent(self, event):
        self.setCursor(Qt.PointingHandCursor)
        super().enterEvent(event)

    @Property(float)
    def thumbPosition(self):
        return self._thumb_position

    @thumbPosition.setter
    def thumbPosition(self, pos):
        self._thumb_position = pos
        self.update()

    def setChecked(self, checked):
        if self._checked != checked:
            self._checked = checked
            self.stateChanged.emit(checked)
            
            # 设置动画
            self._animation.setStartValue(self._thumb_position)
            if checked:
                self._animation.setEndValue(self.width() - self.height() + self._margin)
            else:
                self._animation.setEndValue(self._margin)
            self._animation.start()

    def isChecked(self):
        return self._checked 
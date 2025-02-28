from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QPropertyAnimation, QRectF, Property, Signal
from PySide6.QtGui import QPainter, QColor, QPainterPath
from core.i18n import i18n

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
        
        # 设置颜色
        self._track_color_on = QColor("#2196F3")  # 更改为主题蓝色
        self._track_color_off = QColor("#CCCCCC")
        self._thumb_color = QColor("#FFFFFF")
        
        # 创建动画
        self._animation = QPropertyAnimation(self, b"thumb_position")
        self._animation.setDuration(200)
        
        # 添加 NoFocus 属性
        self.setFocusPolicy(Qt.NoFocus)
        
        # 设置工具提示
        self.update_tooltip()
        
        # 连接语言变更信号
        i18n.language_changed.connect(self.update_text)
        
    def update_text(self):
        self.update_tooltip()
        
    def update_tooltip(self):
        self.setToolTip(i18n.get_text("enabled" if self._checked else "disabled"))

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

    def get_thumb_position(self):
        return self._thumb_position

    def set_thumb_position(self, pos):
        if self._thumb_position != pos:
            self._thumb_position = pos
            self.update()

    thumb_position = Property(float, get_thumb_position, set_thumb_position)

    def setChecked(self, checked):
        if self._checked != checked:
            self._checked = checked
            self.stateChanged.emit(checked)
            
            self._animation.setStartValue(self._thumb_position)
            if checked:
                self._animation.setEndValue(self.width() - self.height() + self._margin)
            else:
                self._animation.setEndValue(self._margin)
            self._animation.start()

    def isChecked(self):
        return self._checked 
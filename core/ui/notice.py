from PySide6.QtWidgets import QFrame, QLabel, QHBoxLayout, QGraphicsOpacityEffect, QGraphicsDropShadowEffect, QWidget
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, Property, QEasingCurve, QParallelAnimationGroup
from PySide6.QtGui import QColor
from core.font.font_manager import FontManager
from core.font.font_pages_manager import FontPagesManager

class Notice(QFrame):
    def __init__(self, message="", icon="info", parent=None):
        super().__init__(parent)
        self.message = message
        self.icon_name = icon
        self.font_manager = FontManager()
        self.font_pages_manager = FontPagesManager()
        self.scroll_pos = 0  # 初始化滚动位置
        self.is_first_scroll = True  # 标记是否是第一次滚动
        self.opacity = 0.0  # 初始透明度
        self.setup_ui()
        
    def setup_ui(self):
        # 主布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        
        # 图标
        self.icon_label = QLabel(self.font_manager.get_icon_text(self.icon_name))
        self.font_manager.apply_icon_font(self.icon_label, size=20)
        self.icon_label.setStyleSheet("""
            color: #F9A825;
            background: transparent;
        """)
        self.icon_label.setFixedWidth(20)
        layout.addWidget(self.icon_label)
        
        # 消息文本容器
        self.text_container = QWidget()
        self.text_container.setFixedHeight(24)
        text_container_layout = QHBoxLayout(self.text_container)
        text_container_layout.setContentsMargins(0, 0, 0, 0)
        text_container_layout.setSpacing(0)
        
        # 消息文本
        self.message_label = QLabel(self.message)
        self.message_label.setWordWrap(False)
        self.font_pages_manager.apply_normal_style(self.message_label)
        self.message_label.setStyleSheet("""
            color: #333333;
            background: transparent;
            letter-spacing: 0.5px;
            padding-left: 4px;
        """)
        text_container_layout.addWidget(self.message_label)
        
        # 添加文本容器到主布局
        layout.addWidget(self.text_container, 1)
        
        # 设置框架样式 - 移除不支持的transition属性
        self.setStyleSheet("""
            Notice {
                background: rgba(249, 168, 37, 0.05);
                border-radius: 8px;
            }
            Notice:hover {
                background: rgba(249, 168, 37, 0.1);
            }
        """)
        
        # 添加背景色动画
        self.background_animation = QPropertyAnimation(self, b"background_color", self)
        self.background_animation.setDuration(300)
        
        # 设置鼠标进入和离开事件
        self.enterEvent = self._handle_enter_event
        self.leaveEvent = self._handle_leave_event
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
        # 设置固定高度和最大宽度
        self.setFixedHeight(48)
        self.setMaximumWidth(850)
        
        # 初始化透明度效果
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.opacity_effect.setOpacity(0.0)
        self.setGraphicsEffect(self.opacity_effect)
        
        # 添加点击事件
        self.setCursor(Qt.PointingHandCursor)  # 设置鼠标指针样式
        self.mousePressEvent = self._handle_click
        
        # 初始化动画组
        self.animation_group = QParallelAnimationGroup(self)
        
        # 滚动动画
        self.scroll_animation = QPropertyAnimation(self, b"scrollPosition")
        self.scroll_animation.setDuration(15000)
        self.scroll_animation.setEasingCurve(QEasingCurve.Linear)
        self.scroll_animation.finished.connect(self._on_scroll_finished)
        
        # 复原动画
        self.restore_animation = QPropertyAnimation(self, b"scrollPosition")
        self.restore_animation.setDuration(800)
        self.restore_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # 透明度动画
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(400)  # 增加淡入淡出时间
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)  # 使用更平滑的缓动曲线
        
        self.animation_group.addAnimation(self.scroll_animation)
        self.animation_group.addAnimation(self.fade_animation)
        
        # 检查是否需要滚动
        QTimer.singleShot(100, self.start_scroll_if_needed)
        
    def show_message(self, duration=3000):
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.show()
        self.fade_animation.start()
        
    def hide_message(self):
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.finished.connect(self.hide)
        self.fade_animation.start()
        
    def get_scroll_position(self):
        return self.scroll_pos
        
    def set_scroll_position(self, pos):
        self.scroll_pos = pos
        self.update_text_position()
        
    scrollPosition = Property(float, get_scroll_position, set_scroll_position)
    
    def update_text_position(self):
        self.message_label.setStyleSheet(f"""
            color: #333333;
            background: transparent;
            letter-spacing: 0.5px;
            padding-left: 4px;
            margin-left: {int(self.scroll_pos)}px;
        """)
        
    def start_scroll_if_needed(self):
        if not self.message_label.isVisible():
            return
            
        text_width = self.message_label.sizeHint().width()
        container_width = self.width() - self.icon_label.width() - 40
        
        if text_width > container_width:
            # 重置位置和动画
            self.scroll_pos = 0
            self.update_text_position()
            self.animation_group.stop()
            
            # 增加初始延迟
            delay = 2500 if self.is_first_scroll else 1500
            self.is_first_scroll = False
            
            # 使用lambda来确保动画开始时重新检查可见性
            QTimer.singleShot(delay, lambda: self._start_scroll_animation(text_width, container_width))
        else:
            self.animation_group.stop()
            self.scroll_pos = 0
            self.update_text_position()
            
    def _start_scroll_animation(self, text_width, container_width):
        if not self.isVisible():
            return
            
        # 只有当文本宽度大于容器宽度时才滚动
        if text_width <= container_width:
            return
            
        # 计算滚动距离
        scroll_distance = -(text_width - container_width + 100)
        
        # 设置滚动动画
        self.scroll_animation.stop()
        
        # 如果不是第一次滚动，先平滑回到起始位置
        if not self.is_first_scroll:
            reset_animation = QPropertyAnimation(self, b"scrollPosition", self)
            reset_animation.setDuration(400)
            reset_animation.setEasingCurve(QEasingCurve.OutCubic)
            reset_animation.setStartValue(self.scroll_pos)
            reset_animation.setEndValue(0)
            reset_animation.finished.connect(lambda: self._start_main_scroll(scroll_distance))
            reset_animation.start()
        else:
            self._start_main_scroll(scroll_distance)
            
    def _start_main_scroll(self, scroll_distance):
        self.scroll_animation.setStartValue(0)
        self.scroll_animation.setEndValue(scroll_distance)
        self.animation_group.start()
        
    def _on_scroll_finished(self):
        if not self.isVisible():
            return
            
        # 执行复原动画
        self._restore_position()
        
        # 复原后等待一段时间再重新开始滚动
        QTimer.singleShot(3000, lambda: self._restart_scroll())
        
    def _restart_scroll(self):
        if not self.isVisible():
            return
            
        text_width = self.message_label.sizeHint().width()
        container_width = self.width() - self.icon_label.width() - 40
        
        # 确保文本宽度大于容器宽度
        if text_width > container_width:
            self.is_first_scroll = False  # 标记非首次滚动
            self._start_scroll_animation(text_width, container_width)
        else:
            # 如果文本宽度小于容器宽度，重置位置
            self.scroll_pos = 0
            self.update_text_position()
        
    def pause_scroll(self):
        if self.animation_group.state() == QParallelAnimationGroup.Running:
            self.animation_group.pause()
        if self.restore_animation.state() == QPropertyAnimation.Running:
            self.restore_animation.pause()
            
    def resume_scroll(self):
        if self.animation_group.state() == QParallelAnimationGroup.Paused:
            self.animation_group.resume()
        if self.restore_animation.state() == QPropertyAnimation.Paused:
            self.restore_animation.resume()
            
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.animation_group.stop()
        self.start_scroll_if_needed()
        
    def set_message(self, message):
        if self.message == message:
            return
            
        self.message = message
        self.message_label.setText(message)
        self.is_first_scroll = True
        self.animation_group.stop()
        self.scroll_pos = 0
        self.update_text_position()
        
        # 添加淡入淡出效果
        fade_out = QPropertyAnimation(self.opacity_effect, b"opacity", self)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.setDuration(150)
        
        fade_in = QPropertyAnimation(self.opacity_effect, b"opacity", self)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.setDuration(150)
        
        # 连接动画
        fade_out.finished.connect(lambda: QTimer.singleShot(100, self.start_scroll_if_needed))
        fade_out.finished.connect(fade_in.start)
        
        fade_out.start()
        
    def set_icon(self, icon_name):
        if self.icon_name == icon_name:
            return
            
        self.icon_name = icon_name
        
        # 添加图标切换动画
        fade_out = QPropertyAnimation(self.icon_label, b"opacity", self)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.setDuration(150)
        
        fade_in = QPropertyAnimation(self.icon_label, b"opacity", self)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.setDuration(150)
        
        def update_icon():
            self.icon_label.setText(self.font_manager.get_icon_text(icon_name))
            
        fade_out.finished.connect(update_icon)
        fade_out.finished.connect(fade_in.start)
        
        fade_out.start()

    def _handle_enter_event(self, event):
        self.background_animation.setStartValue(QColor(249, 168, 37, 13))  # 0.05 * 255 ≈ 13
        self.background_animation.setEndValue(QColor(249, 168, 37, 26))    # 0.1 * 255 ≈ 26
        self.background_animation.start()
        
    def _handle_leave_event(self, event):
        self.background_animation.setStartValue(QColor(249, 168, 37, 26))
        self.background_animation.setEndValue(QColor(249, 168, 37, 13))
        self.background_animation.start()
        
    def get_background_color(self):
        return self.palette().color(self.backgroundRole())
        
    def set_background_color(self, color):
        palette = self.palette()
        palette.setColor(self.backgroundRole(), color)
        self.setPalette(palette)
        
    background_color = Property(QColor, get_background_color, set_background_color)

    def _handle_click(self, event):
        text_width = self.message_label.sizeHint().width()
        container_width = self.width() - self.icon_label.width() - 40
        
        # 如果动画正在运行，先停止
        if self.animation_group.state() == QParallelAnimationGroup.Running:
            self.animation_group.stop()
            # 平滑复原到初始位置
            self._restore_position()
        else:
            # 开始新的滚动
            if text_width > container_width:
                self.is_first_scroll = True
                self._start_scroll_animation(text_width, container_width)

    def _restore_position(self):
        self.restore_animation.stop()
        self.restore_animation.setStartValue(self.scroll_pos)
        self.restore_animation.setEndValue(0)
        
        # 添加弹性效果
        self.restore_animation.setEasingCurve(QEasingCurve.OutBack)
        self.restore_animation.start()

    def update_message(self, new_message):
        if self.message == new_message:
            return
            
        self.message = new_message
        self.message_label.setText(new_message)
        self.is_first_scroll = True
        self.animation_group.stop()
        self.scroll_pos = 0
        self.update_text_position()
        
        # 添加淡入淡出效果
        fade_out = QPropertyAnimation(self.opacity_effect, b"opacity", self)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.setDuration(150)
        
        fade_in = QPropertyAnimation(self.opacity_effect, b"opacity", self)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.setDuration(150)
        
        # 连接动画
        fade_out.finished.connect(lambda: QTimer.singleShot(100, self.start_scroll_if_needed))
        fade_out.finished.connect(fade_in.start)
        
        fade_out.start()

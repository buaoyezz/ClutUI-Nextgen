from PySide6.QtWidgets import QFrame, QLabel, QHBoxLayout, QGraphicsOpacityEffect, QGraphicsDropShadowEffect, QWidget
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, Property, QEasingCurve
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
        text_container = QWidget()
        text_container.setFixedHeight(24)
        text_container_layout = QHBoxLayout(text_container)
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
        layout.addWidget(text_container, 1)
        
        # 设置框架样式
        self.setStyleSheet("""
            Notice {
                background: rgba(249, 168, 37, 0.05);
                border-radius: 8px;
            }
            Notice:hover {
                background: rgba(249, 168, 37, 0.1);
            }
        """)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
        # 设置固定高度和最大宽度
        self.setFixedHeight(48)
        self.setMaximumWidth(850)
        
        # 初始化滚动动画
        self.scroll_animation = QPropertyAnimation(self, b"scrollPosition")
        self.scroll_animation.setDuration(8000)  # 8秒完成滚动
        self.scroll_animation.setEasingCurve(QEasingCurve.Linear)
        self.scroll_animation.finished.connect(self._on_scroll_finished)
        
        # 当鼠标悬停时暂停滚动
        text_container.enterEvent = lambda e: self.pause_scroll()
        text_container.leaveEvent = lambda e: self.resume_scroll()
        
        # 检查是否需要滚动
        QTimer.singleShot(100, self.start_scroll_if_needed)
        
    def show_message(self, duration=3000):
        """显示通知"""
        self.show()
        
    def get_scroll_position(self):
        return self.scroll_pos
        
    def set_scroll_position(self, pos):
        self.scroll_pos = pos
        self.update_text_position()
        
    scrollPosition = Property(float, get_scroll_position, set_scroll_position)
    
    def update_text_position(self):
        """更新文本位置"""
        self.message_label.setStyleSheet(f"""
            color: #333333;
            background: transparent;
            letter-spacing: 0.5px;
            padding-left: 4px;
            margin-left: {int(self.scroll_pos)}px;
        """)
        
    def start_scroll_if_needed(self):
        """检查是否需要开始滚动"""
        if not self.message_label.isVisible():
            return
            
        text_width = self.message_label.sizeHint().width()
        container_width = self.width() - self.icon_label.width() - 40
        
        if text_width > container_width:
            # 重置位置
            self.scroll_pos = 0
            self.update_text_position()
            
            # 如果是第一次滚动或刚刚重置，等待2秒
            delay = 2000 if self.is_first_scroll else 0
            self.is_first_scroll = False
            
            QTimer.singleShot(delay, lambda: self._start_scroll_animation(text_width, container_width))
        else:
            self.scroll_animation.stop()
            self.scroll_pos = 0
            self.update_text_position()
            
    def _start_scroll_animation(self, text_width, container_width):
        """开始滚动动画"""
        if not self.isVisible():
            return
            
        # 设置滚动动画
        self.scroll_animation.stop()
        self.scroll_animation.setStartValue(0)
        self.scroll_animation.setEndValue(-(text_width - container_width + 40))
        self.scroll_animation.start()
        
    def _on_scroll_finished(self):
        """滚动结束的处理"""
        if not self.isVisible():
            return
            
        # 在末尾停留2秒后重新开始
        QTimer.singleShot(2000, self.start_scroll_if_needed)
        
    def pause_scroll(self):
        """暂停滚动"""
        if self.scroll_animation.state() == QPropertyAnimation.Running:
            self.scroll_animation.pause()
            
    def resume_scroll(self):
        """恢复滚动"""
        if self.scroll_animation.state() == QPropertyAnimation.Paused:
            self.scroll_animation.resume()
            
    def resizeEvent(self, event):
        """窗口大小改变时检查是否需要滚动"""
        super().resizeEvent(event)
        self.is_first_scroll = True  # 重置大小时重新开始
        self.scroll_animation.stop()
        self.start_scroll_if_needed()
        
    def set_message(self, message):
        """更新通知消息"""
        self.message = message
        self.message_label.setText(message)
        self.is_first_scroll = True  # 更新消息时重新开始
        self.scroll_animation.stop()
        self.scroll_pos = 0
        self.start_scroll_if_needed()
        
    def set_icon(self, icon_name):
        """更新图标"""
        self.icon_name = icon_name
        self.icon_label.setText(self.font_manager.get_icon_text(icon_name))

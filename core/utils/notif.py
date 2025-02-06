"""
HOW TO USE

# 完整通知
notification = Notification(
    title="自定义标题",
    text="这是通知内容",
    type=NotificationType.TIPS,
    duration=3000
)
notification.show_notification()

# 快速通知
show_info("这是一条提示信息")
show_warning("这是一条警告信息")
show_error("这是一条错误信息")

"""
from PySide6.QtWidgets import (
    QWidget, 
    QLabel, 
    QVBoxLayout, 
    QHBoxLayout, 
    QApplication, 
    QGraphicsDropShadowEffect
)
from PySide6.QtCore import (
    Qt, 
    QTimer, 
    QPoint, 
    QPropertyAnimation,
    Property,
    QEasingCurve
)
from PySide6.QtGui import QColor
from core.animations.notification_ani import NotificationAnimation
from core.font.font_pages_manager import FontPagesManager
from core.font.font_manager import FontManager
from core.log.log_manager import log
from enum import Enum, auto

class NotificationType:
    INFO = "Tips"
    TIPS = "提示"
    WARNING = "警告"
    WARN = "Warn"
    ERROR = "错误"
    FAILED = "失败"

# 通知样式映射
NOTIFICATION_STYLES = {
    NotificationType.INFO: ("#1A73E8", "rgba(26, 115, 232, 0.05)", "rgba(26, 115, 232, 0.1)"),
    NotificationType.TIPS: ("#1A73E8", "rgba(26, 115, 232, 0.05)", "rgba(26, 115, 232, 0.1)"),
    NotificationType.WARNING: ("#F9A825", "rgba(249, 168, 37, 0.05)", "rgba(249, 168, 37, 0.1)"),
    NotificationType.WARN: ("#F9A825", "rgba(249, 168, 37, 0.05)", "rgba(249, 168, 37, 0.1)"),
    NotificationType.ERROR: ("#D93025", "rgba(217, 48, 37, 0.05)", "rgba(217, 48, 37, 0.1)"),
    NotificationType.FAILED: ("#D93025", "rgba(217, 48, 37, 0.05)", "rgba(217, 48, 37, 0.1)")
}

# 图标映射
NOTIFICATION_ICONS = {
    NotificationType.INFO: 'info',
    NotificationType.TIPS: 'info',
    NotificationType.WARNING: 'warning',
    NotificationType.WARN: 'warning',
    NotificationType.ERROR: 'error',
    NotificationType.FAILED: 'error'
}

class Notification(NotificationAnimation):
    # 类级别的通知队列管理
    active_notifications = []
    
    def __init__(self, text="", title=None, type=NotificationType.TIPS, duration=8000, parent=None):
        super().__init__(parent)
        
        # 设置窗口属性
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.Tool | 
            Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
        # 动画时长设置
        self.show_animation_duration = 1000
        self.hide_animation_duration = 800
        self.adjust_animation_duration = 600
        
        # 保存参数，duration 直接使用传入的值
        self.text = text
        self.title = title
        self.notification_type = type
        self.duration = duration  # 移除 max() 限制，直接使用传入的值
        
        # 保存类型和获取对应的图标
        self.icon_name = NOTIFICATION_ICONS.get(type, 'info')
        
        # 初始化字体管理器
        self.font_manager = FontManager()
        self.font_pages_manager = FontPagesManager()
        
        # 初始化UI
        self._init_ui()
        
        # 创建定时器
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.on_timeout)
        
        # 标记动画状态
        self._show_animation_finished = False
        
    def _init_ui(self):
        # 获取通知样式
        text_color, bg_color, hover_color = NOTIFICATION_STYLES.get(
            self.notification_type, 
            NOTIFICATION_STYLES[NotificationType.TIPS]
        )
        
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)
        
        # 创建标题和内容标签
        title = self.title if self.title else self.notification_type
        
        # 创建水平布局用于图标和标题
        title_layout = QHBoxLayout()
        title_layout.setSpacing(8)
        
        # 添加图标标签
        self.icon_label = QLabel()
        self.font_manager.apply_icon_font(self.icon_label, 20)
        
        # 设置图标
        self.icon_label.setText(self.font_manager.get_icon_text(self.icon_name))
        self.icon_label.setStyleSheet(f"color: {text_color};")
        
        self.title_label = QLabel(title)
        self.text_label = QLabel(self.text)
        self.text_label.setWordWrap(True)
        
        # 使用字体管理器，调整字体粗细
        self.font_pages_manager.apply_subtitle_style(self.title_label)
        self.title_label.setStyleSheet(f"color: {text_color}; font-weight: 500;")
        
        self.font_pages_manager.apply_normal_style(self.text_label)
        self.text_label.setStyleSheet("color: #FFFFFF;")
        
        # 添加图标和标题到水平布局
        title_layout.addWidget(self.icon_label)
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()

        # 创建水平布局用于图标和内容
        content_layout = QHBoxLayout()
        content_layout.setSpacing(10)
        content_layout.setContentsMargins(12, 10, 12, 10)

        # 创建左侧颜色条
        color_bar = QWidget()
        color_bar.setFixedWidth(4)
        color_bar.setStyleSheet(f"""
            background-color: {text_color};
            border-radius: 2px;
        """)
        
        # 创建内容区域
        content_widget = QWidget()
        content_widget_layout = QVBoxLayout(content_widget)
        content_widget_layout.setContentsMargins(0, 0, 0, 0)
        content_widget_layout.setSpacing(4)
        content_widget_layout.addLayout(title_layout) 
        content_widget_layout.addWidget(self.text_label)
        
        # 添加到水平布局
        content_layout.addWidget(color_bar)
        content_layout.addWidget(content_widget, 1)
        
        # 将水平布局添加到主布局
        layout.addLayout(content_layout)
        
        # 设置样式
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                border-radius: 12px;
                border: 1px solid rgba(0, 0, 0, 0.08);
            }}
            QLabel {{
                background: transparent;
                border: none;
            }}
        """)
        
        # 设置标题标签的可访问名称以应用特定样式
        self.title_label.setAccessibleName("title")
        
        # 设置固定宽度和最大高度
        self.setFixedWidth(360)
        self.setMaximumHeight(150)
        
        # 设置窗口透明度
        self.setWindowOpacity(1.0)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
    def show_notification(self):
        # 调整大小以适应内容
        self.adjustSize()
        
        # 获取屏幕尺寸
        screen = QApplication.primaryScreen().availableGeometry()
        
        # 计算基础位置
        margin = 20
        start_x = screen.right() - self.width() - margin
        
        # 修改这里：只考虑当前活动的通知数量
        total_height = self.height() + margin
        active_count = len([n for n in Notification.active_notifications if n.isVisible()])
        offset = active_count * total_height
        
        start_y = screen.top() + offset + total_height
        end_y = screen.top() + offset + margin
        
        # 将自己添加到活动通知列表
        Notification.active_notifications.append(self)
        
        # 开始显示动画
        self.pos_animation.setDuration(self.show_animation_duration)
        self.opacity_animation.setDuration(self.show_animation_duration)
        
        self.show_animation(
            QPoint(start_x, start_y),
            QPoint(start_x, end_y)
        )
        
        # 等待显示动画完成后再开始计时
        def start_timer():
            self._show_animation_finished = True
            log.debug(f"通知显示动画完成，开始计时 {self.duration}ms")
            self.timer.start(self.duration)
            
        QTimer.singleShot(self.show_animation_duration + 100, start_timer)
        log.debug(f"显示通知: {self.text_label.text()}, 持续时间: {self.duration}ms")
        
    def on_timeout(self):
        if not self._show_animation_finished:
            log.debug("显示动画未完成，延迟隐藏")
            QTimer.singleShot(500, self.on_timeout)
            return
            
        # 计算隐藏动画的位置
        screen = QApplication.primaryScreen().availableGeometry()
        margin = 8  # 这里也要改为8，保持一致
        start_x = screen.right() - self.width() - margin
        current_y = self.y()
        end_y = current_y - self.height() - margin  # 向上滑出
        
        log.debug(f"通知开始隐藏，显示时长: {self.duration}ms")
        # 开始隐藏动画
        self.hide_animation(
            QPoint(start_x, current_y),
            QPoint(start_x, end_y)
        )
        
    def _on_hide_finished(self):
        # 从活动通知列表中移除自己
        if self in Notification.active_notifications:
            index = Notification.active_notifications.index(self)
            Notification.active_notifications.pop(index)
            
            # 重新调整其他通知的位置，从顶部开始重新排列
            self._adjust_other_notifications(0)  # 修改这里，总是从0开始重新排列
            
        # 最后删除自己
        self.deleteLater()
        
    def _adjust_other_notifications(self, start_index):
        screen = QApplication.primaryScreen().availableGeometry()
        margin = 20
        total_height = self.height() + margin
        
        # 修改这里：只调整可见的通知
        visible_notifications = [n for n in Notification.active_notifications if n.isVisible()]
        
        # 从顶部开始重新排列所有可见通知
        for i, notif in enumerate(visible_notifications):
            target_y = screen.top() + (i * total_height) + margin
            current_x = notif.x()
            
            # 创建位置动画
            anim = QPropertyAnimation(notif, b"pos", notif)
            anim.setDuration(self.adjust_animation_duration)
            anim.setEasingCurve(QEasingCurve.OutCubic)
            anim.setStartValue(notif.pos())
            anim.setEndValue(QPoint(current_x, target_y))
            anim.start()

# 快速通知方法默认时间调整为8秒
def show_info(text, duration=8000):
    notif = Notification(text=text, type=NotificationType.INFO, duration=duration)
    notif.show_notification()
    
def show_warning(text, duration=8000):
    notif = Notification(text=text, type=NotificationType.WARNING, duration=duration)
    notif.show_notification()
    
def show_error(text, duration=8000):
    notif = Notification(text=text, type=NotificationType.ERROR, duration=duration)
    notif.show_notification()

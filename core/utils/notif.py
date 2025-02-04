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
        self.show_animation_duration = 1000  # 显示动画时长增加到1秒
        self.hide_animation_duration = 800   # 隐藏动画时长增加到0.8秒
        self.adjust_animation_duration = 600 # 位置调整动画时长增加到0.6秒
        
        # 保存参数
        self.text = text
        self.title = title
        self.type = type
        self.duration = max(duration, 5000)  # 确保最短显示5秒
        
        # 初始化UI
        self._init_ui()
        
        # 创建定时器
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.on_timeout)
        
        # 连接动画完成信号
        self.animation_finished.connect(self._on_hide_finished)
        
    def _init_ui(self):
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)
        
        # 创建标题和内容标签
        title = self.title if self.title else self.type
        self.title_label = QLabel(title)
        self.text_label = QLabel(self.text)
        self.text_label.setWordWrap(True)
        
        # 应用字体管理器的优化字体
        font_manager = FontManager()
        font_manager.apply_font(self.title_label)
        font_manager.apply_font(self.text_label)
        
        # 只需设置字号和粗细，其他字体属性由FontManager处理
        title_font = self.title_label.font()
        title_font.setPointSize(14)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        
        text_font = self.text_label.font()
        text_font.setPointSize(12)
        self.text_label.setFont(text_font)
        
        # 根据类型设置样式
        style_map = {
            NotificationType.INFO: ("#1A73E8", "rgba(26, 115, 232, 0.05)", "rgba(26, 115, 232, 0.1)"),
            NotificationType.TIPS: ("#1A73E8", "rgba(26, 115, 232, 0.05)", "rgba(26, 115, 232, 0.1)"),
            NotificationType.WARNING: ("#F9A825", "rgba(249, 168, 37, 0.05)", "rgba(249, 168, 37, 0.1)"),
            NotificationType.WARN: ("#F9A825", "rgba(249, 168, 37, 0.05)", "rgba(249, 168, 37, 0.1)"),
            NotificationType.ERROR: ("#D93025", "rgba(217, 48, 37, 0.05)", "rgba(217, 48, 37, 0.1)"),
            NotificationType.FAILED: ("#D93025", "rgba(217, 48, 37, 0.05)", "rgba(217, 48, 37, 0.1)")
        }
        
        text_color, bg_color, hover_color = style_map.get(self.type, style_map[NotificationType.TIPS])
        
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
        content_widget_layout.addWidget(self.title_label)
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
            QLabel[accessibleName="title"] {{
                color: {text_color};
                font-weight: bold;
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
        
        # 计算基础位置 (右上角)
        margin = 20
        start_x = screen.right() - self.width() - margin
        
        # 计算垂直位置，考虑已有的通知
        total_height = self.height() + margin
        offset = len(Notification.active_notifications) * total_height
        
        # 修改起始和结束位置，确保在屏幕内
        start_y = screen.top() + offset + total_height  # 从屏幕顶部开始
        end_y = screen.top() + offset + margin  # 结束位置在屏幕内
        
        # 将自己添加到活动通知列表
        Notification.active_notifications.append(self)
        
        # 开始显示动画（使用新的动画时长）
        self.pos_animation.setDuration(self.show_animation_duration)
        self.opacity_animation.setDuration(self.show_animation_duration)
        
        self.show_animation(
            QPoint(start_x, start_y),
            QPoint(start_x, end_y)
        )
        
        # 启动自动关闭定时器（添加动画时长，确保动画完成后才开始计时）
        self.timer.start(self.duration + self.show_animation_duration)
        log.debug(f"显示通知: {self.text_label.text()}")
        
    def on_timeout(self):
        # 计算隐藏动画的位置
        screen = QApplication.primaryScreen().availableGeometry()
        margin = 20
        start_x = screen.right() - self.width() - margin
        current_y = self.y()
        end_y = current_y - self.height() - margin  # 向上滑出
        
        # 开始隐藏动画
        self.hide_animation(
            QPoint(start_x, current_y),
            QPoint(start_x, end_y)
        )
        log.debug("通知超时,开始隐藏")
        
    def _on_hide_finished(self):
        # 从活动通知列表中移除自己
        if self in Notification.active_notifications:
            index = Notification.active_notifications.index(self)
            Notification.active_notifications.pop(index)
            
            # 重新调整其他通知的位置
            self._adjust_other_notifications(index)
            
        # 最后删除自己
        self.deleteLater()
        
    def _adjust_other_notifications(self, removed_index):
        screen = QApplication.primaryScreen().availableGeometry()
        margin = 20
        total_height = self.height() + margin
        
        # 调整removed_index之后的所有通知位置
        for i, notif in enumerate(Notification.active_notifications[removed_index:]):
            target_y = screen.top() + (i + removed_index) * total_height + margin
            current_x = notif.x()
            
            # 创建位置动画（使用新的调整动画时长）
            anim = QPropertyAnimation(notif, b"pos", notif)
            anim.setDuration(self.adjust_animation_duration)
            anim.setEasingCurve(QEasingCurve.OutCubic)
            anim.setStartValue(notif.pos())
            anim.setEndValue(QPoint(current_x, target_y))
            anim.start()

# 快速通知方法
def show_info(text, duration=3000):
    notif = Notification(text=text, type=NotificationType.INFO, duration=duration)
    notif.show_notification()
    
def show_warning(text, duration=3000):
    notif = Notification(text=text, type=NotificationType.WARNING, duration=duration)
    notif.show_notification()
    
def show_error(text, duration=3000):
    notif = Notification(text=text, type=NotificationType.ERROR, duration=duration)
    notif.show_notification()

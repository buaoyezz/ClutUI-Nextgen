'''
入口程序
'''

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon
from core.utils.initialization_manager import InitializationManager
from core.log.log_manager import log
from core.utils.notif import Notification, NotificationType
from core.ui.title_bar import TitleBar
from core.window.window_manager import WindowManager
from core.i18n import i18n
import sys
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        InitializationManager.init_log_directory()
        InitializationManager.init_window_components(self)
        log.info(i18n.get_text("init_window"))
        
        # 设置应用图标
        icon = QIcon("resources/logo.png")
        self.setWindowIcon(icon)
        QApplication.setWindowIcon(icon)
        
        # 设置窗口基本属性
        self.setWindowTitle(i18n.get_text("app_title", "ClutUI Nextgen"))
        self.setMinimumSize(600, 450)
        self.resize(1080, 650)
        
        # 设置窗口背景透明和无边框
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        
        # 创建主窗口部件
        main_widget = QWidget()
        main_widget.setObjectName("mainWidget")
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.title_bar = TitleBar(self)
        self.title_bar.title_label.setText(i18n.get_text("app_title_full", "ClutUI Next Generation"))
        main_layout.addWidget(self.title_bar)
        
        # 创建内容区域容器
        content_container = QWidget()
        content_layout = QHBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # 右侧内容区
        right_content = QWidget()
        self.right_layout = QVBoxLayout(right_content)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建页面容器
        self.page_container = QWidget()
        self.page_layout = QVBoxLayout(self.page_container)
        self.page_layout.setContentsMargins(0, 0, 0, 0)
        self.page_layout.addWidget(self.pages_manager.get_stacked_widget())
        self.right_layout.addWidget(self.page_container)
        
        # 将左右两侧添加到内容布局
        content_layout.addWidget(self.pages_manager.get_sidebar())
        content_layout.addWidget(right_content)
        
        # 将内容容器添加到主布局
        main_layout.addWidget(content_container)
        
        # 设置主窗口样式
        main_widget.setStyleSheet("""
            QWidget#mainWidget {
                background-color: #F8F9FA;
                border-radius: 10px;
                border: 1px solid #E0E0E0;
            }
        """)
        
        self.setCentralWidget(main_widget)
        
        # 初始化关闭相关属性
        self._closing = False
        self._cleanup_timer = QTimer()
        self._cleanup_timer.setSingleShot(True)
        self._cleanup_timer.timeout.connect(self._finish_close)
        self._notifications = []
        
        # 注册语言变更回调
        i18n.add_language_change_callback(self._on_language_changed)

    def _on_language_changed(self):
        self.setWindowTitle(i18n.get_text("app_title", "ClutUI Nextgen"))
        self.title_bar.title_label.setText(i18n.get_text("app_title_full", "ClutUI Next Generation"))
        # 通知页面管理器更新所有页面的文本
        self.pages_manager.update_all_pages_text()

    def closeEvent(self, event):
        WindowManager.handle_close_event(self, event)

    def _finish_close(self):
        WindowManager.finish_close(self)
        i18n.remove_language_change_callback(self._on_language_changed)

    def switch_page(self, page_name):
        WindowManager.switch_page(self, page_name)

    def show_notification(self, text, type=NotificationType.TIPS, duration=1000):
        notification = Notification(
            text=text,
            type=type,
            duration=duration,
            parent=self
        )
        self._notifications.append(notification)
        notification.animation_finished.connect(
            lambda: self._notifications.remove(notification) if notification in self._notifications else None
        )
        notification.show_notification()

if __name__ == '__main__':
    try:
        app = InitializationManager.init_application()
        window = MainWindow()
        window.show()
        log.info(i18n.get_text("app_started"))
        
        notification = Notification(
            text=i18n.get_text("welcome_notification"),
            type=NotificationType.TIPS,
            parent=window
        )
        notification.show_notification()
        
        exit_code = app.exec()
        window._finish_close()
        sys.exit(exit_code)
        
    except Exception as e:
        log.error(f"{i18n.get_text('app_error')}: {str(e)}")
        sys.exit(1)


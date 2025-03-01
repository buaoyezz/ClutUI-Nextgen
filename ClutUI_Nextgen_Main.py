'''
入口程序
'''

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QIcon, QWindow
from core.utils.initialization_manager import InitializationManager
from core.log.log_manager import log
from core.utils.notif import Notification, NotificationType
from core.ui.title_bar import TitleBar
from core.window.window_manager import WindowManager
from core.i18n import i18n
from core.pages_core.pages_effect import PagesEffect
from core.utils.resource_manager import ResourceManager
from core.utils.yiyanapi import YiyanAPI
import sys
import os
import json
import ctypes
import win32gui
import win32con

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        InitializationManager.init_log_directory()
        InitializationManager.init_window_components(self)
        log.info(i18n.get_text("init_window"))
        
        # 设置应用图标
        resource_manager = ResourceManager()
        icon = resource_manager.get_icon("logo")
        if icon:
            # 设置窗口图标
            self.setWindowIcon(icon)
            QApplication.setWindowIcon(icon)
            
            # 设置任务栏图标
            if os.name == 'nt':  # Windows系统
                try:
                    # 获取窗口句柄
                    hwnd = self.winId().__int__()
                    
                    # 加载图标文件
                    icon_path = resource_manager.get_resource_path(os.path.join("resources", "logo.png"))
                    if os.path.exists(icon_path):
                        # 设置任务栏图标
                        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("ClutUI.Nextgen")
                        log.info("成功设置任务栏图标")
                except Exception as e:
                    log.error(f"设置任务栏图标失败: {str(e)}")
            
            log.info("成功加载应用图标")
        
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
        
        # 先隐藏主窗口部件，避免初始化时的闪烁
        main_widget.hide()
        
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
        
        # 设置窗口属性以支持圆角
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.setCentralWidget(main_widget)
        
        # 初始化关闭相关属性
        self._closing = False
        self._cleanup_timer = QTimer()
        self._cleanup_timer.setSingleShot(True)
        self._cleanup_timer.timeout.connect(self._finish_close)
        self._notifications = []
        
        # 连接语言变更信号
        i18n.language_changed.connect(self._on_language_changed)
        
        # 预先应用一次模糊效果
        PagesEffect.apply_blur_effect(self)
        
        # 使用QTimer延迟应用背景效果并显示窗口
        QTimer.singleShot(50, self._init_background_effect)
        
        # 异步加载一言并显示欢迎通知
        self._show_welcome_notification()

    def _show_welcome_notification(self):
        self.yiyan_api = YiyanAPI()
        # 连接信号
        self.yiyan_api.hitokoto_ready.connect(
            lambda text: self.show_notification(
                text=text,
                type=NotificationType.TIPS,
                duration=3000
            )
        )
        # 开始异步获取
        initial_text = self.yiyan_api.get_hitokoto_async()
        # 显示初始通知
        self.show_notification(
            text=initial_text,
            type=NotificationType.TIPS,
            duration=3000
        )

    def _init_background_effect(self):
        try:
            with open('config.json', 'r') as f:
                config = json.loads(f.read())
                effect = config.get('background_effect', 'effect_none')
                
                if effect == 'effect_none':
                    PagesEffect.remove_effects(self)
                elif effect == 'effect_mica':
                    PagesEffect.apply_mica_effect(self)
                elif effect == 'effect_gaussian':
                    PagesEffect.apply_gaussian_blur(self)
                elif effect == 'effect_blur':
                    PagesEffect.apply_blur_effect(self)
                elif effect == 'effect_acrylic':
                    PagesEffect.apply_acrylic_effect(self)
                elif effect == 'effect_aero':
                    PagesEffect.apply_aero_effect(self)
                else:
                    # 未知效果，使用默认模糊效果
                    PagesEffect.apply_blur_effect(self)
        except Exception as e:
            # 如果配置读取失败，默认使用无效果
            log.error(f"应用背景效果时出错: {str(e)}")
            PagesEffect.remove_effects(self)
        
        # 显示主窗口部件
        self.centralWidget().show()

    def _apply_saved_background_effect(self):
        self._init_background_effect()

    def _on_language_changed(self, lang=None):
        self.setWindowTitle(i18n.get_text("app_title", "ClutUI Nextgen"))
        self.title_bar.title_label.setText(i18n.get_text("app_title_full", "ClutUI Next Generation"))
        # 通知页面管理器更新所有页面的文本
        self.pages_manager.update_all_pages_text()

    def _finish_close(self):
        WindowManager.finish_close(self)
        # 断开信号连接
        try:
            i18n.language_changed.disconnect(self._on_language_changed)
        except:
            pass

    def closeEvent(self, event):
        WindowManager.handle_close_event(self, event)

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
        
        exit_code = app.exec()
        sys.exit(exit_code)
        
    except Exception as e:
        log.error(f"{i18n.get_text('app_error')}: {str(e)}")
        sys.exit(1)


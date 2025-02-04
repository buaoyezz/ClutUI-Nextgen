from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                             QHBoxLayout, QPushButton)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from core.ui.buttons_blue import Button
from core.font.font_pages_manager import FontPagesManager
from core.utils.notif import Notification, NotificationType
from core.animations.notification_ani import NotificationAnimation
from core.log.log_manager import log

class AboutPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.font_manager = FontPagesManager()
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)
        
        # 标题
        title = QLabel("Clut UI\nNext Generation")
        title.setStyleSheet("""
            QLabel {
                color: #333333;
                font-size: 36px;
                font-weight: bold;
                background: transparent;
            }
        """)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # 版本信息
        version = QLabel("Version 0.0.1Alpha")
        version.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 16px;
                background: transparent;
            }
        """)
        version.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(version)
        
        main_layout.addSpacing(30)
        
        # 按钮区域
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        # 检查更新按钮
        update_btn = Button(text="版本发布页面", style="blue")
        update_btn.setFixedSize(150, 40)
        update_btn.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl("https://github.com/buaoyezz/ClutUI-Nextgen/releases")))
        buttons_layout.addWidget(update_btn)
        
        # 官方网站按钮
        website_btn = Button(text="官方网站", style="blue")
        website_btn.setFixedSize(150, 40)
        website_btn.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl("https://zzbuaoye.us.kg")))
        buttons_layout.addWidget(website_btn)
        
        # GitHub按钮
        github_btn = Button(text="GitHub", style="blue")
        github_btn.setFixedSize(150, 40)
        github_btn.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl("https://github.com/ZZBuaaYe/ClutUI-Nextgen")))
        buttons_layout.addWidget(github_btn)
        
        # 添加通知按钮
        notify_btn = Button(text="显示通知", style="blue")
        notify_btn.setFixedSize(150, 40)
        notify_btn.clicked.connect(self.show_notification)
        buttons_layout.addWidget(notify_btn)
        
        buttons_layout.setAlignment(Qt.AlignCenter)
        main_layout.addLayout(buttons_layout)
        
        main_layout.addSpacing(40)
        
        # 描述文本
        description = QLabel(
            "ClutUI Nextgen是ClutUI1.0后的下一代！\n"
            "全新的Clut UI 2.0 界面，更加简洁美观\n"
            "全新的项目结构，更加便于开发\n"
            "全新的功能，更加强大\n"
            "全新的体验，更加流畅\n"
        )
        description.setWordWrap(True)
        description.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 14px;
                line-height: 24px;
                background: transparent;
            }
        """)
        description.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(description)
        
        # 添加额外的信息文本
        extra_info = QLabel("FOR PYTHON 3.12 AND PYSIDE6 MADE BY ZZBUAOYE")  # 这里可以放置额外的文字内容
        extra_info.setWordWrap(True)
        extra_info.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 14px;
                line-height: 24px;
                background: transparent;
            }
        """)
        extra_info.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(extra_info)
        
        # 版权信息
        copyright = QLabel("© 2024 ClutUI Nextgen. By ZZBuAoYe All rights reserved.")
        copyright.setStyleSheet("""
            QLabel {
                color: #999999;
                font-size: 12px;
                background: transparent;
            }
        """)
        copyright.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(copyright)
        
        # 使用 addStretch 让内容居中显示
        main_layout.addStretch()
        
        # 设置背景颜色
        self.setStyleSheet("""
            QWidget {
                background: #F8F9FA;
            }
        """)
    def show_notification(self):
        try:
            # 获取主窗口实例
            main_window = self.window()
            if main_window:
                main_window.show_notification(
                    text="ClutUI Nextgen 已准备好为您服务喵~",
                    type=NotificationType.TIPS,
                    duration=3000
                )
                log.debug("关于页面欢迎通知已触发")
            else:
                log.error("无法获取主窗口实例")
            
        except Exception as e:
            log.error(f"弹出通知时遇到问题: {str(e)}")
            # 尝试使用简单通知作为后备方案
            try:
                if self.window():
                    self.window().show_notification(
                        text="无法显示完整通知，但我们正在努力修复这个问题~",
                        type=NotificationType.WARNING,
                        duration=2000
                    )
            except Exception as backup_error:
                log.error(f"备用通知也失败了: {str(backup_error)}")

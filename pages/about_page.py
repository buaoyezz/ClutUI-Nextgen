from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                             QHBoxLayout, QScrollArea)
from PySide6.QtCore import Qt, QUrl, QTimer
from PySide6.QtGui import QDesktopServices, QPixmap
from core.ui.button_white import WhiteButton
from core.font.font_pages_manager import FontPagesManager
from core.utils.notif import NotificationType
from core.log.log_manager import log
from core.ui.scroll_style import ScrollStyle
from core.animations.scroll_hide_show import ScrollBarAnimation
from core.font.font_manager import resource_path
import os

class AboutPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.font_manager = FontPagesManager()
        self.setup_ui()
        
    def setup_ui(self):
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建一个容器来包裹滚动区域
        scroll_container = QWidget()
        scroll_container.setObjectName("scrollContainer")
        scroll_container_layout = QVBoxLayout(scroll_container)
        scroll_container_layout.setContentsMargins(0, 0, 0, 0)
        
        # 设置滚动区域
        scroll_area = QScrollArea()
        self.scroll_area = scroll_area
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setObjectName("scrollArea")
        
        # 设置滚动条动画
        self.scroll_animation = ScrollBarAnimation(scroll_area.verticalScrollBar())
        
        # 连接滚动条值改变信号
        scroll_area.verticalScrollBar().valueChanged.connect(
            self.scroll_animation.show_temporarily
        )
        
        # 内容容器
        container = QWidget()
        container.setObjectName("container")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(40, 60, 40, 60)
        container_layout.setSpacing(30)
        
        # Logo和标题区域
        logo_label = QLabel()
        logo_path = resource_path(os.path.join("resources", "logo2.png"))
        logo_pixmap = QPixmap(logo_path)
        scaled_pixmap = logo_pixmap.scaled(400, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(scaled_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(logo_label)
        
        subtitle = QLabel("Next Generation")
        self.font_manager.apply_subtitle_style(subtitle)
        subtitle.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(subtitle)
        
        version = QLabel("Version 0.0.5 Alpha")
        self.font_manager.apply_small_style(version)
        version.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(version)
        
        container_layout.addSpacing(40)
    
        main_buttons = QHBoxLayout()
        main_buttons.setSpacing(20)
        
        buttons_data = [
            ("更新日志", "https://github.com/buaoyezz/ClutUI-Nextgen/releases", "history"),
            ("文档", "https://zzbuaoye.us.kg/clutui/docs/", "article"),
            ("源代码", "https://github.com/buaoyezz/ClutUI-Nextgen", "code"),
        ]
        
        for text, url, icon in buttons_data:
            btn = WhiteButton(title=text, icon=self.font_manager.get_icon_text(icon))
            btn.clicked.connect(lambda u=url: QDesktopServices.openUrl(QUrl(u)))
            main_buttons.addWidget(btn)
        
        main_buttons.setAlignment(Qt.AlignCenter)
        container_layout.addLayout(main_buttons)
        
        container_layout.addSpacing(30)
        
        # 介绍文本
        intro_text = QLabel(
            "ClutUI Next Generation 是不基于ClutUI1.0的新一代的UI开发框架\n"
            "致力于提供简单、高效、美观的界面开发体验"
        )
        intro_text.setWordWrap(True)
        self.font_manager.apply_normal_style(intro_text)
        intro_text.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(intro_text)
        
        container_layout.addSpacing(40)
        
        # 技术信息
        tech_info = QLabel(
            "基于 Python 3.12 & PySide6\n"
            "界面设计参考 Material Design 3\n"
            "字体: HarmonyOS Sans & Mulish\n"
            "图标: Material Icons\n"
            "动画: QPropertyAnimation & QEasingCurve\n"
            "本软件使用的上述字体，请遵守相关协议和限制，不可修改，不可二次分发，其他具体限制范围需要咨询相关部门\n"
            "详情查看下述按钮相关协议与许可协议"
        )
        tech_info.setWordWrap(True)
        self.font_manager.apply_small_style(tech_info)
        tech_info.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(tech_info)
        
        container_layout.addSpacing(20)
        
        # 法律信息按钮
        legal_buttons = QHBoxLayout()
        legal_buttons.setSpacing(15)
        
        legal_data = [
            ("许可协议", "https://zzbuaoye.us.kg/clutui/font/license.txt", "gavel"),
            ("相关协议", "https://zzbuaoye.us.kg/clutui/statement.txt", "shield"),
        ]
        
        for text, url, icon in legal_data:
            btn = WhiteButton(title=text, icon=self.font_manager.get_icon_text(icon))
            btn.setFixedWidth(120)
            btn.clicked.connect(lambda u=url: QDesktopServices.openUrl(QUrl(u)))
            legal_buttons.addWidget(btn)
        
        legal_buttons.setAlignment(Qt.AlignCenter)
        container_layout.addLayout(legal_buttons)
        
        container_layout.addSpacing(30)
        
        # 版权信息
        copyright = QLabel("© 2025 ClutUI Next Generation. All rights reserved.")
        self.font_manager.apply_small_style(copyright)
        copyright.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(copyright)
        
        container_layout.addStretch()
        
        # 设置滚动区域的内容
        scroll_area.setWidget(container)
        scroll_container_layout.addWidget(scroll_area)
        
        # 将滚动容器添加到主布局
        main_layout.addWidget(scroll_container)
        
        # 更新样式表
        self.setStyleSheet(f"""
            QWidget#scrollContainer {{
                background: transparent;
                margin: 0px 20px;
            }}
            
            QScrollArea#scrollArea {{
                background: transparent;
                border: none;
            }}
            
            QWidget#container {{
                background: transparent;
            }}
            
            QLabel {{
                color: #1F2937;
                background: transparent;
            }}
            
            /* 自定义滚动条样式 */
            QScrollBar:vertical {{
                background: transparent;
                width: 8px;
                margin: 4px 4px 4px 4px;
            }}
            
            QScrollBar::handle:vertical {{
                background: #C0C0C0;
                border-radius: 4px;
                min-height: 30px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background: #A0A0A0;
            }}
            
            QScrollBar::add-line:vertical {{
                height: 0px;
            }}
            
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
        """)

    def show_notification(self):
        try:
            main_window = self.window()
            if main_window:
                main_window.show_notification(
                    text="欢迎使用 ClutUI Next Generation",
                    type=NotificationType.TIPS,
                    duration=1000
                )
                log.debug("显示欢迎通知")
            else:
                log.error("未找到主窗口实例")
        except Exception as e:
            log.error(f"显示通知出错: {str(e)}")

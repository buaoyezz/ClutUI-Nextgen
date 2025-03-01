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
from core.i18n import i18n
import os

class AboutPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.font_manager = FontPagesManager()
        
        # 创建主布局
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        self.setup_ui()
        
        # 连接语言变更信号
        i18n.language_changed.connect(self.update_text)
        
    def setup_ui(self):
        # 创建一个容器来包裹滚动区域
        scroll_container = QWidget()
        scroll_container.setObjectName("scrollContainer")
        scroll_container_layout = QVBoxLayout(scroll_container)
        scroll_container_layout.setContentsMargins(0, 0, 0, 0)
        
        # 设置全局样式
        self.setStyleSheet("""
            QWidget#scrollContainer {
                background: transparent;
                margin: 0px 20px;
            }
            
            QScrollArea#scrollArea {
                background: transparent;
                border: none;
            }
            
            QWidget#container {
                background: transparent;
            }
            
            QLabel {
                color: #1F2937;
                background: transparent;
                font-size: 14px;
                letter-spacing: 0.3px;
            }
            
            QLabel[class="title"] {
                font-size: 24px;
                font-weight: 600;
                color: #1F2937;
            }
            
            QLabel[class="subtitle"] {
                font-size: 18px;
                font-weight: 500;
                color: #2196F3;
            }
            
            QLabel[class="version"] {
                font-size: 13px;
                color: #666666;
            }
            
            QLabel[class="description"] {
                font-size: 14px;
                color: #666666;
                line-height: 1.6;
            }
            
            QLabel[class="copyright"] {
                font-size: 12px;
                color: #9E9E9E;
            }
            
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
        
        # 设置滚动区域
        scroll_area = QScrollArea()
        self.scroll_area = scroll_area
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setObjectName("scrollArea")
        
        # 应用滚动条样式
        ScrollStyle.apply_to_widget(scroll_area)
        
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
        
        self.subtitle = QLabel("Next Generation")
        self.font_manager.apply_subtitle_style(self.subtitle)
        self.subtitle.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(self.subtitle)
        
        self.version = QLabel(i18n.get_text("version"))
        self.font_manager.apply_small_style(self.version)
        self.version.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(self.version)
        
        container_layout.addSpacing(40)
    
        main_buttons = QHBoxLayout()
        main_buttons.setSpacing(20)
        
        # 按钮配置
        self.buttons_data = [
            ("changelog", i18n.get_text("urls.changelog"), "history"),
            ("documentation", i18n.get_text("urls.documentation"), "article"),
            ("source_code", i18n.get_text("urls.source_code"), "code"),
        ]
        
        self.main_buttons = []  # 存储主要按钮引用
        for key, url, icon in self.buttons_data:
            btn = WhiteButton(title=i18n.get_text(key), icon=self.font_manager.get_icon_text(icon))
            btn.clicked.connect(lambda u=url: QDesktopServices.openUrl(QUrl(u)))
            main_buttons.addWidget(btn)
            self.main_buttons.append((key, btn))  # 保存按钮引用和对应的key
        
        main_buttons.setAlignment(Qt.AlignCenter)
        container_layout.addLayout(main_buttons)
        
        container_layout.addSpacing(30)
        
        # 介绍文本
        self.intro_text = QLabel(i18n.get_text("intro_text"))
        self.intro_text.setWordWrap(True)
        self.font_manager.apply_normal_style(self.intro_text)
        self.intro_text.setStyleSheet("""
            QLabel {
                color: #666666;
                background: transparent;
            }
        """)
        self.intro_text.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(self.intro_text)
        
        container_layout.addSpacing(40)
        
        # 技术信息
        self.tech_info = QLabel(i18n.get_text("tech_info"))
        self.tech_info.setWordWrap(True)
        self.font_manager.apply_small_style(self.tech_info)
        self.tech_info.setStyleSheet("""
            QLabel {
                color: #666666;
                background: transparent;
            }
        """)
        self.tech_info.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(self.tech_info)
        
        container_layout.addSpacing(20)
        
        # 法律信息按钮
        legal_buttons = QHBoxLayout()
        legal_buttons.setSpacing(15)
        
        self.legal_buttons_data = [
            ("license", i18n.get_text("urls.license"), "gavel"),
            ("related_terms", i18n.get_text("urls.related_terms"), "shield"),
        ]
        
        self.legal_buttons = []  # 存储法律按钮引用
        for key, url, icon in self.legal_buttons_data:
            btn = WhiteButton(title=i18n.get_text(key), icon=self.font_manager.get_icon_text(icon))
            btn.setFixedWidth(120)
            btn.clicked.connect(lambda u=url: QDesktopServices.openUrl(QUrl(u)))
            legal_buttons.addWidget(btn)
            self.legal_buttons.append((key, btn))  # 保存按钮引用和对应的key
        
        legal_buttons.setAlignment(Qt.AlignCenter)
        container_layout.addLayout(legal_buttons)
        
        container_layout.addSpacing(30)
        
        # 版权信息
        self.copyright = QLabel(i18n.get_text("copyright"))
        self.font_manager.apply_small_style(self.copyright)
        self.copyright.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(self.copyright)
        
        container_layout.addStretch()
        
        # 设置滚动区域的内容
        scroll_area.setWidget(container)
        scroll_container_layout.addWidget(scroll_area)
        
        # 将滚动容器添加到主布局
        self.layout.addWidget(scroll_container)

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

    def update_text(self):
        # 更新标题文本
        if hasattr(self, 'subtitle'):
            self.subtitle.setText(i18n.get_text("next_generation"))
            
        # 更新版本文本
        if hasattr(self, 'version'):
            self.version.setText(i18n.get_text("version"))
            
        # 更新主要按钮文本
        if hasattr(self, 'main_buttons'):
            for key, button in self.main_buttons:
                button.update_title(i18n.get_text(key))
                    
        # 更新介绍文本
        if hasattr(self, 'intro_text'):
            self.intro_text.setText(i18n.get_text("intro_text"))
            
        # 更新技术信息
        if hasattr(self, 'tech_info'):
            self.tech_info.setText(i18n.get_text("tech_info"))
            
        # 更新法律按钮文本
        if hasattr(self, 'legal_buttons'):
            for key, button in self.legal_buttons:
                button.update_title(i18n.get_text(key))
                    
        # 更新版权信息
        if hasattr(self, 'copyright'):
            self.copyright.setText(i18n.get_text("copyright"))

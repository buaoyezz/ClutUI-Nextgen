from PySide6.QtWidgets import (QLabel, QPushButton, QHBoxLayout, QWidget, 
                             QVBoxLayout, QFrame, QGraphicsDropShadowEffect, QMessageBox)
from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtGui import QColor, QDesktopServices
from core.utils.notif import Notification
from core.ui.buttons_blue import Button
from core.log.log_manager import log
from core.ui.little_card import LittleCard
from core.utils.notif import Notification, NotificationType
from core.font.font_pages_manager import FontPagesManager
from core.ui.little_card2 import LittleCard2
from core.i18n import i18n
from core.utils.yiyanapi import YiyanAPI

class InfoCard(QFrame):
    clicked = Signal(str)
    
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.title = title
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # 标题
        title_label = QLabel(self.title)
        self.font_manager = FontPagesManager()  # 添加字体管理器
        self.font_manager.apply_font(title_label, "title")  # 应用普通字体
        title_label.setStyleSheet("""
            QLabel {
                color: #333333;
                background: transparent;
                font-size: 16px;
                font-weight: 500;
                letter-spacing: 0.3px;
            }
        """)
        
        # 主要信息显示
        self.info_label = QLabel("")
        self.font_manager.apply_font(self.info_label, "title")  # 应用标题字体
        self.info_label.setStyleSheet("""
            QLabel {
                color: #2196F3;
                background: transparent;
                font-size: 15px;
                font-weight: 500;
                letter-spacing: 0.3px;
            }
        """)
        
        # 次要信息显示
        self.sub_info_label = QLabel("Open Link➡")
        self.font_manager.apply_font(self.sub_info_label, "small")  # 应用小字体
        self.sub_info_label.setStyleSheet("""
            QLabel {
                color: #666666;
                background: transparent;
                font-size: 13px;
                letter-spacing: 0.2px;
            }
        """)
        
        layout.addWidget(title_label, alignment=Qt.AlignLeft)
        layout.addWidget(self.info_label, alignment=Qt.AlignRight)
        layout.addWidget(self.sub_info_label, alignment=Qt.AlignRight)
        
        # 卡片样式
        self.setStyleSheet("""
            InfoCard {
                background: white;
                border-radius: 15px;
                border: 1px solid #E0E0E0;
            }
            InfoCard:hover {
                background: #F5F5F5;
                border: 1px solid #2196F3;
            }
        """)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.title)
            
    def update_info(self, main_info, sub_info=None):
        self.info_label.setText(main_info)
        if sub_info is not None:
            self.sub_info_label.setText(sub_info)

class QuickStartPage(QWidget):
    category_clicked = Signal(str)
    switch_page_requested = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.info_cards = {}
        self.font_manager = FontPagesManager()
        self.yiyan_api = YiyanAPI()
        
        # 创建主布局
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(15)
        
        self.setup_ui()
        
        # 连接语言变更信号
        i18n.language_changed.connect(self.update_text)

    def setup_ui(self):
        # 顶部标题
        main_title = QLabel("ClutUI Nextgen")
        self.font_manager.apply_font(main_title, "title")  # 应用标题字体
        main_title.setStyleSheet("""
            QLabel {
                color: #1F2937;
                background: transparent;
                font-size: 36px;
                font-weight: 600;
                letter-spacing: 1px;
                padding: 20px 0;
            }
        """)
        main_title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(main_title)
        
        # 说明文本
        hitokoto = self.yiyan_api.get_hitokoto_sync()
        description = QLabel(f"{hitokoto}")
        self.font_manager.apply_font(description, "normal")  # 应用普通字体
        description.setStyleSheet("""
            QLabel {
                color: #666666;
                background: transparent;
                font-size: 15px;
                line-height: 24px;
                letter-spacing: 0.3px;
            }
        """)
        description.setAlignment(Qt.AlignCenter)
        description.setWordWrap(True)  # 启用自动换行
        self.layout.addWidget(description)
        
        self.layout.addSpacing(40)
        
        # 信息卡片配置
        cards_config = [
            {
                "title": "Pyside6 Link",
                "description": i18n.get_text("official_doc"),
                "link_url": "https://doc.qt.io/qtforpython-6/"
            },
            {
                "title": "Python Link",
                "description": i18n.get_text("python_official"),
                "link_url": "https://www.python.org/"
            },
            {
                "title": "Clut UI Link",
                "description": i18n.get_text("project_repo"),
                "link_url": "https://github.com/buaoyezz/ClutUI-Nextgen"
            },
            {
                "title": "ZZBUAOYE Link",
                "description": i18n.get_text("author_page"),
                "link_url": "https://github.com/buaoyezz"
            }
        ]
        
        # 创建卡片网格
        grid_layout = QHBoxLayout()
        grid_layout.setSpacing(25)
        
        for config in cards_config:
            card = LittleCard(**config)
            card.clicked.connect(self.on_category_clicked)
            self.info_cards[config["title"]] = card
            grid_layout.addWidget(card)
            
        self.layout.addLayout(grid_layout)
        
        self.layout.addSpacing(30)
         
        # 设置整体样式
        self.setStyleSheet("""
            QWidget {
                background: #F8F9FA;
            }
        """)

    def on_category_clicked(self, category):
        urls = {
            "Pyside6 Link": "https://doc.qt.io/qtforpython-6/",
            "Python Link": "https://www.python.org/",
            "Clut UI Link": "https://github.com/buaoyezz/ClutUI-Nextgen",
            "ZZBUAOYE Link": "https://github.com/buaoyezz"
        }
        
        if category in urls:
            url = QUrl(urls[category])
            QDesktopServices.openUrl(url)
            log.info(f"打开链接: {urls[category]}")
            
            # 添加通知
            Notification(
                text=f"正在打开 {category} 链接",
                type=NotificationType.TIPS,
                duration=1000
            ).show_notification()
            
    def switch_page(self, page_name):
        self.switch_page_requested.emit(page_name)
        log.info(f"请求切换到页面: {page_name}")

    def on_top_card_clicked(self):
        log.info("Top card clicked")
        # 在这里添加点击卡片后的处理逻辑 

    def update_text(self):
        """更新页面所有文本"""
        # 更新卡片文本
        cards_config = {
            "Pyside6 Link": {
                "description": i18n.get_text("official_doc")
            },
            "Python Link": {
                "description": i18n.get_text("python_official")
            },
            "Clut UI Link": {
                "description": i18n.get_text("project_repo")
            },
            "ZZBUAOYE Link": {
                "description": i18n.get_text("author_page")
            }
        }
        
        for title, config in cards_config.items():
            if title in self.info_cards:
                card = self.info_cards[title]
                if hasattr(card, 'description_label'):
                    card.description_label.setText(config["description"]) 
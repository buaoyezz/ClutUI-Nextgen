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
            }
        """)
        
        # 主要信息显示
        self.info_label = QLabel("")
        self.font_manager.apply_font(self.info_label, "title")  # 应用标题字体
        self.info_label.setStyleSheet("""
            QLabel {
                color: #2196F3;
                background: transparent;
            }
        """)
        
        # 次要信息显示
        self.sub_info_label = QLabel("Open Link➡")
        self.font_manager.apply_font(self.sub_info_label, "small")  # 应用小字体
        self.sub_info_label.setStyleSheet("""
            QLabel {
                color: #666666;
                background: transparent;
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
        self.font_manager = FontPagesManager()  # 添加字体管理器
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(15)
        """
        # Card2预览用的代码，可删
        # 左上角的LittleCard2
        # top_card = LittleCard2(
        #     title="Title",
        #     label="Label",
        #     action_text="Action"
        # )
        # top_card.setFixedSize(200, 120)  # 设置卡片大小
        # top_card.clicked.connect(lambda: self.on_top_card_clicked())
        
        # # 创建一个容器来包含top_card，并设置对齐方式
        # top_container = QWidget()
        # top_layout = QHBoxLayout(top_container)
        # top_layout.setContentsMargins(0, 0, 0, 0)
        # top_layout.addWidget(top_card, alignment=Qt.AlignLeft)
        # top_layout.addStretch()  # 添加弹性空间，使卡片保持在左侧
        
        # main_layout.addWidget(top_container)
        """
        # 顶部标题
        main_title = QLabel("ClutUI Nextgen")
        self.font_manager.apply_font(main_title, "title")  # 应用标题字体
        main_title.setStyleSheet("""
            QLabel {
                color: rgba(51, 51, 51, 0.85); 
                letter-spacing: 1px;
            }
        """)
        main_title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(main_title)
        
        # 说明文本
        description = QLabel("")
        self.font_manager.apply_font(description, "normal")  # 应用普通字体
        description.setStyleSheet("""
            QLabel {
                color: rgba(102, 102, 102, 0.85);
                line-height: 24px;
            }
        """)
        description.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(description)
        
        main_layout.addSpacing(40)
        
        # 信息卡片配置
        cards_config = [
            {
                "title": "Pyside6 Link",
                "description": "官方文档",
                "link_url": "https://doc.qt.io/qtforpython-6/"
            },
            {
                "title": "Python Link",
                "description": "Python官网",
                "link_url": "https://www.python.org/"
            },
            {
                "title": "Clut UI Link",
                "description": "项目仓库",
                "link_url": "https://github.com/buaoyezz/ClutUI-Nextgen"
            },
            {
                "title": "ZZBUAOYE Link",
                "description": "作者主页",
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
            
        main_layout.addLayout(grid_layout)
        
        main_layout.addSpacing(30)
         
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
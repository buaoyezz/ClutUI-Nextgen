from PySide6.QtWidgets import (QLabel, QPushButton, QHBoxLayout, QWidget, 
                             QVBoxLayout, QFrame, QGraphicsDropShadowEffect, QMessageBox)
from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtGui import QColor, QDesktopServices
from core.utils.notif import Notification
from core.ui.buttons_blue import Button
from core.log.log_manager import log
from core.ui.little_card import LittleCard
from core.utils.notif import Notification, NotificationType
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
        title_label.setStyleSheet("""
            QLabel {
                color: #333333;
                font-size: 16px;
                font-weight: bold;
                background: transparent;
            }
        """)
        
        # 主要信息显示
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("""
            QLabel {
                color: #2196F3;
                font-size: 24px;
                font-weight: bold;
                background: transparent;
            }
        """)
        
        # 次要信息显示
        self.sub_info_label = QLabel("Open Link➡")
        self.sub_info_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 12px;
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
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(15)
        
        # 顶部标题
        main_title = QLabel("ClutUI Nextgen")
        main_title.setStyleSheet("""
            QLabel {
                color: rgba(51, 51, 51, 0.85); 
                font-size: 42px;
                font-weight: bold;
                letter-spacing: 1px;
            }
        """)
        main_title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(main_title)
        
        
        # 说明文本
        description = QLabel("")
        description.setStyleSheet("""
            QLabel {
                color: rgba(102, 102, 102, 0.85);
                font-size: 16px;
                letter-spacing: 0.3px;
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
            
            # 使用主窗口的通知方法
            if self.window():
                self.window().show_notification(
                    text=f"正在打开 {category}  ",
                    type=NotificationType.TIPS,
                    duration=3000
                )
        else:
            QMessageBox.warning(self, "提示", "无效的链接")
            
    def switch_page(self, page_name):
        self.switch_page_requested.emit(page_name)
        log.info(f"请求切换到页面: {page_name}") 
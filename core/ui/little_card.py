from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtGui import QColor, QDesktopServices
from core.font.font_manager import FontManager
from core.log.log_manager import log
from core.utils.notif import Notification, NotificationType

class LittleCard(QFrame):
    clicked = Signal(str)
    
    def __init__(self, 
                 title="", 
                 description="",
                 link_text="Open Link➡",
                 link_url="",
                 notify_on_click=True,
                 parent=None):
        """
        创建一个小卡片组件
        
        Args:
            title (str): 卡片标题
            description (str): 卡片描述文字
            link_text (str): 链接文字
            link_url (str): 点击后打开的链接
            notify_on_click (bool): 点击时是否显示通知
            parent (QWidget): 父组件
        """
        super().__init__(parent)
        self.title = title
        self.description = description
        self.link_text = link_text
        self.link_url = link_url
        self.notify_on_click = notify_on_click
        
        # 创建字体管理器
        self.font_manager = FontManager()
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI布局"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # 标题
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet("""
            QLabel {
                color: #333333;
                font-size: 16px;
                font-weight: bold;
                background: transparent;
            }
        """)
        self.font_manager.apply_font(self.title_label)
        
        # 描述文字
        self.description_label = QLabel(self.description)
        self.description_label.setStyleSheet("""
            QLabel {
                color: #2196F3;
                font-size: 24px;
                font-weight: bold;
                background: transparent;
            }
        """)
        self.font_manager.apply_font(self.description_label)
        
        # 链接文字
        self.link_label = QLabel(self.link_text)
        self.link_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 12px;
                background: transparent;
            }
        """)
        self.font_manager.apply_font(self.link_label)
        
        # 添加到布局
        layout.addWidget(self.title_label, alignment=Qt.AlignLeft)
        layout.addWidget(self.description_label, alignment=Qt.AlignRight)
        layout.addWidget(self.link_label, alignment=Qt.AlignRight)
        
        # 卡片样式
        self.setStyleSheet("""
            LittleCard {
                background: white;
                border-radius: 15px;
                border: 1px solid #E0E0E0;
            }
            LittleCard:hover {
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
        """处理鼠标点击事件"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.title)
            if self.link_url:
                QDesktopServices.openUrl(QUrl(self.link_url))
                log.info(f"打开链接: {self.link_url}")
                
                if self.notify_on_click:
                    Notification(
                        text=f"正在打开 {self.title} 链接",
                        type=NotificationType.TIPS,
                        duration=3000
                    ).show_notification()
                    
    def update_content(self, title=None, description=None, link_text=None, link_url=None):
        """更新卡片内容"""
        if title is not None:
            self.title = title
            self.title_label.setText(title)
            
        if description is not None:
            self.description = description
            self.description_label.setText(description)
            
        if link_text is not None:
            self.link_text = link_text
            self.link_label.setText(link_text)
            
        if link_url is not None:
            self.link_url = link_url 
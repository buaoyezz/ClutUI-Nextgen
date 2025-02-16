from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QGraphicsDropShadowEffect, QHBoxLayout, QWidget
from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtGui import QColor, QDesktopServices
from core.font.font_manager import FontManager
from core.font.font_pages_manager import FontPagesManager
from core.log.log_manager import log
from core.utils.notif import Notification, NotificationType
from core.ui.card_shadow import CardShadow

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
        self.font_pages_manager = FontPagesManager()
        self.font_manager = FontManager()
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # 标题容器
        title_container = QHBoxLayout()
        title_container.setSpacing(8)
        
        # 标题图标
        self.icon_label = QLabel(self.font_manager.get_icon_text('article'))
        self.font_manager.apply_icon_font(self.icon_label, size=20)
        self.icon_label.setStyleSheet("""
            QLabel {
                color: #333333;
                background: transparent;
            }
        """)
        
        # 标题文字
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet("""
            QLabel {
                color: #333333;
                background: transparent;
            }
        """)
        self.font_pages_manager.apply_normal_style(self.title_label)
        
        # 添加图标和标题到容器
        title_container.addWidget(self.icon_label)
        title_container.addWidget(self.title_label)
        title_container.addStretch()
        
        # 描述文字
        self.description_label = QLabel(self.description)
        self.description_label.setStyleSheet("""
            QLabel {
                color: #666666;
                background: transparent;
            }
        """)
        self.font_pages_manager.apply_small_style(self.description_label)
        
        # 链接容器
        link_container = QHBoxLayout()
        link_container.setSpacing(4)
        
        # 创建一个单独的widget来包含链接文字和图标
        link_widget = QWidget()
        link_widget.setObjectName("linkWidget")
        link_widget_layout = QHBoxLayout(link_widget)
        link_widget_layout.setContentsMargins(8, 4, 8, 4)
        link_widget_layout.setSpacing(4)
        
        # 链接文字
        self.link_text_label = QLabel(self.link_text.replace('➡', ''))
        self.link_text_label.setObjectName("linkText")
        self.font_pages_manager.apply_small_style(self.link_text_label)
        
        # 链接箭头图标
        self.link_icon = QLabel(self.font_manager.get_icon_text('arrow_forward'))
        self.link_icon.setObjectName("linkIcon")
        self.font_manager.apply_icon_font(self.link_icon, size=16)
        
        # 添加到链接容器
        link_widget_layout.addWidget(self.link_text_label)
        link_widget_layout.addWidget(self.link_icon)
        
        # 直接添加到主布局，不使用额外的容器
        layout.addLayout(title_container)
        layout.addWidget(self.description_label, alignment=Qt.AlignRight)
        layout.addWidget(link_widget, alignment=Qt.AlignRight)
        
        # 卡片样式
        self.setStyleSheet("""
            LittleCard {
                background: white;
                border-radius: 15px;
                border: 1px solid #E0E0E0;
            }
            LittleCard:hover {
                border: 1px solid #2196F3;
            }
            QWidget#linkWidget {
                background: rgba(33, 150, 243, 0.08);
                border-radius: 4px;
            }
            #linkText, #linkIcon {
                color: #666666;
            }
            LittleCard:hover #linkText,
            LittleCard:hover #linkIcon {
                color: #2196F3;
            }
        """)
        
        # 添加阴影效果
        self.setGraphicsEffect(CardShadow.get_shadow(self))
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.title)
            
    def update_content(self, title=None, description=None, link_text=None, link_url=None):
        if title is not None:
            self.title = title
            self.title_label.setText(title)
            
        if description is not None:
            self.description = description
            self.description_label.setText(description)
            
        if link_text is not None:
            self.link_text = link_text
            self.link_text_label.setText(link_text)
            
        if link_url is not None:
            self.link_url = link_url 
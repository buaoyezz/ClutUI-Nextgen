from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout, QWidget
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QCursor
from core.font.font_manager import FontManager
from core.font.font_pages_manager import FontPagesManager
from core.ui.card_shadow import CardShadow
from core.animations.expandable_animation import ExpandableMixin

class ExpandableCard(QFrame, ExpandableMixin):
    clicked = Signal(str)
    item_clicked = Signal(str, str)  # 发送子项的标题和副标题
    
    def __init__(self, title="", subtitle="", parent=None):
        super().__init__(parent)
        self.title = title
        self.subtitle = subtitle
        
        self.font_manager = FontManager()
        self.font_pages_manager = FontPagesManager()
        
        self.setup_ui()
        
    def setup_ui(self):
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)
        
        # 标题容器
        self.header = QWidget()
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)
        
        # 标题图标
        self.icon_label = QLabel(self.font_manager.get_icon_text('article'))
        self.font_manager.apply_icon_font(self.icon_label, size=20)
        self.icon_label.setStyleSheet("""
            color: #333333;
            background: transparent;
        """)
        
        # 标题文本
        self.title_label = QLabel(self.title)
        self.font_pages_manager.apply_normal_style(self.title_label)
        self.title_label.setStyleSheet("""
            color: #333333;
            font-weight: 500;
            background: transparent;
        """)
        
        # 展开/收起图标
        self.expand_icon = QLabel(self.font_manager.get_icon_text('expand_more'))
        self.font_manager.apply_icon_font(self.expand_icon, size=20)
        self.expand_icon.setStyleSheet("""
            color: #666666;
            background: transparent;
        """)
        
        header_layout.addWidget(self.icon_label)
        header_layout.addWidget(self.title_label, 1)
        header_layout.addWidget(self.expand_icon)
        
        # 副标题
        self.subtitle_label = QLabel(self.subtitle)
        self.font_pages_manager.apply_small_style(self.subtitle_label)
        self.subtitle_label.setStyleSheet("""
            color: #666666;
            background: transparent;
        """)
        
        # 内容区域
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(28, 8, 0, 0)
        self.content_layout.setSpacing(8)
        self.content.setMaximumHeight(0)
        self.content.setStyleSheet("background: transparent;")
        
        layout.addWidget(self.header)
        layout.addWidget(self.subtitle_label)
        layout.addWidget(self.content)
        
        # 初始化动画
        self.init_expandable(self.content, self.expand_icon)
        
        # 卡片样式
        self.setStyleSheet("""
            ExpandableCard {
                background: #F8F9FA;
                border-radius: 12px;
                border: 1px solid #E0E0E0;
            }
            ExpandableCard:hover {
                border: 1px solid #2196F3;
            }
            QWidget {
                background: transparent;
            }
        """)
        
        # 添加阴影
        self.setGraphicsEffect(CardShadow.get_shadow(self))
        
        # 绑定点击事件
        self.header.mousePressEvent = self._handle_header_click
        
    def _handle_header_click(self, event):
        if event.button() == Qt.LeftButton:
            self.toggle_expand()
            
    def add_item(self, title, subtitle=""):
        """添加一个子项"""
        item = QWidget()
        item_layout = QHBoxLayout(item)
        item_layout.setContentsMargins(0, 0, 0, 0)
        item_layout.setSpacing(8)
        item.setStyleSheet("""
            QWidget {
                background: transparent;
            }
            QWidget:hover {
                background: rgba(33, 150, 243, 0.1);
                border-radius: 4px;
            }
        """)
        item.setCursor(QCursor(Qt.PointingHandCursor))
        
        # 子项图标
        icon = QLabel(self.font_manager.get_icon_text('subdirectory_arrow_right'))
        self.font_manager.apply_icon_font(icon, size=18)
        icon.setStyleSheet("""
            color: #666666;
            background: transparent;
        """)
        
        # 子项内容
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(2)
        content.setStyleSheet("background: transparent;")
        
        title_label = QLabel(title)
        self.font_pages_manager.apply_normal_style(title_label)
        title_label.setStyleSheet("""
            color: #333333;
            background: transparent;
        """)
        
        if subtitle:
            subtitle_label = QLabel(subtitle)
            self.font_pages_manager.apply_small_style(subtitle_label)
            subtitle_label.setStyleSheet("""
                color: #666666;
                background: transparent;
            """)
            content_layout.addWidget(subtitle_label)
            
        content_layout.addWidget(title_label)
        
        item_layout.addWidget(icon)
        item_layout.addWidget(content, 1)
        
        # 添加点击事件
        def item_clicked():
            self.item_clicked.emit(title, subtitle)
            
        item.mousePressEvent = lambda e: item_clicked() if e.button() == Qt.LeftButton else None
        
        self.content_layout.addWidget(item)
        return item 
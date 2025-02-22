from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPixmap
from core.font.font_manager import FontManager
from core.font.font_pages_manager import FontPagesManager
from core.ui.card_shadow import CardShadow

class LittleCard2(QFrame):
    clicked = Signal(str)
    
    def __init__(self, 
                 title="", 
                 label="",
                 action_text="配置档案",
                 parent=None):
        """
        创建一个小卡片组件2
        
        Args:
            title (str): 卡片标题
            label (str): 标签文字
            action_text (str): 操作按钮文字
            parent (QWidget): 父组件
        """
        super().__init__(parent)
        self.title = title
        self.label = label
        self.action_text = action_text
        
        # 创建字体管理器
        self.font_pages_manager = FontPagesManager()
        self.font_manager = FontManager()
        
        # 设置更柔和的阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(8)  # 更小的模糊半径
        shadow.setColor(QColor(0, 0, 0, 15))  # 非常轻的阴影
        shadow.setOffset(0, 1)  # 最小的垂直偏移
        self.setGraphicsEffect(shadow)
        
        self.setup_ui()
        
    def setup_ui(self):
        # 设置固定大小
        self.setFixedSize(220, 130)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        # 标题容器
        title_container = QHBoxLayout()
        title_container.setSpacing(8)
        
        # Logo图片
        self.logo_label = QLabel()
        logo_pixmap = QPixmap("./resources/logo.png")  # 加载logo图片
        scaled_logo = logo_pixmap.scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.logo_label.setPixmap(scaled_logo)
        self.logo_label.setFixedSize(20, 20)
        
        # 标题文字
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet("""
            QLabel {
                color: #333333;
                font-weight: bold;
                background: transparent;
            }
        """)
        self.font_pages_manager.apply_normal_style(self.title_label)
        
        title_container.addWidget(self.logo_label)
        title_container.addWidget(self.title_label)
        title_container.addStretch()
        
        # 标签容器
        label_container = QHBoxLayout()
        label_container.setSpacing(8)
        
        # 标签前的图标
        self.label_icon = QLabel(self.font_manager.get_icon_text('vertical_split'))
        self.font_manager.apply_icon_font(self.label_icon, size=16)
        self.label_icon.setStyleSheet("""
            QLabel {
                color: #666666;
                background: transparent;
            }
        """)
        
        # 标签文字
        self.label_text = QLabel(self.label)
        self.label_text.setStyleSheet("""
            QLabel {
                color: #666666;
                background: transparent;
            }
        """)
        self.font_pages_manager.apply_small_style(self.label_text)
        
        label_container.addWidget(self.label_icon)
        label_container.addWidget(self.label_text)
        label_container.addStretch()
        
        layout.addLayout(title_container)
        layout.addLayout(label_container)
        
        # 操作按钮容器
        action_container = QWidget()
        action_container.setObjectName("actionContainer")
        action_layout = QHBoxLayout(action_container)
        action_layout.setContentsMargins(8, 4, 8, 4)
        action_layout.setSpacing(4)
        
        # 操作文字
        self.action_label = QLabel(self.action_text)
        self.action_label.setObjectName("actionText")
        self.font_pages_manager.apply_small_style(self.action_label)
        
        # 箭头图标
        self.arrow_icon = QLabel(self.font_manager.get_icon_text('arrow_forward'))
        self.arrow_icon.setObjectName("arrowIcon")
        self.font_manager.apply_icon_font(self.arrow_icon, size=16)
        
        action_layout.addWidget(self.action_label)
        action_layout.addWidget(self.arrow_icon)
        
        layout.addWidget(action_container, alignment=Qt.AlignRight)
        
        # 更新卡片样式
        self.setStyleSheet("""
            LittleCard2 {
                background: white;
                border-radius: 12px;
                border: 1px solid rgba(0, 0, 0, 0.06);  /* 更淡的边框 */
                margin: 2px;  /* 为阴影留出空间 */
            }
            LittleCard2:hover {
                border: 1px solid #2196F3;
                background: white;
            }
            QWidget#actionContainer {
                background: rgba(33, 150, 243, 0.08);
                border-radius: 4px;
                padding: 4px 8px;
            }
            #actionText, #arrowIcon {
                color: #666666;
            }
            LittleCard2:hover #actionText,
            LittleCard2:hover #arrowIcon {
                color: #2196F3;
            }
        """)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.title)
            
    def update_content(self, title=None, label=None, action_text=None):
        if title is not None:
            self.title = title
            self.title_label.setText(title)
            
        if label is not None:
            self.label = label
            self.label_text.setText(label)
            
        if action_text is not None:
            self.action_text = action_text
            self.action_label.setText(action_text)

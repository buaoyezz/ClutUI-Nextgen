from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QGraphicsDropShadowEffect, QHBoxLayout, QWidget
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from core.font.font_manager import FontManager
from core.font.font_pages_manager import FontPagesManager
from core.log.log_manager import log
from core.utils.notif import Notification, NotificationType

class CardWhite(QFrame):
    clicked = Signal(str)
    action_clicked = Signal(str)
    
    def __init__(self, title="", description="", actions=None, parent=None):
        super().__init__(parent)
        self.title = title
        self.description = description
        self.actions = actions or []
        self.clicked_states = {}  # 添加状态记录
        
        self.font_pages_manager = FontPagesManager()
        self.font_manager = FontManager()
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)
        
        # 标题容器
        title_container = QHBoxLayout()
        title_container.setSpacing(12)
        
        # 添加右箭头装饰
        line_label = QLabel(self.font_manager.get_icon_text('chevron_right'))
        self.font_manager.apply_icon_font(line_label, size=20)
        line_label.setStyleSheet("""
            color: #2196F3;
            background: transparent;
        """)
        title_container.addWidget(line_label)
        
        # 标题文字
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet("""
            font-weight: 500;
            background: transparent;
        """)
        self.font_pages_manager.apply_normal_style(self.title_label)
        
        title_container.addWidget(self.title_label)
        title_container.addStretch()
        
        # 右侧操作按钮
        if "attachment" in [a.get('type', '') for a in self.actions]:
            attachment_btn = QLabel(self.font_manager.get_icon_text('attachment'))
            self.font_manager.apply_icon_font(attachment_btn, size=20)
            attachment_btn.setStyleSheet("""
                padding: 6px 10px;
                border-radius: 4px;
                background: rgba(33, 150, 243, 0.1);
                color: #2196F3;
            """)
            attachment_btn.setCursor(Qt.PointingHandCursor)  # 添加鼠标指针样式
            title_container.addWidget(attachment_btn)
        
        # 描述文字
        self.description_label = QLabel(self.description)
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("""
            background: transparent;
            line-height: 140%;
        """)
        self.description_label.setObjectName("description")
        self.font_pages_manager.apply_small_style(self.description_label)
        
        # 操作按钮容器
        action_container = QHBoxLayout()
        action_container.setSpacing(8)
        action_container.setContentsMargins(0, 8, 0, 0)
        
        # 默认的社交操作按钮
        default_actions = [
            {"icon": "thumb_up_outline", "icon_outline": "thumb_up", "text": "点赞"},
            {"icon": "bookmark_border", "icon_outline": "bookmark", "text": "收藏"},
            {"icon": "share", "icon_outline": "share", "text": "转发"}  # 添加 icon_outline 属性
        ]
        
        # 如果没有自定义操作，使用默认操作
        actions_to_use = self.actions if self.actions else default_actions
        
        for action in actions_to_use:
            if action.get('type') == 'attachment':
                continue
                
            action_widget = QWidget()
            action_widget.setObjectName("actionWidget")
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(8, 4, 8, 4)
            action_layout.setSpacing(6)

            # 操作图标 - 默认使用轮廓图标
            icon_name = action.get('icon_outline', 'link')  # 默认使用轮廓图标
            icon_label = QLabel(self.font_manager.get_icon_text(icon_name))
            self.font_manager.apply_icon_font(icon_label, size=16)
            icon_label.setObjectName("actionIcon")
            icon_label.setStyleSheet("color: rgba(0, 0, 0, 0.6);")
            action_layout.addWidget(icon_label)
            
            # 添加文字标签
            text_label = QLabel(action.get('text', ''))
            self.font_pages_manager.apply_small_style(text_label)
            text_label.setObjectName("actionText")
            text_label.setStyleSheet("color: rgba(0, 0, 0, 0.6);")  # 默认使用灰色
            action_layout.addWidget(text_label)

            # 保存按钮状态和引用
            action['icon_label'] = icon_label
            action['text_label'] = text_label
            self.clicked_states[action.get('text', '')] = False

            action_widget.mousePressEvent = lambda e, a=action: self._handle_action_click(a)
            action_container.addWidget(action_widget)
            
        action_container.addStretch()

        layout.addLayout(title_container)
        layout.addWidget(self.description_label)
        layout.addLayout(action_container)
        
        # 卡片样式
        self.setStyleSheet("""
            CardWhite {
                background: #FFFFFF;
                border-radius: 8px;
                border: 1px solid #E0E0E0;
            }
            CardWhite:hover {
                border: 1px solid #2196F3;
                background: #FFFFFF;
            }
            
            QLabel {
                color: #333333;
            }
            
            #description {
                color: rgba(0, 0, 0, 0.6);
            }
            
            QWidget#actionWidget {
                background: transparent;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QWidget#actionWidget:hover {
                background: rgba(33, 150, 243, 0.1);
            }
            #actionText, #actionIcon {
                color: rgba(0, 0, 0, 0.6);
            }
            QWidget#actionWidget:hover #actionText,
            QWidget#actionWidget:hover #actionIcon {
                color: #2196F3;
            }
        """)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
    def _handle_action_click(self, action):
        text = action.get('text', '')
        if text in ['点赞', '收藏']:
            self.clicked_states[text] = not self.clicked_states[text]
            
            if self.clicked_states[text]:
                action['icon_label'].setText(self.font_manager.get_icon_text(action.get('icon_outline')))
                action['icon_label'].setStyleSheet("color: #2196F3;")
                action['text_label'].setStyleSheet("color: #2196F3;")
            else:
                # 未选中状态使用轮廓图标，灰色
                action['icon_label'].setText(self.font_manager.get_icon_text(action.get('icon_outline')))
                action['icon_label'].setStyleSheet("color: rgba(0, 0, 0, 0.6);")
                action['text_label'].setStyleSheet("color: rgba(0, 0, 0, 0.6);")
        
        self.action_clicked.emit(text)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.title)
            
    def update_content(self, title=None, description=None, actions=None):
        if title is not None:
            self.title = title
            self.title_label.setText(title)
            
        if description is not None:
            self.description = description
            self.description_label.setText(description)
            
        if actions is not None:
            self.actions = actions
            
        # 更新卡片样式
        self.setStyleSheet("""
            CardWhite {
                background: #FFFFFF;
                border-radius: 8px;
                border: 1px solid #E0E0E0;
            }
            CardWhite:hover {
                border: 1px solid #2196F3;
                background: #FFFFFF;
            }
            
            QLabel {
                color: #333333;
            }
            
            #description {
                color: rgba(0, 0, 0, 0.6);
            }
            
            QWidget#actionWidget {
                background: transparent;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QWidget#actionWidget:hover {
                background: rgba(33, 150, 243, 0.1);
            }
            #actionText, #actionIcon {
                color: rgba(0, 0, 0, 0.6);
            }
            QWidget#actionWidget:hover #actionText,
            QWidget#actionWidget:hover #actionIcon {
                color: #2196F3;
            }
        """)
        
        # 重新设置布局
        self.setup_ui() 
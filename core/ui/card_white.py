from PySide6.QtWidgets import (QFrame, QLabel, QVBoxLayout, QGraphicsDropShadowEffect, 
                             QHBoxLayout, QWidget, QPushButton, QSizePolicy)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from core.font.font_manager import FontManager
from core.font.font_pages_manager import FontPagesManager
from core.log.log_manager import log
from core.utils.notif import Notification, NotificationType
from core.i18n import i18n

class CardWhite(QFrame):
    clicked = Signal(str)
    action_clicked = Signal(str)
    
    def __init__(self, title="", description="", actions=None, parent=None):
        super().__init__(parent)
        self.title = title
        self.description = description
        self.actions = [] if actions is False else (actions or [])
        self.clicked_states = {}
        self.is_expanded = False 
        self.show_actions = actions is not False
        
        self.font_pages_manager = FontPagesManager()
        self.font_manager = FontManager()
        
        self.setup_ui()
        
        # 连接语言变更信号
        i18n.language_changed.connect(self.update_text)
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)
        
        # 标题容器
        title_container = QHBoxLayout()
        title_container.setSpacing(8)
        
        # 添加右箭头装饰
        line_label = QLabel(self.font_manager.get_icon_text('chevron_right'))
        self.font_manager.apply_icon_font(line_label, size=18)
        line_label.setStyleSheet("""
            color: #2196F3;
            background: transparent;
        """)
        line_label.setFixedWidth(18)
        title_container.addWidget(line_label)
        
        # 标题文字
        self.title_label = QLabel()
        self.title_label.setWordWrap(True)
        self.title_label.setTextFormat(Qt.PlainText)
        self.font_pages_manager.apply_normal_style(self.title_label)
        self.title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        
        # 设置标题
        title_text = self.format_title(self.title)
        self.title_label.setText(title_text)
        self.title_label.setStyleSheet("""
            font-weight: 500;
            background: transparent;
            padding: 0px;
            letter-spacing: 0.3px;
            min-height: 20px;
        """)
        
        title_container.addWidget(self.title_label, 1)
        
        # 右侧操作按钮
        if self.show_actions and "attachment" in [a.get('type', '') for a in self.actions]:
            attachment_btn = QLabel(self.font_manager.get_icon_text('attachment'))
            self.font_manager.apply_icon_font(attachment_btn, size=18)
            attachment_btn.setStyleSheet("""
                padding: 4px 8px;
                border-radius: 4px;
                background: rgba(33, 150, 243, 0.1);
                color: #2196F3;
            """)
            attachment_btn.setCursor(Qt.PointingHandCursor)
            title_container.addWidget(attachment_btn)
        
        # 描述文字容器
        description_container = QWidget()
        description_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        self.description_layout = QVBoxLayout(description_container)
        self.description_layout.setContentsMargins(26, 4, 0, 0)
        self.description_layout.setSpacing(4)
        
        # 描述文字
        self.description_label = QLabel(self.description)
        self.description_label.setWordWrap(True)
        self.description_label.setTextFormat(Qt.PlainText)
        self.font_pages_manager.apply_normal_style(self.description_label)
        self.description_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        self.description_label.setStyleSheet("""
            background: transparent;
            padding: 0px;
            letter-spacing: 0.3px;
            color: #666666;
            min-height: 20px;
        """)
        
        # 添加省略号处理
        if not self.is_expanded:
            metrics = self.description_label.fontMetrics()
            elided_text = metrics.elidedText(self.description, Qt.ElideRight, self.width() - 80)
            self.description_label.setText(elided_text)
        else:
            self.description_label.setText(self.description)
        
        # 展开/收起按钮容器
        expand_container = QWidget()
        expand_layout = QHBoxLayout(expand_container)
        expand_layout.setContentsMargins(0, 0, 0, 0)
        expand_layout.setSpacing(4)
        
        # 展开图标
        self.expand_icon = QLabel(self.font_manager.get_icon_text('expand_more'))
        self.font_manager.apply_icon_font(self.expand_icon, size=16)
        self.expand_icon.setStyleSheet("color: #2196F3;")
        
        # 展开文字
        self.expand_button = QPushButton("展开")
        self.font_pages_manager.apply_small_style(self.expand_button)
        self.expand_button.setStyleSheet("""
            QPushButton {
                border: none;
                color: #2196F3;
                background: transparent;
                text-align: left;
                padding: 0;
            }
            QPushButton:hover {
                color: #1976D2;
            }
        """)
        self.expand_button.clicked.connect(self.toggle_expand)
        
        expand_layout.addWidget(self.expand_icon)
        expand_layout.addWidget(self.expand_button)
        expand_layout.addStretch()
        
        self.description_layout.addWidget(self.description_label)
        self.description_layout.addWidget(expand_container)
        expand_container.hide()
        self.expand_container = expand_container
        
        # 检查是否需要显示展开按钮
        self.check_description_length()
        
        # 添加主要布局
        layout.addLayout(title_container)
        layout.addWidget(description_container)
        
        # 设置卡片大小策略
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        
        # 只在需要时添加操作按钮
        if self.show_actions:
            # 操作按钮容器
            action_container = QHBoxLayout()
            action_container.setSpacing(8)
            action_container.setContentsMargins(0, 8, 0, 0)
            
            # 默认的社交操作按钮
            default_actions = [
                {"icon": "thumb_up_outline", "icon_outline": "thumb_up", "text": i18n.get_text("like"), "key": "like"},
                {"icon": "bookmark_border", "icon_outline": "bookmark", "text": i18n.get_text("favorite"), "key": "favorite"},
                {"icon": "chat_bubble_outline", "icon_outline": "chat_bubble", "text": i18n.get_text("comment"), "key": "comment"},
                {"icon": "share", "icon_outline": "share", "text": i18n.get_text("share"), "key": "share"}
            ]
            
            # 如果没有自定义操作，使用默认操作
            self.actions_to_use = self.actions if self.actions else default_actions
            
            for action in self.actions_to_use:
                if action.get('type') == 'attachment':
                    continue
                    
                action_widget = QWidget()
                action_widget.setObjectName("actionWidget")
                action_layout = QHBoxLayout(action_widget)
                action_layout.setContentsMargins(8, 4, 8, 4)
                action_layout.setSpacing(6)

                icon_name = action.get('icon_outline', 'link')
                icon_label = QLabel(self.font_manager.get_icon_text(icon_name))
                self.font_manager.apply_icon_font(icon_label, size=16)
                icon_label.setObjectName("actionIcon")
                icon_label.setStyleSheet("color: rgba(0, 0, 0, 0.6);")
                action_layout.addWidget(icon_label)
                
                text_label = QLabel(action.get('text', ''))
                self.font_pages_manager.apply_small_style(text_label)
                text_label.setObjectName("actionText")
                text_label.setStyleSheet("color: rgba(0, 0, 0, 0.6);")
                action_layout.addWidget(text_label)

                action['icon_label'] = icon_label
                action['text_label'] = text_label
                action['key'] = action.get('key', action.get('text', ''))
                self.clicked_states[action['key']] = False

                action_widget.mousePressEvent = lambda e, a=action: self._handle_action_click(a)
                action_container.addWidget(action_widget)
                
            action_container.addStretch()
            layout.addLayout(action_container)
        
        # 卡片样式
        self.setStyleSheet("""
            CardWhite {
                background: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E0E0E0;
                max-width: 850px;
                min-height: 20px;
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
            
            * {
                border-radius: 12px;
            }
            
            QWidget#actionWidget {
                border-radius: 4px;
            }
        """)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
    def _handle_action_click(self, action):
        key = action.get('key', '')
        if key in ['like', 'favorite']:  # 使用key而不是文本来判断
            self.clicked_states[key] = not self.clicked_states[key]
            
            if self.clicked_states[key]:
                action['icon_label'].setText(self.font_manager.get_icon_text(action.get('icon_outline')))
                action['icon_label'].setStyleSheet("color: #2196F3;")
                action['text_label'].setStyleSheet("color: #2196F3;")
            else:
                action['icon_label'].setText(self.font_manager.get_icon_text(action.get('icon_outline')))
                action['icon_label'].setStyleSheet("color: rgba(0, 0, 0, 0.6);")
                action['text_label'].setStyleSheet("color: rgba(0, 0, 0, 0.6);")
        
        self.action_clicked.emit(key)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.title)
            
    def update_content(self, title=None, description=None, actions=None):
        if title is not None:
            self.title = title
            self.title_label.setText(self.format_title(title))
            
        if description is not None:
            self.description = description
            self.description_label.setText(description)
            self.check_description_length()
            
        if actions is not None:
            self.actions = actions
            
        # 更新卡片样式
        self.setStyleSheet("""
            CardWhite {
                background: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E0E0E0;
                max-width: 850px;
                min-height: 20px;
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
            
            * {
                border-radius: 12px;
            }
            
            QWidget#actionWidget {
                border-radius: 4px;
            }
        """)
        
    def check_description_length(self):
        metrics = self.description_label.fontMetrics()
        text = self.description
        rect = metrics.boundingRect(0, 0, self.description_label.maximumWidth(), 
                                  1000, Qt.TextWordWrap, text)
        # da gai 2 hang
        if rect.height() > 36:
            self.expand_container.show()
            elided_text = metrics.elidedText(text, Qt.ElideRight, 750)
            self.description_label.setText(elided_text)
        else:
            self.expand_container.hide()
            self.description_label.setText(text)
            
    def toggle_expand(self):
        self.is_expanded = not self.is_expanded
        if self.is_expanded:
            self.description_label.setMaximumHeight(16777215)
            formatted_text = self.format_text_with_breaks(self.description, 80)
            self.description_label.setText(formatted_text)
            self.expand_button.setText(i18n.get_text("collapse"))
            self.expand_icon.setText(self.font_manager.get_icon_text('expand_less'))
        else:
            self.description_label.setMaximumHeight(48)
            metrics = self.description_label.fontMetrics()
            elided_text = metrics.elidedText(self.description, Qt.ElideRight, 750)
            self.description_label.setText(elided_text)
            self.expand_button.setText(i18n.get_text("expand"))
            self.expand_icon.setText(self.font_manager.get_icon_text('expand_more'))

    def format_text_with_breaks(self, text, max_length):
        if not text:
            return text
            
        # split
        paragraphs = text.split('\n')
        formatted_paragraphs = []
        
        for paragraph in paragraphs:
            # use punctuation to split
            segments = []
            current_segment = ""
            
            for char in paragraph:
                current_segment += char
                # use punctuation to split, but keep punctuation in current segment
                if char in '，。！？；：、,.!?;:':
                    segments.append(current_segment)
                    current_segment = ""
            
            if current_segment:
                segments.append(current_segment)
            
            # combine semantic segments, control line length
            current_line = ""
            formatted_lines = []
            
            for segment in segments:
                # calculate current segment length (chinese character count 2, other count 1)
                segment_length = sum(2 if self._is_chinese_char(c) else 1 for c in segment)
                current_line_length = sum(2 if self._is_chinese_char(c) else 1 for c in current_line)
                
                # if current line plus new segment is too long, handle line break
                if current_line_length + segment_length > max_length and current_line:
                    formatted_lines.append(current_line.strip())
                    current_line = segment
                else:
                    current_line += segment
            
            if current_line:
                formatted_lines.append(current_line.strip())
            
            # combine processed lines into paragraph
            formatted_paragraphs.append('\n'.join(formatted_lines))
        
        # combine all paragraphs, keep empty line between paragraphs
        return '\n\n'.join(formatted_paragraphs)

    def _is_chinese_char(self, char):
        return '\u4e00' <= char <= '\u9fff'

    def format_title(self, title):
        if not title:
            return title
            
        # return processed title, remove extra spaces and line breaks
        return ' '.join(title.split())
        
    def update_text(self):
        if self.expand_button:
            self.expand_button.setText(i18n.get_text("expand" if not self.is_expanded else "collapse"))
            
        # 更新所有操作按钮的文本
        if hasattr(self, 'actions_to_use'):
            for action in self.actions_to_use:
                if 'text_label' in action and 'key' in action:
                    action['text_label'].setText(i18n.get_text(action['key']))
        
    def add_custom_widget(self, widget):
        """添加自定义组件到卡片中"""
        if hasattr(self, 'description_layout'):
            # 将组件插入到描述文字和展开按钮之间
            index = self.description_layout.indexOf(self.description_label) + 1
            self.description_layout.insertWidget(index, widget)
        
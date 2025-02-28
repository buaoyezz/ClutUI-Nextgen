from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QGraphicsDropShadowEffect, QSizePolicy, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from core.font.font_pages_manager import FontPagesManager

class TransportCard(QFrame):
    def __init__(self, title="", description="", parent=None):
        super().__init__(parent)
        self.title = title
        self.description = description
        self.font_manager = FontPagesManager()
        self.setup_ui()
        
    def setup_ui(self):
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)  # 增加间距
        
        # 标题
        self.title_label = QLabel(self.title)
        self.font_manager.apply_subtitle_style(self.title_label)
        self.title_label.setStyleSheet("""
            QLabel {
                color: #1F2937;
                font-size: 16px;
                font-weight: 500;
                letter-spacing: 0.3px;
                padding: 4px 0;
            }
        """)
        self.title_label.setWordWrap(True)
        self.title_label.setTextFormat(Qt.PlainText)
        # 设置标题大小策略
        self.title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        self.title_label.setMinimumHeight(20)
        
        # 描述
        self.description_label = QLabel(self.description)
        self.font_manager.apply_normal_style(self.description_label)
        self.description_label.setWordWrap(True)
        self.description_label.setTextFormat(Qt.PlainText)
        self.description_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 13px;
                line-height: 1.6;
                letter-spacing: 0.2px;
                padding: 4px 0;
            }
        """)
        # 设置描述大小策略
        self.description_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        self.description_label.setMinimumHeight(20)
        
        # 创建一个容器用于自定义控件
        self.custom_widget_container = QWidget()
        self.custom_widget_layout = QVBoxLayout(self.custom_widget_container)
        self.custom_widget_layout.setContentsMargins(0, 4, 0, 0)
        self.custom_widget_layout.setSpacing(8)
        self.custom_widget_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        
        # 添加到布局
        layout.addWidget(self.title_label)
        layout.addWidget(self.description_label)
        layout.addWidget(self.custom_widget_container)
        
        # 设置卡片样式
        self.setStyleSheet("""
            TransportCard {
                background: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E0E0E0;
                max-width: 850px;
                min-height: 20px;
            }
            TransportCard:hover {
                border: 1px solid #E0E0E0;
                background: #FFFFFF;
            }
        """)
        
        # 设置卡片大小策略
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 1)
        self.setGraphicsEffect(shadow)
        
    def add_custom_widget(self, widget):
        """添加自定义控件到卡片"""
        self.custom_widget_layout.addWidget(widget)
        
    def update_title(self, title):
        """更新标题文本"""
        self.title = title
        self.title_label.setText(title)
        self.title_label.adjustSize()
        
    def update_description(self, description):
        """更新描述文本"""
        self.description = description
        self.description_label.setText(description)
        self.description_label.adjustSize()
        
    def set_content_margins(self, left, top, right, bottom):
        """设置内容边距"""
        self.layout().setContentsMargins(left, top, right, bottom)
        
    def set_spacing(self, spacing):
        """设置间距"""
        self.layout().setSpacing(spacing)
        
    def format_text_with_breaks(self, text, max_length):
        """格式化文本，添加适当的换行"""
        if not text:
            return text
            
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            word_length = len(word)
            if current_length + word_length + len(current_line) <= max_length:
                current_line.append(word)
                current_length += word_length
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_length = word_length
                
        if current_line:
            lines.append(' '.join(current_line))
            
        return '\n'.join(lines) 
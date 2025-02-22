from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QScrollArea)
from PySide6.QtCore import Qt
from core.ui.card_white import CardWhite
from core.ui.messagebox_white import MessageBoxWhite, MessageButton
from core.font.font_pages_manager import FontPagesManager
from core.animations.scroll_hide_show import ScrollBarAnimation
from core.ui.notice import Notice

class ExamplePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.font_manager = FontPagesManager()
        self.setup_ui()
        
    def setup_ui(self):
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建通知组件
        notice_container = QWidget()
        notice_layout = QVBoxLayout(notice_container)
        notice_layout.setContentsMargins(20, 20, 20, 0)
        
        self.notice = Notice(message="很一个通知很一个通知很一个通知很一个通知很一个通知很一个通知很一个通知很一个通知很一个通知很一个通知很一个通知很一个通知很一个通知很一个通知很一个通知很一个通知", icon="info")
        notice_layout.addWidget(self.notice)
        main_layout.addWidget(notice_container)
        
        # 显示通知
        self.notice.show_message(duration=0)  # duration=0 表示不自动消失
        
        # 创建滚动区域容器
        scroll_container = QWidget()
        scroll_container.setObjectName("scrollContainer")
        scroll_container_layout = QVBoxLayout(scroll_container)
        scroll_container_layout.setContentsMargins(0, 0, 0, 0)
        
        # 设置滚动区域
        scroll_area = QScrollArea()
        self.scroll_area = scroll_area
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setObjectName("scrollArea")
        
        # 设置滚动条动画
        self.scroll_animation = ScrollBarAnimation(scroll_area.verticalScrollBar())
        scroll_area.verticalScrollBar().valueChanged.connect(
            self.scroll_animation.show_temporarily
        )
        
        # 内容容器
        container = QWidget()
        container.setObjectName("container")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 原有的按钮和卡片内容
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        # 基础消息框按钮
        basic_btn = QPushButton("基础消息框")
        self.font_manager.apply_normal_style(basic_btn)
        basic_btn.setFixedSize(120, 36)
        basic_btn.clicked.connect(self.show_basic_message)
        
        # 确认消息框按钮
        confirm_btn = QPushButton("确认消息框")
        self.font_manager.apply_normal_style(confirm_btn)
        confirm_btn.setFixedSize(120, 36)
        confirm_btn.clicked.connect(self.show_confirm_message)
        
        # 自定义消息框按钮
        custom_btn = QPushButton("自定义消息框")
        self.font_manager.apply_normal_style(custom_btn)
        custom_btn.setFixedSize(120, 36)
        custom_btn.clicked.connect(self.show_custom_message)

        button_layout.addWidget(basic_btn)
        button_layout.addWidget(confirm_btn)
        button_layout.addWidget(custom_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        text = """在PySide6开发中，文本自动换行和图标管理是两个常见的UI优化问题。本文将从以下几个方面详细讲解实现步骤：首先，我们需要使用QLabel的setWordWrap和setMaximumWidth属性来实现基础的文本换行功能。其次，通过自定义的format_text_with_breaks方法，我们可以在指定字符数后强制换行，避免单行文本过长，超出屏幕导致的观感不协调。对于图标，我采用了FontManager类来统一管理Material Icons字体图标
在处理长文本显示时，我实现了展开/收起功能，默认显示两行文本并在末尾显示省略号，用户点击展开后可以查看完整内容。这样有利于软件的观感，而不是一大篇文章，对于文本宽度控制，我通过setMaximumWidth和elideText等方法确保文本不会超出卡片边界。
最后，我们还优化了卡片的视觉效果，添加了阴影、圆角和悬浮状态"""
        
        info_card = CardWhite(
            title="我是帖子Title",
            description="简单的提示消息,只包含一个确定按钮",
        )
        
        confirm_card = CardWhite(
            title="我是帖子Title",
            description="包含确认和取消按钮,用于需要用户确认的操作",
        )
        
        custom_card = CardWhite(
            title="论我是如何将本卡片的自动换行和图标完善的？在Pyside6中实现这些的步骤总共有哪些？过长的言论会不会飘出屏幕？这些都是很好的问题，本篇文章将详细描述",
            description=text
        )
        
        layout.addWidget(info_card)
        layout.addWidget(confirm_card)
        layout.addWidget(custom_card)
        layout.addStretch()
        
        # 设置滚动区域的内容
        scroll_area.setWidget(container)
        scroll_container_layout.addWidget(scroll_area)
        
        # 将滚动容器添加到主布局
        main_layout.addWidget(scroll_container)
        
        # 设置页面样式
        self.setStyleSheet("""
            QWidget#scrollContainer {
                background: transparent;
                margin: 0px 20px;
            }
            
            QScrollArea#scrollArea {
                background: transparent;
                border: none;
            }
            
            QWidget#container {
                background: #F8F9FA;
            }
            
            QPushButton {
                background: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
            }
            
            QPushButton:hover {
                background: #1E88E5;
            }
            
            QPushButton:pressed {
                background: #1976D2;
            }
            
            QScrollBar:vertical {
                background: transparent;
                width: 8px;
                margin: 4px 4px 4px 4px;
            }
            
            QScrollBar::handle:vertical {
                background: #C0C0C0;
                border-radius: 4px;
                min-height: 30px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: #A0A0A0;
            }
            
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """)

    def show_basic_message(self):
        message_box = MessageBoxWhite(
            title="提示",
            message="这是一个基础消息框示例",
            buttons=[MessageButton("确定", "primary")],
            icon="info",
            parent=self
        )
        self._show_message_box(message_box)

    def show_confirm_message(self):
        buttons = [
            MessageButton("取消", "default", "cancel"),
            MessageButton("确定", "primary", "confirm")
        ]
        message_box = MessageBoxWhite(
            title="确认操作",
            message="确定要执行此操作吗？",
            buttons=buttons,
            icon="help",
            parent=self
        )
        self._show_message_box(message_box)

    def show_custom_message(self):
        buttons = [
            MessageButton("取消", "default", "cancel"),
            MessageButton("删除", "danger", "delete"),
            MessageButton("保存", "primary", "save")
        ]
        message_box = MessageBoxWhite(
            title="自定义消息框",
            message="这是一个自定义按钮样式和返回值的消息框示例",
            buttons=buttons,
            icon="warning",
            parent=self
        )
        self._show_message_box(message_box)

    def _show_message_box(self, message_box):
        message_box.setFixedWidth(360)
        message_box.move(
            (self.width() - message_box.width()) // 2,
            (self.height() - message_box.height()) // 2
        )
        message_box.button_clicked.connect(self.handle_message_box_click)
        message_box.show()

    def handle_message_box_click(self, button):
        action_map = {
            "confirm": "确认操作",
            "cancel": "取消操作",
            "delete": "删除操作",
            "save": "保存操作"
        }
        print(f"用户点击了: {action_map.get(button.return_value, button.text)}")

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from core.ui.card_white import CardWhite
from core.ui.messagebox_white import MessageBoxWhite, MessageButton
from core.font.font_pages_manager import FontPagesManager

class ExamplePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.font_manager = FontPagesManager()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 添加消息框示例按钮组
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
        
        # 创建示例卡片
        info_card = CardWhite(
            title="基础消息框",
            description="简单的提示消息,只包含一个确定按钮"
        )
        
        confirm_card = CardWhite(
            title="确认消息框",
            description="包含确认和取消按钮,用于需要用户确认的操作"
        )
        
        custom_card = CardWhite(
            title="自定义消息框",
            description="支持自定义按钮样式、图标和返回值,可以处理更复杂的交互"
        )
        
        layout.addWidget(info_card)
        layout.addWidget(confirm_card)
        layout.addWidget(custom_card)
        layout.addStretch()
        
        # 设置页面样式
        self.setStyleSheet("""
            ExamplePage {
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

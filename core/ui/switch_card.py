from PySide6.QtWidgets import QHBoxLayout, QLabel
from core.ui.transportcard import TransportCard
from core.ui.switch import QSwitch
from core.font.font_pages_manager import FontPagesManager

class SwitchCard(TransportCard):
    def __init__(self, title="", description="", switch_text="", parent=None):
        super().__init__(title, description, parent)
        self.switch_text = switch_text
        self.font_manager = FontPagesManager()
        self.setup_switch()
        
    def setup_switch(self):
        # 创建开关布局
        switch_layout = QHBoxLayout()
        switch_layout.setContentsMargins(24, 0, 24, 20)
        
        # 开关文本标签
        self.switch_label = QLabel(self.switch_text)
        self.font_manager.apply_normal_style(self.switch_label)
        
        # 创建开关
        self.switch = QSwitch()
        
        # 添加到布局
        switch_layout.addWidget(self.switch_label)
        switch_layout.addWidget(self.switch)
        switch_layout.addStretch()
        
        # 将开关布局添加到卡片
        self.layout().addLayout(switch_layout)
        
    def set_checked(self, checked):
        self.switch.setChecked(checked)
        
    def is_checked(self):
        return self.switch.isChecked()
        
    def connect_state_changed(self, callback):
        self.switch.stateChanged.connect(callback)
        
    def update_switch_text(self, text):
        self.switch_text = text
        self.switch_label.setText(text) 
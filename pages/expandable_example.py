from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QHBoxLayout, QLabel, QPushButton
from core.ui.expandable_card import ExpandableCard
from core.utils.notif import Notification, NotificationType, show_info
from core.ui.scroll_style import ScrollStyle
from core.ui.progress_bar import ProgressBar
from PySide6.QtCore import QTimer

class ExpandableExamplePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
        # 创建定时器用于动态更新进度
        self.progress_timer = QTimer(self)
        self.progress_timer.timeout.connect(self.update_progress)
        self.current_progress = 0
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # 设置全局 Label 样式
        self.setStyleSheet("""
            QLabel {
                color: #333333;
                background: transparent;
                font-size: 14px;
                letter-spacing: 0.3px;
            }
            QLabel[class="title"] {
                font-size: 16px;
                font-weight: 500;
                color: #1F2937;
            }
            QLabel[class="description"] {
                font-size: 13px;
                color: #666666;
            }
            QLabel[class="progress"] {
                color: #666666;
                font-size: 13px;
                letter-spacing: 0.2px;
            }
        """)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            QScrollArea > QWidget > QWidget {{
                background: transparent;
            }}
            QWidget {{
                border-radius: 8px;
            }}
            {ScrollStyle.get_style()}
        """)
        
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(16)
        
        # 进度条示例卡片
        progress_card = ExpandableCard("进度条示例", "展示不同状态的进度条")
        
        # 创建进度条容器
        progress_container = QWidget()
        progress_layout = QVBoxLayout(progress_container)
        progress_layout.setContentsMargins(12, 8, 12, 8)
        progress_layout.setSpacing(16)
        
        # 添加进度条
        self.progress1 = ProgressBar()
        self.progress2 = ProgressBar()
        self.progress3 = ProgressBar()
        self.dynamic_progress = ProgressBar()  # 动态进度条
        
        # 创建进度条布局
        for progress, value, text in [
            (self.progress1, 30, "基础进度展示 - 30%"),
            (self.progress2, 60, "中等进度展示 - 60%"),
            (self.progress3, 90, "高进度展示 - 90%")
        ]:
            item_widget = QWidget()
            item_layout = QVBoxLayout(item_widget)
            item_layout.setContentsMargins(0, 0, 0, 8)
            
            label = QLabel(text)
            label.setStyleSheet("color: #666666; font-size: 13px;")
            
            item_layout.addWidget(label)
            item_layout.addWidget(progress)
            progress_layout.addWidget(item_widget)
            progress.setProgress(value)
            
        # 添加动态进度条
        dynamic_widget = QWidget()
        dynamic_layout = QVBoxLayout(dynamic_widget)
        dynamic_layout.setContentsMargins(0, 0, 0, 8)
        
        dynamic_header = QWidget()
        dynamic_header_layout = QHBoxLayout(dynamic_header)
        dynamic_header_layout.setContentsMargins(0, 0, 0, 0)
        
        dynamic_label = QLabel("动态进度展示")
        dynamic_label.setStyleSheet("color: #666666; font-size: 13px;")
        
        start_button = QPushButton("开始")
        start_button.setFixedWidth(60)
        start_button.setStyleSheet("""
            QPushButton {
                background: #B39DDB;
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: #9575CD;
            }
            QPushButton:pressed {
                background: #7E57C2;
            }
        """)
        start_button.clicked.connect(self.toggle_progress)
        self.start_button = start_button
        
        dynamic_header_layout.addWidget(dynamic_label)
        dynamic_header_layout.addWidget(start_button)
        
        dynamic_layout.addWidget(dynamic_header)
        dynamic_layout.addWidget(self.dynamic_progress)
        progress_layout.addWidget(dynamic_widget)
        
        progress_layout.addStretch()
        progress_card.add_item("进度条展示", "点击查看不同状态的进度条")
        progress_card.item_clicked.connect(lambda title, subtitle: self.handle_progress_click(progress_container))
        container_layout.addWidget(progress_card)
        
        # 开发文档卡片
        card1 = ExpandableCard("开发文档", "查看项目相关的开发文档")
        card1.add_item("PySide6 文档", "Qt for Python 官方文档")
        card1.add_item("Python 文档", "Python 语言官方文档")
        card1.add_item("Material Design", "Google Material Design 设计规范")
        card1.item_clicked.connect(self.handle_doc_click)
        container_layout.addWidget(card1)
        
        # 项目配置卡片
        card2 = ExpandableCard("项目配置", "管理项目的基本配置")
        card2.add_item("基础设置", "修改项目的基本参数")
        card2.add_item("主题设置", "自定义界面主题风格")
        card2.add_item("语言设置", "切换界面显示语言")
        card2.item_clicked.connect(self.handle_settings_click)
        container_layout.addWidget(card2)
        
        # 系统日志卡片
        card3 = ExpandableCard("系统日志", "查看系统运行日志")
        card3.add_item("运行日志", "应用程序运行日志")
        card3.add_item("错误日志", "系统错误和异常记录")
        card3.add_item("操作日志", "用户操作历史记录")
        card3.item_clicked.connect(self.handle_log_click)
        container_layout.addWidget(card3)
        
        container_layout.addStretch()
        scroll_area.setWidget(container)
        layout.addWidget(scroll_area)
        
        self.setStyleSheet("""
            QWidget {
                background: #F8F9FA;
            }
            ExpandableCard {
                background: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                margin: 4px;
            }
            ExpandableCard:hover {
                border-color: #BDBDBD;
                background: #FAFAFA;
            }
        """)
        
    def handle_doc_click(self, title, subtitle):
        Notification(
            text=f"正在打开{title} - {subtitle}",
            type=NotificationType.TIPS,
            duration=2000
        ).show_notification()
        
    def handle_settings_click(self, title, subtitle):
        Notification(
            text=f"正在打开{title}页面 - {subtitle}",
            type=NotificationType.INFO,
            duration=2000
        ).show_notification()
        
    def handle_log_click(self, title, subtitle):
        show_info(f"正在查看{title} - {subtitle}", duration=2000)
        
    def handle_progress_click(self, widget):
        if widget.isVisible():
            widget.hide()
        else:
            widget.show()
        
    def toggle_progress(self):
        if self.progress_timer.isActive():
            self.progress_timer.stop()
            self.start_button.setText("开始")
            self.current_progress = 0
            self.dynamic_progress.setProgress(0, animated=False)
        else:
            self.current_progress = 0
            self.dynamic_progress.setProgress(0, animated=False)
            self.progress_timer.start(100)  # 每100ms更新一次
            self.start_button.setText("重置")
            
    def update_progress(self):
        if self.current_progress >= 100:
            self.progress_timer.stop()
            self.start_button.setText("开始")
            return
            
        self.current_progress = min(self.current_progress + 2, 100)  # 每次增加2%，最大不超过100%
        self.dynamic_progress.setProgress(self.current_progress, animated=True) 
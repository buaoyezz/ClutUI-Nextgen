from PySide6.QtWidgets import QStackedWidget, QPushButton, QVBoxLayout, QWidget
from PySide6.QtCore import Qt
from pages.quick_start import QuickStartPage
from pages.about_page import AboutPage
from pages.log_page import LogPage
from core.animations.animation_manager import AnimationManager
from core.log.log_manager import log

class PagesManager:
    def __init__(self):
        # 基础组件初始化
        self.stacked_widget = QStackedWidget()
        self.pages = {}
        self.buttons = {}
        self.current_page = None
        
        # 创建动画管理器
        self.animation_manager = AnimationManager()
        
        # 创建页面实例
        self.quick_start_page = QuickStartPage()
        self.about_page = AboutPage()
        self.log_page = LogPage()
        # 初始化侧边栏
        self.sidebar = QWidget()
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(10, 10, 10, 10)
        self.sidebar_layout.setSpacing(2)
        
        # 创建并存储按钮
        self.buttons = {
            "快速开始": self.create_sidebar_button("快速开始"),
            "日志": self.create_sidebar_button("日志"),
            "关于": self.create_sidebar_button("关于")
        }
        
        # 添加按钮到布局
        self.sidebar_layout.addWidget(self.buttons["快速开始"])
        self.sidebar_layout.addStretch(1)
        self.sidebar_layout.addWidget(self.buttons["日志"])
        self.sidebar_layout.addWidget(self.buttons["关于"])
        
        # 添加页面映射
        self.pages = {
            "快速开始": self.quick_start_page,
            "日志": self.log_page,
            "关于": self.about_page
        }
        
        # 将页面添加到堆叠窗口
        for page in self.pages.values():
            self.stacked_widget.addWidget(page)
        
        # 设置默认页面
        self.buttons["快速开始"].setChecked(True)
        self.stacked_widget.setCurrentWidget(self.quick_start_page)
        self.current_page = "快速开始"
        
        log.info("初始化页面管理器")
    
    def create_sidebar_button(self, text):
        btn = QPushButton(text)
        btn.setFixedHeight(40)
        btn.setFixedWidth(150)  # 设置固定宽度
        btn.setCheckable(True)
        btn.clicked.connect(lambda: self.switch_page(text))
        btn.setStyleSheet("""
            QPushButton {
                border: none;
                text-align: left;
                padding-left: 20px;
                color: #333333;
                background: transparent;
                font-size: 14px;
                min-width: 150px;  /* 设置最小宽度 */
                max-width: 150px;  /* 设置最大宽度 */
            }
            QPushButton:hover {
                background-color: rgba(245, 245, 245, 0.8);
            }
            QPushButton:checked {
                background-color: rgba(245, 245, 245, 0.8);
                border-left: 3px solid #2196F3;
                color: #2196F3;
            }
        """)
        return btn
        
    def get_sidebar(self):
        return self.sidebar
        
    def add_page(self, name, page, button):
        if name in self.pages:
            log.warning(f"页面 {name} 已存在,将被覆盖")
            
        self.stacked_widget.addWidget(page)
        self.pages[name] = page
        self.buttons[name] = button
        log.info(f"添加页面: {name}")
        
    def switch_page(self, name):
        # 检查页面是否存在
        if name not in self.pages:
            log.error(f"页面 {name} 不存在")
            return
        
        # 检查是否正在切换到当前页面
        if name == self.current_page:
            log.debug(f"已经在 {name} 页面，无需切换")
            # 确保当前按钮保持选中状态
            self.buttons[name].setChecked(True)
            return
        
        log.info(f"切换到页面: {name}")
        
        # 取消其他按钮的选中状态
        for btn in self.buttons.values():
            btn.setChecked(False)
        
        # 设置当前按钮选中
        self.buttons[name].setChecked(True)
        
        # 获取当前页面和目标页面
        current_page = self.pages[self.current_page]
        next_page = self.pages[name]
        
        # 根据页面索引决定动画方向
        current_index = list(self.pages.keys()).index(self.current_page)
        next_index = list(self.pages.keys()).index(name)
        direction = "right" if next_index > current_index else "left"
        
        # 创建并执行动画
        self.animation_manager.create_page_switch_animation(
            current_page,
            next_page,
            direction
        )
        
        self.current_page = name
        log.info(f"页面切换完成: {name}")
    
    def get_stacked_widget(self):
        """获取堆叠窗口部件"""
        return self.stacked_widget
        
    def stop_animations(self) -> None:
        self.animation_manager.stop_all_animations()
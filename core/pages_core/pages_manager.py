from PySide6.QtWidgets import QStackedWidget, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, QEasingCurve, QObject
from PySide6.QtGui import QFont, QFontDatabase
from pages.quick_start import QuickStartPage
from pages.about_page import AboutPage
from pages.log_page import LogPage
from core.animations.animation_manager import AnimationManager
from core.log.log_manager import log
from core.font.font_manager import FontManager
from core.font.font_pages_manager import FontPagesManager
from core.animations.animation_pagemanager import PageAnimationManager
from pages.example_page import ExamplePage
from pages.settings_pages import SettingsPage
from pages.expandable_example import ExpandableExamplePage
from core.i18n import i18n

class PagesManager(QObject):
    def __init__(self):
        super().__init__()
        # 基础组件初始化
        self.stacked_widget = QStackedWidget()
        self.pages = {}
        self.buttons = {}
        self.current_page = None
        
        # 创建动画管理器
        self.animation_manager = AnimationManager()
        self.page_animation_manager = PageAnimationManager()
        
        # 创建字体管理器 (现在会使用单例模式)
        self.font_manager = FontManager()
        self.font_pages_manager = FontPagesManager()
        
        # 创建页面实例
        self.quick_start_page = QuickStartPage()
        self.about_page = AboutPage()
        self.log_page = LogPage()
        self.example_page = ExamplePage()
        self.settings_page = SettingsPage()
        self.expandable_example_page = ExpandableExamplePage()
        
        # 初始化侧边栏
        self.sidebar = QWidget()
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(10, 10, 10, 10)
        self.sidebar_layout.setSpacing(2)
        
        # 使用字体管理器获取图标映射
        self.icons = {
            "quick_start": ('dashboard', i18n.get_text("quick_start")),
            "example": ('auto_awesome', i18n.get_text("example")),
            "expandable": ('expand_more', i18n.get_text("expandable")),
            "log": ('article', i18n.get_text("log")),
            "about": ('info', i18n.get_text("about")),
            "settings": ('settings', i18n.get_text("settings"))
        }
        
        # 创建并存储按钮
        self.buttons = {
            key: self.create_sidebar_button(key, icon_info[0], icon_info[1])
            for key, icon_info in self.icons.items()
        }
        
        # 添加按钮到布局
        self.sidebar_layout.addWidget(self.buttons["quick_start"])
        self.sidebar_layout.addWidget(self.buttons["example"])
        self.sidebar_layout.addWidget(self.buttons["expandable"])
        self.sidebar_layout.addStretch(1)
        self.sidebar_layout.addWidget(self.buttons["log"])
        self.sidebar_layout.addWidget(self.buttons["about"])
        self.sidebar_layout.addWidget(self.buttons["settings"])
        
        # 添加页面映射
        self.pages = {
            "quick_start": self.quick_start_page,
            "example": self.example_page,
            "expandable": self.expandable_example_page,
            "log": self.log_page,
            "about": self.about_page,
            "settings": self.settings_page
        }
        
        # 将页面添加到堆叠窗口
        for page in self.pages.values():
            self.stacked_widget.addWidget(page)
        
        # 设置默认页面
        self.buttons["quick_start"].setChecked(True)
        self.stacked_widget.setCurrentWidget(self.quick_start_page)
        self.current_page = "quick_start"
        self.page_animation_manager.create_button_click_animation(self.buttons["quick_start"])
        
        # 连接语言变更信号
        i18n.language_changed.connect(self.update_all_pages_text)
        
        log.info(i18n.get_text("init_page_manager"))
    
    def create_sidebar_button(self, key, icon_name, text):
        btn = QPushButton()
        btn.setObjectName(f"btn_{key}")
        
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 0, 0, 0)
        layout.setSpacing(10)
        
        # 添加图标
        icon_label = QLabel(self.font_manager.get_icon_text(icon_name))
        icon_label.setObjectName(f"icon_{key}")
        self.font_manager.apply_icon_font(icon_label, size=20)
        icon_label.setStyleSheet("""
            QLabel {
                color: #666666;
                min-width: 24px;
                max-width: 24px;
            }
        """)
        layout.addWidget(icon_label)
        
        # 添加文本标签
        text_label = QLabel(text)
        text_label.setObjectName(f"text_{key}")
        default_font = self.font_pages_manager.setFont("HarmonyOS Sans SC", size=14)
        text_label.setFont(default_font)
        text_label.setWordWrap(True)  # 启用自动换行
        text_label.setStyleSheet("""
            QLabel {
                color: #333333;
                padding: 5px 0;
            }
        """)
        layout.addWidget(text_label)
        
        # 创建容器并设置布局
        container = QWidget()
        container.setLayout(layout)
        
        # 设置按钮样式和属性
        btn.setFixedWidth(150)
        btn.setMinimumHeight(40)  # 改为最小高度而不是固定高度
        btn.setCheckable(True)
        btn.clicked.connect(lambda: self.switch_page(key))
        
        # 设置布局
        btn.setLayout(layout)
        
        # 修改按钮样式表
        btn.setStyleSheet("""
            QPushButton {
                border: none;
                text-align: left;
                padding: 0;
                background: transparent;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: rgba(33, 150, 243, 0.1);
            }
            QPushButton:checked {
                background: rgba(33, 150, 243, 0.1);
            }
            QPushButton:checked QLabel {
                color: #2196F3;
            }
        """)
        return btn
        
    def update_all_pages_text(self):
        # 更新侧边栏按钮文本
        for key in self.buttons:
            text_label = self.buttons[key].findChild(QLabel, f"text_{key}")
            if text_label:
                text_label.setText(i18n.get_text(key))
        
        # 更新每个页面的文本
        for page in self.pages.values():
            if hasattr(page, "update_text"):
                try:
                    page.update_text()
                except Exception as e:
                    log.error(f"Error updating text for page {page.__class__.__name__}: {str(e)}")
                
    def get_sidebar(self):
        return self.sidebar
        
    def add_page(self, name, page, button):
        if name in self.pages:
            log.warning(i18n.get_text("page_exists", name))
            
        self.stacked_widget.addWidget(page)
        self.pages[name] = page
        self.buttons[name] = button
        log.info(i18n.get_text("add_page", name))
        
    def switch_page(self, name):
        if name not in self.pages:
            log.error(i18n.get_text("page_not_exists", name))
            return
        
        if name == self.current_page:
            log.debug(i18n.get_text("already_on_page", name))
            self.buttons[name].setChecked(True)
            return
            
        # 重要：切换前确保所有页面状态正确
        for page_name, page in self.pages.items():
            if page_name == name or page_name == self.current_page:
                page.show()
            else:
                page.hide()
        
        # 创建按钮点击动画
        self.page_animation_manager.create_button_click_animation(self.buttons[name])
        
        log.info(i18n.get_text("switch_to_page", name))
        
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
        
        # 优化动画方向判断
        if current_index < next_index:
            direction = "left"  # 向左滑出，新页面从右边进入
            offset = self.stacked_widget.width()
        else:
            direction = "right"  # 向右滑出，新页面从左边进入
            offset = -self.stacked_widget.width()
            
        # 预先设置新页面的初始位置
        next_page.show()
        next_page.setGeometry(current_page.geometry())
        
        # 创建平滑的滑动动画
        self.animation_manager.create_smooth_page_switch_animation(
            current_page=current_page,
            next_page=next_page,
            direction=direction,
            duration=300,  # 动画持续时间(毫秒)
            easing_curve=QEasingCurve.OutCubic  # 使用缓动曲线让动画更自然
        )
        
        self.current_page = name
        log.info(i18n.get_text("page_switch_complete", name))
    
    def get_stacked_widget(self):
        return self.stacked_widget
        
    def stop_animations(self) -> None:
        self.animation_manager.stop_all_animations()
        self.page_animation_manager.stop_animations()
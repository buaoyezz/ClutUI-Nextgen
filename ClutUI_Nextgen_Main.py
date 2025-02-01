'''
入口程序
'''

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget
from PySide6.QtCore import Qt, QThread, QMetaObject, QTimer
from PySide6.QtGui import QIcon, QColor, QFontDatabase
from pages.quick_start import QuickStartPage
from core.animations.animation_manager import AnimationManager
from core.font.font_manager import FontManager
from core.log.log_manager import log
from core.pages_core.pages_manager import PagesManager
import time
import sys
import os

class TitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.moving = False
        self.offset = None
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(0)
        
        # 创建字体管理器
        self.font_manager = FontManager()
        log.info("初始化标题栏字体管理器")
        
        # 设置背景色和高度
        self.setFixedHeight(40)
        self.setStyleSheet("""
            QWidget {
                background: transparent;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                border-bottom: 1px solid #E0E0E0;
            }
            QPushButton {
                background: transparent;
                color: #666666;
                border: none;
                width: 20px;
                height: 20px;
                padding: 4px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #F5F5F5;
            }
            QPushButton#closeButton:hover {
                background-color: #FF6B6B;
                color: white;
            }
        """)
        
        # 标题文本
        self.title_label = QLabel("ClutUI Next Generation | For Pyside6 ")
        self.title_label.setStyleSheet("""
            QLabel {
                background: transparent;
                color: #333333;
                font-weight: bold;
                padding: 0 5px;
            }
        """)
        
        # 应用字体
        self.font_manager.apply_font(self.title_label)
        # 设置标题字体大小
        font = self.title_label.font()
        font.setPointSize(12)
        self.title_label.setFont(font)
        
        # 最小化和关闭按钮
        self.min_button = QPushButton("一")  # 使用更标准的减号符号
        self.close_button = QPushButton("✕")  # 使用更清晰的乘号符号
        # 应用字体到按钮
        self.font_manager.apply_font(self.min_button)
        self.font_manager.apply_font(self.close_button)
        
        # 修改按钮样式
        btn_style = """
            QPushButton {
                background: transparent;
                color: #666666;
                border: none;
                width: 20px;
                height: 20px;
                padding: 4px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #E5E5E5;
            }
            QPushButton#closeButton:hover {
                background-color: #FF4D4D;
                color: white;
            }
        """
        self.min_button.setStyleSheet(btn_style)
        self.close_button.setStyleSheet(btn_style)
        self.close_button.setObjectName("closeButton")
        
        # 添加到布局
        layout.addWidget(self.title_label)
        layout.addStretch()
        layout.addWidget(self.min_button)
        layout.addWidget(self.close_button)
        
        # 连接信号
        self.min_button.clicked.connect(self.window().showMinimized)
        self.close_button.clicked.connect(self.window().close)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.moving = True
            self.offset = event.position()
            log.debug("开始拖动窗口")
            
    def mouseMoveEvent(self, event):
        if self.moving:
            # 获取全局位置并考虑偏移量
            new_pos = event.globalPosition().toPoint() - self.offset.toPoint()
            # 确保窗口不会超出屏幕边界
            window = self.window()
            screen = QApplication.primaryScreen().geometry()
            new_x = max(screen.left(), min(new_pos.x(), screen.right() - window.width()))
            new_y = max(screen.top(), min(new_pos.y(), screen.bottom() - window.height()))
            window.move(new_x, new_y)
            
    def mouseReleaseEvent(self, event):
        self.moving = False
        log.debug("结束拖动窗口")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 确保日志目录存在
        log_dir = os.path.join(os.path.expanduser('~'), '.clutui_nextgen_example', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log.info("初始化主窗口")
        self.moving = False
        self.offset = None
        
        # 创建页面管理器
        self.pages_manager = PagesManager()
        
        # 获取快速开始页面
        self.quick_start_page = self.pages_manager.quick_start_page
        
        # 创建字体管理器
        self.font_manager = FontManager()
        
        # 设置窗口基本属性
        self.setWindowTitle("ClutUI Nextgen")
        self.setMinimumSize(600, 450)
        self.resize(1080, 650)
        
        # 设置窗口背景透明
        self.setAttribute(Qt.WA_TranslucentBackground)
        # 设置无边框窗口
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        
        # 创建主窗口部件
        main_widget = QWidget()
        main_widget.setObjectName("mainWidget")
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 添加标题栏
        title_bar = TitleBar(self)
        main_layout.addWidget(title_bar)
        
        # 创建内容区域容器
        content_container = QWidget()
        content_layout = QHBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # 右侧内容区
        right_content = QWidget()
        self.right_layout = QVBoxLayout(right_content)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建动画管理器
        self.animation_manager = AnimationManager()
        log.info("初始化动画管理器")
        
        # 创建一个容器来包装堆叠窗口，用于动画
        self.page_container = QWidget()
        self.page_layout = QVBoxLayout(self.page_container)
        self.page_layout.setContentsMargins(0, 0, 0, 0)
        self.page_layout.addWidget(self.pages_manager.get_stacked_widget())
        
        # 将容器添加到右侧布局
        self.right_layout.addWidget(self.page_container)
        
        # 将左右两侧添加到内容布局
        content_layout.addWidget(self.pages_manager.get_sidebar())  # 使用 PagesManager 的侧边栏
        content_layout.addWidget(right_content)
        
        # 将内容容器添加到主布局
        main_layout.addWidget(content_container)
        
        # 设置主窗口样式
        main_widget.setStyleSheet("""
            QWidget#mainWidget {
                background-color: #F8F9FA;
                border-radius: 10px;
                border: 1px solid #E0E0E0;
            }
        """)
        
        self.setCentralWidget(main_widget)
        
        # 添加计数器属性
        self.total_files = 0
        self.scanned_size = 0
        
        # 初始化扫描线程属性
        self.scan_thread = None
        
        # 添加线程管理
        self._closing = False
        self._cleanup_timer = QTimer()
        self._cleanup_timer.setSingleShot(True)
        self._cleanup_timer.timeout.connect(self._finish_close)

    def closeEvent(self, event):
        if self._closing:
            event.accept()
            return
            
        try:
            log.info("开始关闭应用程序")
            self._closing = True
            event.ignore()
            
            # 停止所有动画
            self.pages_manager.stop_animations()
            
            # 确保所有页面都停止扫描
            stacked_widget = self.pages_manager.get_stacked_widget()
            for i in range(stacked_widget.count()):
                page = stacked_widget.widget(i)
                if hasattr(page, 'safe_cleanup'):
                    page.safe_cleanup()
            
            # 延迟关闭
            self._cleanup_timer.start(1000)  # 给予1秒的清理时间
            
        except Exception as e:
            log.error(f"关闭应用程序时出错: {str(e)}")
            event.accept()

    def _finish_close(self):
        try:
            # 强制清理所有页面的引用
            stacked_widget = self.pages_manager.get_stacked_widget()
            while stacked_widget.count() > 0:
                widget = stacked_widget.widget(0)
                stacked_widget.removeWidget(widget)
                if hasattr(widget, 'scanner'):
                    widget.scanner = None
                widget.deleteLater()
            
            # 清理其他资源
            QApplication.processEvents()
            
            # 确保主窗口关闭
            self.close()
            
        except Exception as e:
            log.error(f"完成关闭时出错: {str(e)}")
            self.close()

    def switch_page(self, page_name):
        try:
            # 获取页面索引
            page_index = {
                "快速开始": 0,
                "关于": 1,
            }.get(page_name)
            
            if page_index is not None:
                # 切换到对应页面
                self.pages_manager.get_stacked_widget().setCurrentIndex(page_index)
                # 更新侧边栏选中状态
                if hasattr(self, 'sidebar'):
                    self.sidebar.select_item(page_name)
                log.info(f"切换到页面: {page_name}")
            else:
                log.error(f"未找到页面: {page_name}")
                
        except Exception as e:
            log.error(f"切换页面失败: {str(e)}")

if __name__ == '__main__':
    try:
        app = QApplication([])
        
        # 设置应用程序属性，确保正确清理
        app.setAttribute(Qt.AA_DontShowIconsInMenus, True)
        app.setQuitOnLastWindowClosed(True)
        
        font_manager = FontManager()
        font_manager.apply_font(app)
        
        app.setStyleSheet("""
            * {
                color: #333333;
            }
        """)
        
        window = MainWindow()
        window.show()
        log.info("ClutUI Nextgen 已经启动！")
        exit_code = app.exec()
        window._finish_close()
        
        sys.exit(exit_code)
        
    except Exception as e:
        log.error(f"应用程序运行出错: {str(e)}")
        sys.exit(1)


from PySide6.QtWidgets import (
    QWidget, 
    QVBoxLayout, 
    QHBoxLayout,
    QLabel,
    QPushButton,
    QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QColor
from core.font.font_pages_manager import FontPagesManager
from core.log.log_manager import log
from core.animations.animation_msgbox import MessageBoxAnimation

class MessageButton:
    def __init__(self, text, style="default", return_value=None):
        self.text = text
        self.style = style  # default, primary, danger
        self.return_value = return_value if return_value is not None else text

class MessageBoxWhite(MessageBoxAnimation):
    button_clicked = Signal(object)
    
    def __init__(self, title="", message="", buttons=None, icon=None, parent=None):
        super().__init__(parent)
        
        if buttons is None:
            buttons = [MessageButton("确定", "primary")]
        elif isinstance(buttons[0], str):
            # 兼容旧的字符串列表方式
            buttons = [MessageButton(text, "primary" if i == len(buttons)-1 else "default") 
                      for i, text in enumerate(buttons)]
            
        self.font_manager = FontPagesManager()
        self.moving = False
        self.offset = QPoint()
        
        # 设置窗口属性
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.Tool |
            Qt.WindowStaysOnTopHint |
            Qt.Dialog
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)  # 增加边距以显示阴影
        
        # 创建内容容器
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(24, 20, 24, 20)
        content_layout.setSpacing(16)
        
        # 标题栏布局
        title_layout = QHBoxLayout()
        
        # 图标(如果有)
        if icon:
            icon_label = QLabel()
            self.font_manager.apply_icon_font(icon_label, 20)
            icon_label.setText(icon)
            icon_label.setStyleSheet("color: #333333;")
            title_layout.addWidget(icon_label)
        
        # 标题
        title_label = QLabel(title)
        self.font_manager.apply_subtitle_style(title_label)
        title_label.setStyleSheet("color: #333333; font-weight: 500;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # 消息内容
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        self.font_manager.apply_normal_style(message_label)
        message_label.setStyleSheet("color: #666666;")
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        button_layout.addStretch()
        
        # 按钮样式映射
        button_styles = {
            "default": """
                QPushButton {
                    background: #F5F5F5;
                    color: #333333;
                    border: none;
                    border-radius: 4px;
                    padding: 0 16px;
                }
                QPushButton:hover { background: #EEEEEE; }
                QPushButton:pressed { background: #E0E0E0; }
            """,
            "primary": """
                QPushButton {
                    background: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 0 16px;
                }
                QPushButton:hover { background: #1E88E5; }
                QPushButton:pressed { background: #1976D2; }
            """,
            "danger": """
                QPushButton {
                    background: #F44336;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 0 16px;
                }
                QPushButton:hover { background: #E53935; }
                QPushButton:pressed { background: #D32F2F; }
            """
        }
        
        for btn in buttons:
            button = QPushButton(btn.text)
            button.setFixedHeight(32)
            self.font_manager.apply_normal_style(button)
            button.setStyleSheet(button_styles.get(btn.style, button_styles["default"]))
            button.clicked.connect(lambda checked, b=btn: self.on_button_clicked(b))
            button_layout.addWidget(button)
        
        # 添加到内容布局
        content_layout.addLayout(title_layout)
        content_layout.addWidget(message_label)
        content_layout.addSpacing(4)
        content_layout.addLayout(button_layout)
        
        # 设置内容容器样式
        content.setStyleSheet("""
            QWidget {
                background: white;
                border-radius: 8px;
            }
        """)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        content.setGraphicsEffect(shadow)
        
        # 添加到主布局
        layout.addWidget(content)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.moving = True
            self.offset = event.position().toPoint()
            log.debug("开始拖动消息框")
            
    def mouseMoveEvent(self, event):
        if self.moving and event.buttons() == Qt.LeftButton:
            self.move(self.mapToGlobal(event.position().toPoint() - self.offset))
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.moving = False
            log.debug("结束拖动消息框")
            
    def showEvent(self, event):
        self.show_with_animation()
        super().showEvent(event)
    
    def closeEvent(self, event):
        self.hide_with_animation()
        event.ignore()
    
    def on_button_clicked(self, button):
        self.button_clicked.emit(button)
        self.close()

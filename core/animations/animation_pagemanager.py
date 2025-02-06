from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QSequentialAnimationGroup
from PySide6.QtWidgets import QWidget, QFrame

class PageAnimationManager:
    def __init__(self):
        self.current_animation = None
        self.blue_line = None
        self.blue_bg = None
        self.current_button = None
        
    def create_button_click_animation(self, button: QWidget) -> None:
        # 停止正在运行的动画
        if self.current_animation and self.current_animation.state() == QPropertyAnimation.Running:
            self.current_animation.stop()
        
        # 如果是新按钮，移除旧的蓝条和背景
        if self.current_button != button:
            if self.blue_line:
                self.blue_line.deleteLater()
                self.blue_line = None
            if self.blue_bg:
                self.blue_bg.deleteLater()
                self.blue_bg = None
            
        if not self.blue_line:
            # 创建蓝条
            self.blue_line = QFrame(button)
            self.blue_line.setStyleSheet("background-color: #2196F3;")
            self.blue_line.setFixedWidth(3)
            self.blue_line.show()
            
            # 创建背景
            self.blue_bg = QFrame(button)
            self.blue_bg.setStyleSheet("""
                QFrame {
                    background-color: rgba(33, 150, 243, 0.15);
                    border-radius: 4px;
                }
            """)
            self.blue_bg.setFixedHeight(button.height())
            self.blue_bg.lower()  # 将背景放到最底层
            self.blue_bg.show()
            
        self.current_button = button
        animation_group = QParallelAnimationGroup()  # 改用并行动画组
        
        # 透明度动画
        opacity_animation = QPropertyAnimation(button, b"windowOpacity")
        opacity_animation.setDuration(200)
        opacity_animation.setEasingCurve(QEasingCurve.InOutCubic)
        opacity_animation.setStartValue(1.0)
        opacity_animation.setKeyValueAt(0.5, 0.7)
        opacity_animation.setEndValue(1.0)
        
        # 蓝条高度动画
        height_animation = QPropertyAnimation(self.blue_line, b"geometry")
        height_animation.setDuration(300)
        height_animation.setEasingCurve(QEasingCurve.InOutCubic)
        self.blue_line.setGeometry(0, 0, 3, 0)
        height_animation.setStartValue(self.blue_line.geometry())
        height_animation.setEndValue(self.blue_line.geometry().adjusted(0, 0, 0, button.height()))
        
        # 背景宽度动画
        bg_animation = QPropertyAnimation(self.blue_bg, b"geometry")
        bg_animation.setDuration(300)
        bg_animation.setEasingCurve(QEasingCurve.InOutCubic)
        self.blue_bg.setGeometry(0, 0, 0, button.height())
        bg_animation.setStartValue(self.blue_bg.geometry())
        bg_animation.setEndValue(self.blue_bg.geometry().adjusted(0, 0, button.width(), 0))
        
        animation_group.addAnimation(opacity_animation)
        animation_group.addAnimation(height_animation)
        animation_group.addAnimation(bg_animation)
        
        self.current_animation = animation_group
        animation_group.start()
        
    def stop_animations(self) -> None:
        if self.current_animation:
            self.current_animation.stop()
        if self.blue_line:
            self.blue_line.deleteLater()
            self.blue_line = None
        if self.blue_bg:
            self.blue_bg.deleteLater()
            self.blue_bg = None

from PySide6.QtCore import QPropertyAnimation, QParallelAnimationGroup, QEasingCurve, Property, QPoint, Qt, QObject
from PySide6.QtWidgets import QWidget, QLabel, QGraphicsRotation, QGraphicsOpacityEffect
from PySide6.QtGui import QTransform
from core.font.font_manager import FontManager

class ExpandableAnimation(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.content = None
        self.icon = None
        self.font_manager = FontManager()
        self.duration = 250  # 缩短动画时长提升响应速度
        self._icon_rotation = 0
        self._content_height = 0
        self._target_height = 0
        self._setup_animations()
        
    def _setup_animations(self):
        # 内容高度动画
        self.height_animation = QPropertyAnimation(self, b"content_height")
        self.height_animation.setDuration(self.duration)
        self.height_animation.setEasingCurve(QEasingCurve.OutCubic)  # 使用更自然的缓动曲线
        
        # 图标旋转动画
        self.rotation_animation = QPropertyAnimation(self, b"icon_rotation")
        self.rotation_animation.setDuration(self.duration)
        self.rotation_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # 动画组
        self.animation_group = QParallelAnimationGroup()
        self.animation_group.addAnimation(self.height_animation)
        self.animation_group.addAnimation(self.rotation_animation)
        
    def set_widgets(self, content_widget, icon_widget=None):
        """设置需要动画的组件"""
        self.content = content_widget
        self.icon = icon_widget
        if self.content:
            # 初始化目标高度
            self._target_height = self.content.sizeHint().height()
            # 确保初始状态是收起的
            self.content.setMaximumHeight(0)
        if self.icon:
            # 设置初始图标
            self.icon.setText(self.font_manager.get_icon_text('expand_more'))
            self.icon.setStyleSheet("background: transparent;")
            
    def get_content_height(self):
        return self._content_height
        
    def set_content_height(self, height):
        self._content_height = height
        if self.content:
            self.content.setMaximumHeight(height)
            
    content_height = Property(int, get_content_height, set_content_height)
    
    def get_icon_rotation(self):
        return self._icon_rotation
        
    def set_icon_rotation(self, angle):
        self._icon_rotation = angle
        if self.icon:
            # 直接切换图标
            icon_name = 'expand_less' if angle > 90 else 'expand_more'
            self.icon.setText(self.font_manager.get_icon_text(icon_name))
            
    icon_rotation = Property(float, get_icon_rotation, set_icon_rotation)
    
    def update_target_height(self):
        """更新目标高度"""
        if self.content:
            # 临时移除最大高度限制以获取真实高度
            self.content.setMaximumHeight(16777215)
            self._target_height = self.content.sizeHint().height()
            # 恢复当前高度
            self.content.setMaximumHeight(self._content_height)
    
    def toggle_animation(self, is_expanded):
        """切换展开/收起动画"""
        if not self.content:
            return
            
        # 更新目标高度
        self.update_target_height()
        
        # 设置动画起始和结束值
        current_height = self.content.maximumHeight()
        
        if is_expanded:
            # 展开动画
            self.height_animation.setStartValue(current_height)
            self.height_animation.setEndValue(self._target_height)
            self.rotation_animation.setStartValue(0)
            self.rotation_animation.setEndValue(180)
        else:
            # 收起动画
            self.height_animation.setStartValue(current_height)
            self.height_animation.setEndValue(0)
            self.rotation_animation.setStartValue(180)
            self.rotation_animation.setEndValue(0)
            
        self.animation_group.start()
        
    def set_duration(self, duration=250):
        """设置动画时长"""
        self.duration = duration
        self.height_animation.setDuration(duration)
        self.rotation_animation.setDuration(duration)
        
    def is_running(self):
        """检查动画是否正在运行"""
        return self.animation_group.state() == QParallelAnimationGroup.Running
        
    def stop(self):
        """停止动画"""
        self.animation_group.stop()
        
class ExpandableMixin:
    """可以被其他卡片组件继承的Mixin类"""
    def init_expandable(self, content_widget, icon_widget=None, duration=300):
        self.animation = ExpandableAnimation(self)
        self.animation.set_widgets(content_widget, icon_widget)
        self.animation.set_duration(duration)
        self._is_expanded = False
        
    def toggle_expand(self, force_state=None):
        """切换展开状态"""
        if self.animation.is_running():
            return
            
        if force_state is not None:
            self._is_expanded = force_state
        else:
            self._is_expanded = not self._is_expanded
            
        self.animation.toggle_animation(self._is_expanded)
        
    def is_expanded(self):
        return self._is_expanded
        
    def set_animation_duration(self, duration=300):
        self.animation.set_duration(duration) 
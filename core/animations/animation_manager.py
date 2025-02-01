"""
提供的Args:
        Args:
            current_page: 当前页面
            next_page: 目标页面
            direction: 切换方向，"right" 或 "left"
    
"""


from PySide6.QtCore import QObject, QPropertyAnimation, QParallelAnimationGroup, QEasingCurve, QPoint
from PySide6.QtWidgets import QWidget
from core.log.log_manager import log

class AnimationManager(QObject):
    def __init__(self):
        super().__init__()
        self.current_animations = []
        self.animation_running = False
        
    def create_page_switch_animation(self, current_page: QWidget, next_page: QWidget, direction: str = "right") -> None:
        if not current_page or not next_page:
            return
            
        # 如果有动画正在运行，立即停止并重置页面位置
        if self.animation_running:
            self.stop_all_animations()
            # 重置所有页面位置
            if hasattr(self, 'current_page'):
                self.current_page.move(0, 0)
                self.current_page.hide()
            if hasattr(self, 'next_page'):
                self.next_page.move(0, 0)
                self.next_page.show()
        
        # 标记动画开始运行
        self.animation_running = True
        
        # 获取页面尺寸
        width = current_page.width()
        height = current_page.height()
        
        # 确保两个页面大小一致
        next_page.resize(width, height)
        
        # 设置初始位置并确保页面可见
        current_page.raise_()
        next_page.raise_()
        
        # 设置初始位置
        if direction == "right":
            next_page.move(width, 0)
            start_pos_current = QPoint(0, 0)
            end_pos_current = QPoint(-width, 0)
            start_pos_next = QPoint(width, 0)
            end_pos_next = QPoint(0, 0)
        else:
            next_page.move(-width, 0)
            start_pos_current = QPoint(0, 0)
            end_pos_current = QPoint(width, 0)
            start_pos_next = QPoint(-width, 0)
            end_pos_next = QPoint(0, 0)
            
        # 创建动画组
        group = QParallelAnimationGroup(self)
        
        # 当前页面的动画
        current_anim = QPropertyAnimation(current_page, b"pos", self)
        current_anim.setDuration(300)
        current_anim.setStartValue(start_pos_current)
        current_anim.setEndValue(end_pos_current)
        current_anim.setEasingCurve(QEasingCurve.InOutQuad)
        
        # 下一个页面的动画
        next_anim = QPropertyAnimation(next_page, b"pos", self)
        next_anim.setDuration(300)
        next_anim.setStartValue(start_pos_next)
        next_anim.setEndValue(end_pos_next)
        next_anim.setEasingCurve(QEasingCurve.InOutQuad)
        
        # 将动画添加到组中
        group.addAnimation(current_anim)
        group.addAnimation(next_anim)
        
        # 保存对页面的引用
        self.current_page = current_page
        self.next_page = next_page
        
        # 连接完成信号
        group.finished.connect(self._on_animation_finished)
        
        # 保存当前动画组
        self.current_animations.append(group)
        
        # 显示下一个页面并确保其位于正确的位置
        next_page.show()
        
        # 开始动画
        group.start()
        log.debug(f"开始页面切换动画: {direction}")
        
    def stop_all_animations(self):
        self.animation_running = False
        for animation in self.current_animations:
            if animation and animation.state() == QPropertyAnimation.Running:
                animation.stop()
        self.current_animations.clear()
        
    def _on_animation_finished(self):
        try:
            if hasattr(self, 'current_page'):
                if hasattr(self.current_page, 'to_be_deleted') and self.current_page.to_be_deleted:
                    # 如果页面标记为待删除，现在可以安全地删除它
                    stacked_widget = self.current_page.parent()
                    if stacked_widget:
                        stacked_widget.removeWidget(self.current_page)
                        self.current_page.deleteLater()
                        log.debug("已删除旧页面 ~")
                else:
                    self.current_page.hide()
            
            if hasattr(self, 'next_page'):
                self.next_page.show()
                self.next_page.move(0, 0)
                
        except Exception as e:
            log.error(f"动画完成处理出错: {str(e)}")
            
        finally:
            # 清理引用和动画
            self.animation_running = False
            self.current_animations.clear()
            if hasattr(self, 'current_page'):
                delattr(self, 'current_page')
            if hasattr(self, 'next_page'):
                delattr(self, 'next_page')
            log.debug("页面切换动画完成")

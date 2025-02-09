"""
提供的Args:
        Args:
            current_page: 当前页面
            next_page: 目标页面
            direction: 切换方向，"right" 或 "left"
    
"""


from PySide6.QtCore import QObject, QPropertyAnimation, QParallelAnimationGroup, QEasingCurve, QPoint, Qt
from PySide6.QtWidgets import QWidget, QStackedWidget
from core.log.log_manager import log

class AnimationManager(QObject):
    def __init__(self):
        super().__init__()
        self.current_animations = []
        self.animation_running = False
        self.current_animation = None
        
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

    def create_smooth_page_switch_animation(self, current_page, next_page, direction, duration=300, easing_curve=QEasingCurve.OutCubic):
        if self.current_animation and self.current_animation.state() == QPropertyAnimation.Running:
            self.current_animation.stop()
            self._cleanup_animation(current_page, next_page)
            
        # 获取父级QStackedWidget
        stacked_widget = current_page.parent()
        if not isinstance(stacked_widget, QStackedWidget):
            return
            
        # 重要：确保所有其他页面都隐藏
        for i in range(stacked_widget.count()):
            page = stacked_widget.widget(i)
            if page not in (current_page, next_page):
                page.hide()
            
        # 设置页面层级关系
        next_page.stackUnder(current_page)
        
        # 设置WA_TranslucentBackground以支持叠加
        current_page.setAttribute(Qt.WA_TranslucentBackground)
        next_page.setAttribute(Qt.WA_TranslucentBackground)
        
        # 确保两个页面都可见并正确定位
        current_page.show()
        next_page.show()
        next_page.raise_()
        
        # 获取页面尺寸
        width = stacked_widget.width()
        
        # 设置初始位置
        current_page.move(0, 0)
        if direction == "left":
            next_page.move(width, 0)
        else:
            next_page.move(-width, 0)
            
        # 创建动画组
        animation_group = QParallelAnimationGroup()
        
        # 当前页面动画
        current_anim = QPropertyAnimation(current_page, b"pos")
        current_anim.setDuration(duration)
        current_anim.setStartValue(QPoint(0, 0))
        current_anim.setEndValue(QPoint(-width if direction == "left" else width, 0))
        current_anim.setEasingCurve(easing_curve)
        
        # 下一页面动画
        next_anim = QPropertyAnimation(next_page, b"pos")
        next_anim.setDuration(duration)
        next_anim.setStartValue(next_page.pos())
        next_anim.setEndValue(QPoint(0, 0))
        next_anim.setEasingCurve(easing_curve)
        
        animation_group.addAnimation(current_anim)
        animation_group.addAnimation(next_anim)
        
        # 动画完成后的清理
        animation_group.finished.connect(
            lambda: self._cleanup_animation(current_page, next_page)
        )
        
        self.current_animation = animation_group
        animation_group.start()
        
    def _cleanup_animation(self, current_page, next_page):
        # 重要：确保其他页面状态正确
        stacked_widget = current_page.parent()
        if isinstance(stacked_widget, QStackedWidget):
            for i in range(stacked_widget.count()):
                page = stacked_widget.widget(i)
                if page == next_page:
                    page.show()
                    page.raise_()
                else:
                    page.hide()
        
        # 重置页面状态
        current_page.hide()
        next_page.show()
        current_page.move(0, 0)
        next_page.move(0, 0)
        
        # 移除透明属性
        current_page.setAttribute(Qt.WA_TranslucentBackground, False)
        next_page.setAttribute(Qt.WA_TranslucentBackground, False)

from PySide6.QtWidgets import QApplication
from core.log.log_manager import log
from core.animations.close_app import CloseAppAnimation

class WindowManager:
    @staticmethod
    def handle_close_event(window, event):
        if window._closing:
            event.accept()
            return
            
        try:
            log.info("Closing Application")
            window._closing = True
            event.ignore()
            
            # 停止所有动画
            window.pages_manager.stop_animations()
            
            # 确保所有页面都停止扫描
            stacked_widget = window.pages_manager.get_stacked_widget()
            for i in range(stacked_widget.count()):
                page = stacked_widget.widget(i)
                if hasattr(page, 'safe_cleanup'):
                    page.safe_cleanup()
            
            # NEW: Close App Animation [Beta]
            window._close_animation = CloseAppAnimation(window)
            window._close_animation.start()
            
        except Exception as e:
            log.error(f"Error: 中头彩了|{str(e)}|可以去提交issue了")
            event.accept()

    @staticmethod
    def finish_close(window):
        try:
            # 强制清理所有页面的引用
            stacked_widget = window.pages_manager.get_stacked_widget()
            while stacked_widget.count() > 0:
                widget = stacked_widget.widget(0)
                stacked_widget.removeWidget(widget)
                if hasattr(widget, 'scanner'):
                    widget.scanner = None
                widget.deleteLater()
            
            # 清理资源
            QApplication.processEvents()
            
            # 强制关闭窗口
            window.close()
            
        except Exception as e:
            log.error(f"Error: 中头彩了|{str(e)}")
            window.close()

    @staticmethod
    def switch_page(window, page_name):
        try:
            # 获取页面索引
            page_index = {
                "快速开始": 0,
                "关于": 1,
            }.get(page_name)
            
            if page_index is not None:
                # 切换到对应页面
                window.pages_manager.get_stacked_widget().setCurrentIndex(page_index)
                # 更新侧边栏选中状态
                if hasattr(window, 'sidebar'):
                    window.sidebar.select_item(page_name)
                log.info(f"切换到页面: {page_name}")
            else:
                log.error(f"未找到页面: {page_name}")
                
        except Exception as e:
            log.error(f"切换页面失败: {str(e)}") 
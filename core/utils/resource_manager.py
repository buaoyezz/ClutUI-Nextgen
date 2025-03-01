import os
import sys
from PySide6.QtGui import QIcon, QPixmap, QImage
from PySide6.QtCore import QSize, Qt
from core.log.log_manager import log
import ctypes

class ResourceManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ResourceManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self._cache = {}
        
    @staticmethod
    def get_resource_path(relative_path):
        if hasattr(sys, '_MEIPASS'):
            # 打包后的路径
            base_path = sys._MEIPASS
        else:
            # 开发环境路径
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
    
    def get_icon(self, name, cache=True):
        if cache and name in self._cache:
            return self._cache[name]
        
        # 首先尝试加载 ICO 文件
        ico_path = self.get_resource_path(os.path.join("resources", f"{name}.ico"))
        if os.path.exists(ico_path):
            icon = QIcon(ico_path)
            if not icon.isNull():
                if cache:
                    self._cache[name] = icon
                return icon
        
        # 如果没有 ICO 文件或加载失败，尝试加载 PNG 文件
        png_path = self.get_resource_path(os.path.join("resources", f"{name}.png"))
        pixmap = QPixmap(png_path)
        
        if pixmap.isNull():
            log.error(f"无法加载图标: {png_path}")
            return None
            
        # 创建图标并添加不同尺寸
        icon = QIcon()
        sizes = [16, 32, 48, 64, 128, 256]
        for size in sizes:
            scaled_pixmap = pixmap.scaled(
                size, size,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            icon.addPixmap(scaled_pixmap)
            
        if cache:
            self._cache[name] = icon
            
        return icon
    
    def get_pixmap(self, name, cache=True, size=None):
        """获取图片，仅支持 PNG 格式
        Args:
            name: 图片名称（不含扩展名）
            cache: 是否缓存
            size: 可选的目标尺寸元组 (width, height)
        """
        if cache and name in self._cache and not size:
            return self._cache[name]
            
        path = self.get_resource_path(os.path.join("resources", f"{name}.png"))
        pixmap = QPixmap(path)
        
        if pixmap.isNull():
            log.error(f"无法加载图片: {path}")
            return None
            
        if size:
            pixmap = pixmap.scaled(
                size[0], size[1],
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        
        if cache and not size:
            self._cache[name] = pixmap
            
        return pixmap
    
    def clear_cache(self):
        self._cache.clear() 
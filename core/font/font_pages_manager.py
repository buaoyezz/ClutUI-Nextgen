# 字体管理器 -Pages

from PySide6.QtGui import QFont, QFontDatabase, QAction
from PySide6.QtWidgets import QWidget, QApplication, QLabel, QPushButton
from core.ui.buttons_blue import Button 
from PySide6.QtCore import Qt
import platform
from core.log.log_manager import log
import os
import sys
from core.font.font_manager import FontManager
from core.thread.thread_manager import thread_manager

def resource_path(relative_path):
    base_path = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class FontPagesManager:
    _instance = None
    _initialized = False
    
    FONT_CONFIGS = {
        'default': {
            'primary': 'HarmonyOS Sans SC',
            'secondary': 'Mulish',
            'icon': 'Material Icons'
        },
        'fallback': {
            'Windows': {'chinese': 'Source Han Sans CN', 'english': 'Roboto'},
            'Darwin': {'chinese': 'Source Han Sans CN', 'english': 'Roboto'},
            'Linux': {'chinese': 'Noto Sans CJK SC', 'english': 'Ubuntu'}
        }
    }
    
    def __new__(cls):
        if cls._instance is None:
            log.info("创建 FontPagesManager 单例")
            cls._instance = super(FontPagesManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            log.info("初始化 FontPagesManager")
            self._setup_font_objects()
            self._initialized = True

    def _setup_font_objects(self):
        fonts = self.FONT_CONFIGS['default']
        
        self.title_font = self._create_font([fonts['primary'], fonts['secondary']], 36, QFont.Weight.Bold)
        self.subtitle_font = self._create_font([fonts['primary'], fonts['secondary']], 16, QFont.Weight.Medium)
        self.normal_font = self._create_font([fonts['primary'], fonts['secondary']], 14)
        self.small_font = self._create_font([fonts['primary'], fonts['secondary']], 13)
        self.button_font = self._create_font([fonts['primary'], fonts['secondary']], 14, QFont.Weight.Medium)
        self.icon_font = self._create_font([fonts['icon']], 24)

    def _create_font(self, families, size, weight=QFont.Weight.Normal, letter_spacing=0.5):
        font = QFont()
        font.setFamilies(families)
        font.setPixelSize(size)
        font.setWeight(weight)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, letter_spacing)
        return font

    def setFont(self, font_name, size=14, weight=QFont.Weight.Normal):
        if not isinstance(font_name, str):
            log.warning("字体名称必须是字符串类型")
            return None
            
        font = QFont()
        font.setFamily(font_name)
        font.setPixelSize(size)
        font.setWeight(weight)
        return font

    def apply_font(self, widget, font_type="normal"):
        if not isinstance(widget, (QWidget, QLabel, QAction)):
            log.warning(f"不支持的控件类型: {type(widget)}")
            return

        font_map = {
            "title": self.title_font,
            "normal": self.normal_font,
            "small": self.small_font
        }
        widget.setFont(font_map.get(font_type, self.normal_font))

    def apply_icon_font(self, widget, size=24):
        if isinstance(widget, (QWidget, QLabel, QAction)):
            icon_font = self._create_font([self.FONT_CONFIGS['default']['icon']], size)
            widget.setFont(icon_font)
        else:
            log.warning(f"不支持的控件类型: {type(widget)}")

    def get_icon_text(self, icon_name):
        from core.font.icon_map import ICON_MAP
        return ICON_MAP.get(icon_name, '')

    def apply_title_style(self, widget):
        self.apply_font(widget, "title")
        
    def apply_normal_style(self, widget):
        self.apply_font(widget, "normal")
        
    def apply_small_style(self, widget):
        self.apply_font(widget, "small")
        
    def apply_subtitle_style(self, widget):
        if not isinstance(widget, (QWidget, QLabel)):
            log.warning(f"不支持的控件类型: {type(widget)}")
            return
            
        widget.setFont(self.subtitle_font)
        if isinstance(widget, QLabel):
            widget.setStyleSheet("color: #666666; background: transparent;")

    def apply_button_style(self, widget):
        if not isinstance(widget, (QPushButton, Button)):
            log.warning(f"不支持的控件类型: {type(widget)}")
            return
            
        widget.setFont(self.button_font)

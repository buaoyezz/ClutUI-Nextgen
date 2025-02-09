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
    
    FONT_FILES = {
        'HarmonyOS Sans SC': 'HarmonyOS_Sans_SC_Regular.ttf',
        'HarmonyOS Sans SC Bold': 'HarmonyOS_Sans_SC_Bold.ttf',
        'Mulish': 'Mulish-Regular.ttf',
        'Mulish Bold': 'Mulish-Bold.ttf',
        'Material Icons': 'MaterialIcons-Regular.ttf'
    }

    def __init__(self):
        self.fonts = {}
        self._init_font_paths()
        self._load_fonts()
        self._setup_font_objects()

    def _init_font_paths(self):
        self.font_paths = {}
        for font_name, file_name in self.FONT_FILES.items():
            folder = 'icons' if 'Material' in font_name else 'font'
            path = resource_path(os.path.join("core", "font", folder, file_name))
            self.font_paths[font_name] = path

    def _load_fonts(self):
        font_db = QFontDatabase()
        loaded_fonts = set()
        
        def load_single_font(font_name, path):
            try:
                if os.path.exists(path):
                    font_id = font_db.addApplicationFont(path)
                    if font_id >= 0:
                        families = font_db.applicationFontFamilies(font_id)
                        if families:
                            return {
                                'success': True,
                                'family': families[0],
                                'id': font_id
                            }
                return {'success': False, 'error': '字体文件不存在'}
            except Exception as e:
                return {'success': False, 'error': str(e)}
        
        # 批量提交任务
        tasks = {}
        batch_size = 4  # 每批处理的字体数量
        current_batch = []
        
        for font_name, path in self.font_paths.items():
            current_batch.append((font_name, path))
            
            if len(current_batch) >= batch_size:
                for name, p in current_batch:
                    task_id = f"load_font_{name}"
                    future = thread_manager.submit_task(
                        task_id,
                        load_single_font,
                        name,
                        p
                    )
                    tasks[name] = future
                current_batch = []
        
        # 处理剩余的字体
        if current_batch:
            for name, p in current_batch:
                task_id = f"load_font_{name}"
                future = thread_manager.submit_task(
                    task_id,
                    load_single_font,
                    name,
                    p
                )
                tasks[name] = future
        
        # 收集结果
        for font_name, future in tasks.items():
            try:
                result = future.result(timeout=5)
                if result['success']:
                    loaded_fonts.add(result['family'])
                    log.info(f"字体加载成功: {font_name}")
                else:
                    log.error(f"字体加载失败 {font_name}: {result['error']}")
            except Exception as e:
                log.error(f"等待字体加载结果失败 {font_name}: {str(e)}")
        
        self._handle_fallbacks(loaded_fonts)

    def _handle_fallbacks(self, loaded_fonts):
        # 如果字体已经成功加载，就不需要使用备选字体
        if 'HarmonyOS Sans SC' in loaded_fonts:
            self.FONT_CONFIGS['default']['primary'] = 'HarmonyOS Sans SC'
            return
            
        # 只有在字体加载失败时才使用备选字体
        system = platform.system()
        fallbacks = self.FONT_CONFIGS['fallback'].get(system, {})
        self.FONT_CONFIGS['default']['primary'] = fallbacks.get('chinese')
        log.info(f"使用备选中文字体: {fallbacks.get('chinese')}")
            
        if 'Mulish' not in loaded_fonts:
            self.FONT_CONFIGS['default']['secondary'] = fallbacks.get('english')
            log.info(f"使用备选英文字体: {fallbacks.get('english')}")

    def _setup_font_objects(self):
        fonts = self.FONT_CONFIGS['default']
        
        self.title_font = self._create_font([fonts['primary'], fonts['secondary'], fonts['icon']], 36, QFont.Weight.Bold)
        self.subtitle_font = self._create_font([fonts['primary'], fonts['secondary']], 16, QFont.Weight.Medium)
        self.normal_font = self._create_font([fonts['primary'], fonts['secondary'], fonts['icon']], 14)
        self.small_font = self._create_font([fonts['primary'], fonts['secondary'], fonts['icon']], 13)
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
            log.warning(f"字体名称必须是字符串类型")
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
        font_manager = FontManager()
        return font_manager.get_icon_text(icon_name)

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

from PySide6.QtGui import QFont, QFontDatabase, QColor
from PySide6.QtWidgets import QWidget, QApplication, QLabel, QPushButton
from PySide6.QtCore import Qt, QThread, Signal
import platform
import re
import os
import sys
from core.log.log_manager import log
from .icon_map import ICON_MAP
from core.thread.thread_manager import thread_manager

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        # Anti Packaged
        base_path = sys._MEIPASS
    else:
        # Dev
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class FontLoaderThread(QThread):
    finished = Signal(dict)  # 修改为返回字典，包含更多信息
    progress = Signal(str, int)  # 添加进度百分比
    
    def __init__(self, fonts_to_load):
        super().__init__()
        self.fonts_to_load = fonts_to_load
        
    def run(self):
        font_db = QFontDatabase()
        loaded_fonts = {}
        total = len(self.fonts_to_load)
        
        def load_single_font(font_path, font_name):
            try:
                if os.path.exists(font_path):
                    font_id = font_db.addApplicationFont(font_path)
                    if font_id >= 0:
                        return {
                            'success': True,
                            'name': font_name,
                            'id': font_id,
                            'families': font_db.applicationFontFamilies(font_id)
                        }
                return {'success': False, 'name': font_name, 'error': '字体文件不存在'}
            except Exception as e:
                return {'success': False, 'name': font_name, 'error': str(e)}

        # 创建任务列表
        tasks = {}
        for i, (font_path, font_name) in enumerate(self.fonts_to_load):
            task_id = f"font_load_{font_name}_{i}"
            future = thread_manager.submit_task(
                task_id,
                load_single_font,
                font_path,
                font_name
            )
            tasks[task_id] = (future, font_name)
            self.progress.emit(f"提交字体加载任务: {font_name}", int((i + 1) * 50 / total))

        # 收集结果
        for i, (task_id, (future, font_name)) in enumerate(tasks.items()):
            try:
                result = future.result(timeout=3)  # 3秒超时
                loaded_fonts[font_name] = result
                self.progress.emit(
                    f"完成字体加载: {font_name}", 
                    int(50 + (i + 1) * 50 / total)
                )
            except Exception as e:
                loaded_fonts[font_name] = {
                    'success': False,
                    'name': font_name,
                    'error': f'加载超时: {str(e)}'
                }
                
        self.finished.emit(loaded_fonts)

class FontManager:
    _instance = None
    _initialized = False
    _fonts_loaded = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FontManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not FontManager._initialized:
            self._init_basic_fonts()
            FontManager._initialized = True
    
    def _init_basic_fonts(self):
        # 基础字体配置
        self.hmsans_fonts = "HarmonyOS_Sans_SC"
        self.hmsans_fonts_bold = "HarmonyOS_Sans_SC_Bold"
        self.mulish_font = "Mulish"
        self.mulish_bold = "Mulish-Bold"
        self.material_font = "Material Icons"
        
        # 获取字体路径
        self.icon_font_path = resource_path(os.path.join("core", "font", "icons", "MaterialIcons-Regular.ttf"))
        self.hmsans_font_path = resource_path(os.path.join("core", "font", "font", "HarmonyOS_Sans_SC_Regular.ttf"))
        self.hmsans_bold_path = resource_path(os.path.join("core", "font", "font", "HarmonyOS_Sans_SC_Bold.ttf"))
        self.mulish_font_path = resource_path(os.path.join("core", "font", "font", "Mulish-Regular.ttf"))
        self.mulish_bold_path = resource_path(os.path.join("core", "font", "font", "Mulish-Bold.ttf"))
        
        # 先加载图标字体，因为这个是必需的
        font_db = QFontDatabase()
        if os.path.exists(self.icon_font_path):
            font_id = font_db.addApplicationFont(self.icon_font_path)
            if font_id >= 0:
                log.info("加载图标字体成功")
                
        # 同步加载其他字体
        self._load_fonts_sync()
    
    def _load_fonts_sync(self):
        """同步加载字体"""
        log.info("开始同步加载字体")
        font_db = QFontDatabase()
        fonts_to_load = [
            (self.mulish_font_path, "Mulish Regular"),
            (self.mulish_bold_path, "Mulish Bold"), 
            (self.hmsans_font_path, "HarmonyOS Sans SC Regular"),
            (self.hmsans_bold_path, "HarmonyOS Sans SC Bold"),
        ]
        
        for font_path, font_name in fonts_to_load:
            try:
                if os.path.exists(font_path):
                    font_id = font_db.addApplicationFont(font_path)
                    if font_id >= 0:
                        log.info(f"同步加载字体成功: {font_name}")
                    else:
                        log.error(f"同步加载字体失败: {font_name}")
                else:
                    log.error(f"字体文件不存在: {font_path}")
            except Exception as e:
                log.error(f"加载字体出错 {font_name}: {str(e)}")
        
        FontManager._fonts_loaded = True
        log.info("字体同步加载完成")

    def _get_background_color(self, widget):
        # QApplication 默认使用亮色主题
        if isinstance(widget, QApplication):
            return True
        
        # 获取背景色
        bg_color = widget.palette().color(widget.backgroundRole())
        
        # 背景透明时的处理
        if bg_color.alpha() == 0:
            parent = widget
            while parent:
                style = parent.styleSheet()
                if "background-color:" in style:
                    color_match = re.search(r'background-color:\s*(.*?)(;|$)', style)
                    if color_match:
                        color_str = color_match.group(1).strip().lower()
                        
                        # 处理颜色关键字
                        color_keywords = {
                            'white': True,
                            'black': False,
                            'transparent': True  # 透明默认当作亮色处理
                        }
                        if color_str in color_keywords:
                            return color_keywords[color_str]
                        
                        # 处理 rgb/rgba 格式
                        if color_str.startswith('rgb'):
                            rgb_match = re.search(r'(\d+)\s*,\s*(\d+)\s*,\s*(\d+)', color_str)
                            if rgb_match:
                                r, g, b = map(int, rgb_match.groups())
                                return (r * 299 + g * 587 + b * 114) / 1000 > 128
                                
                        # 处理十六进制格式
                        if color_str.startswith('#'):
                            r = int(color_str[1:3], 16) if len(color_str) >= 3 else 255
                            g = int(color_str[3:5], 16) if len(color_str) >= 5 else 255
                            b = int(color_str[5:7], 16) if len(color_str) >= 7 else 255
                            return (r * 299 + g * 587 + b * 114) / 1000 > 128
                            
                parent = parent.parentWidget()
                
            return True  # 找不到背景色时默认为亮色
            
        # 计算亮度 (使用感知亮度公式)
        return (bg_color.red() * 299 + bg_color.green() * 587 + bg_color.blue() * 114) / 1000 > 128
            
    def _create_optimized_font(self, is_bold=False):
        font = QFont()
        # 设置字体族优先级：中文用 HarmonyOS_Sans_SC，英文用 Mulish
        font.setFamilies([
            self.hmsans_fonts_bold if is_bold else self.hmsans_fonts,  # 中文字体优先
            self.mulish_bold if is_bold else self.mulish_font,     # 英文字体其次
            self.material_font                                      # 图标字体最后
        ])
        
        # 设置字体渲染选项
        font.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
        font.setStyleStrategy(
            QFont.StyleStrategy.PreferAntialias |
            QFont.StyleStrategy.PreferQuality
        )
        
        # 设置字体属性
        font.setKerning(True)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 0.3)
        font.setWeight(QFont.Weight.Bold if is_bold else QFont.Weight.Medium)
        font.setPixelSize(16)
        
        return font

    def create_icon_font(self, size=24):
        font = QFont(self.material_font)
        font.setPixelSize(size)
        return font

    def get_icon_text(self, icon_name):
        return ICON_MAP.get(icon_name, '')

    def apply_font(self, widget):
        if isinstance(widget, (QWidget, QApplication)):
            # 使用优化后的字体配置
            font = self._create_optimized_font()
            
            if isinstance(widget, QApplication):
                widget.setFont(font)
                # 为整个应用设置基础样式
                widget.setStyleSheet("""
                    QWidget {
                        color: #333333;
                        background-color: transparent;
                    }
                    QLabel, QPushButton {
                        background-color: transparent;
                    }
                """)
            else:
                widget.setFont(font)
                
                # 获取当前控件的样式表
                current_style = widget.styleSheet()
                
                # 构建新的样式
                new_styles = []
                
                # 保持原有的自定义样式
                if current_style:
                    new_styles.append(current_style)
                
                # 添加背景透明
                if not "background-color:" in current_style:
                    new_styles.append("background-color: transparent;")
                
                # 根据背景设置文字颜色
                is_light_background = self._get_background_color(widget)
                if is_light_background:
                    new_styles.append("color: #333333;")
                else:
                    new_styles.append("color: #FFFFFF;")
                
                # 应用组合后的样式
                widget.setStyleSheet("\n".join(new_styles))
                
                # 如果是特定类型的控件，确保背景透明
                if isinstance(widget, (QLabel, QPushButton)):
                    widget.setAttribute(Qt.WA_TranslucentBackground)
                
        else:
            raise TypeError("不支持的类型,只能应用到QWidget或QApplication ")

    def apply_icon_font(self, widget, size=24):
        if isinstance(widget, (QWidget, QLabel)):
            icon_font = self.create_icon_font(size)
            widget.setFont(icon_font)
        else:
            raise TypeError("不支持的类型,只能应用到QWidget或QLabel ")


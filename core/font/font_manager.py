from PySide6.QtGui import QFont, QFontDatabase, QColor
from PySide6.QtWidgets import QWidget, QApplication, QLabel, QPushButton
from PySide6.QtCore import Qt
import platform
import re
import os
import sys
from core.log.log_manager import log

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        # Anti Packaged
        base_path = sys._MEIPASS
    else:
        # Dev
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class FontManager:
    def __init__(self):
        self.hmsans_fonts = "HarmonyOS_Sans_SC"
        self.hmsans_fonts_bold = "HarmonyOS_Sans_SC_Bold"
        self.mulish_font = "Mulish"
        self.mulish_bold = "Mulish-Bold"
        self.material_font = "Material Icons"
        
        # 使用 resource_path 获取字体文件路径
        self.icon_font_path = resource_path(os.path.join("core", "font", "icons", "MaterialIcons-Regular.ttf"))
        self.hmsans_font_path = resource_path(os.path.join("core", "font", "font", "HarmonyOS_Sans_SC_Regular.ttf"))
        self.hmsans_bold_path = resource_path(os.path.join("core", "font", "font", "HarmonyOS_Sans_SC_Bold.ttf"))
        self.mulish_font_path = resource_path(os.path.join("core", "font", "font", "Mulish-Regular.ttf"))
        self.mulish_bold_path = resource_path(os.path.join("core", "font", "font", "Mulish-Bold.ttf"))
        
        # 加载字体文件
        self._load_fonts()
        self._init_fonts()
        
    def _load_fonts(self):
        font_db = QFontDatabase()
        
        # 先加载 Mulish 字体
        if os.path.exists(self.mulish_font_path):
            mulish_id = font_db.addApplicationFont(self.mulish_font_path)
            if mulish_id < 0:
                log.error("Mulish 常规字体加载失败")
                return
        
        if os.path.exists(self.mulish_bold_path):
            mulish_bold_id = font_db.addApplicationFont(self.mulish_bold_path)
            if mulish_bold_id < 0:
                log.error("Mulish Bold字体加载失败")
                return
                
        # 加载其他字体
        if os.path.exists(self.hmsans_font_path):
            hmsans_id = font_db.addApplicationFont(self.hmsans_font_path)
            if hmsans_id < 0:
                log.error("HarmonyOS_Sans_SC 常规字体加载失败")
                
        if os.path.exists(self.hmsans_bold_path):
            hmsans_bold_id = font_db.addApplicationFont(self.hmsans_bold_path)
            if hmsans_bold_id < 0:
                log.error("HarmonyOS_Sans_SC Bold字体加载失败")
                
        if os.path.exists(self.icon_font_path):
            icon_id = font_db.addApplicationFont(self.icon_font_path)
            if icon_id < 0:
                log.error("Material Icons 字体加载失败")

    def _init_fonts(self):
        # 获取系统类型
        system = platform.system()
        
        # 使用新的推荐方式创建 QFontDatabase
        font_db = QFontDatabase
        
        # 加载所有字体
        icon_font_id = QFontDatabase.addApplicationFont(self.icon_font_path)
        if icon_font_id < 0:
            log.warning("Material Icons 字体加载失败")
            
        hmsans_font_id = QFontDatabase.addApplicationFont(self.hmsans_font_path)
        if hmsans_font_id < 0:
            log.warning("HarmonyOS_Sans_SC 字体加载失败")
        
        hmsans_bold_id = QFontDatabase.addApplicationFont(self.hmsans_bold_path)
        if hmsans_bold_id < 0:
            log.warning("HarmonyOS_Sans_SC Bold 字体加载失败")
        
        mulish_font_id = QFontDatabase.addApplicationFont(self.mulish_font_path)
        if mulish_font_id < 0:
            log.warning("Mulish 字体加载失败")
        
        mulish_bold_id = QFontDatabase.addApplicationFont(self.mulish_bold_path)
        if mulish_bold_id < 0:
            log.warning("Mulish Bold 字体加载失败")

        available_fonts = font_db.families()
        
        if self.hmsans_fonts not in available_fonts:
            self.hmsans_fonts = "HarmonyOS_Sans_SC"  # 思源黑体,开源免费商用
        if self.mulish_font not in available_fonts:
            self.mulish_font = "Roboto"  # Roboto字体,开源免费商用
        
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
        # 统一图标映射
        icon_map = {
            'home': '\ue88a',
            'settings': '\ue8b8',
            'close': '\ue5cd',
            'menu': '\ue5d2',
            'arrow_back': '\ue5c4',
            'arrow_forward': '\ue5c8',
            'refresh': '\ue5d5',
            'search': '\ue8b6',
            'info': '\ue88e',
            'warning': '\ue002',
            'error': '\ue000',
            'success': '\ue86c',
            'article': '\uef42',
            'history': '\ue889',
            'code': '\ue86f',
            'gavel': '\ue90e',
            'shield': '\ue9e9',
            'dashboard': '\ue871',
            'person': '\ue7fd',
            'folder': '\ue2c7',
            'description': '\ue873',
            'bug_report': '\ue868',
            'build': '\ue869',
        }
        return icon_map.get(icon_name, '')

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


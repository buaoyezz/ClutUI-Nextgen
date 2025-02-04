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
        # PyInstaller 打包后的路径
        base_path = sys._MEIPASS
    else:
        # 开发环境的路径
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class FontManager:
    def __init__(self):
        # 使用 resource_path 获取字体文件路径
        self.icon_font_path = resource_path(os.path.join("core", "font", "icons", "MaterialIcons-Regular.ttf"))
        # 如果找不到上面的路径，尝试根目录
        if not os.path.exists(self.icon_font_path):
            self.icon_font_path = resource_path("MaterialIcons-Regular.ttf")
            
        if not os.path.exists(self.icon_font_path):
            raise FileNotFoundError(f"找不到字体文件: {self.icon_font_path}")

        self.chinese_font = "Microsoft YaHei"  # 换成更现代的微软雅黑UI
        self.english_font = "Arial"
        self.symbol_font = "Segoe UI"
        self.material_font = "Material Icons"  # 添加 Material Icons 字体支持

        self._init_fonts()
        
    def _init_fonts(self):
        # 获取系统类型
        system = platform.system()
        
        # 使用新的推荐方式创建 QFontDatabase
        font_db = QFontDatabase
        
        # 加载 Material Icons 字体
        font_id = QFontDatabase.addApplicationFont(self.icon_font_path)
        if font_id < 0:
            log.warning("Material Icons 字体加载失败")
        
        available_fonts = font_db.families()
        
        if self.chinese_font not in available_fonts:
            self.chinese_font = "SimHei"
            
        if self.english_font not in available_fonts:
            self.english_font = "Arial"
            
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
            
    def _create_optimized_font(self):
        # 创建一个超级平滑的字体配置 
        font = QFont()
        font.setFamilies([self.chinese_font, self.english_font, self.symbol_font])
        
        # 设置最强渲染参数
        font.setHintingPreference(QFont.HintingPreference.PreferNoHinting)  # 禁用 hinting 获得更平滑的轮廓
        font.setStyleStrategy(
            QFont.StyleStrategy.PreferAntialias |  # 抗锯齿
            QFont.StyleStrategy.PreferQuality |    # 优先质量
            QFont.StyleStrategy.ForceOutline       # 强制使用轮廓渲染
        )
        
        # 优化字体显示参数 
        font.setKerning(True)                      # 启用字距调整
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 0.6)  # 绝对字距
        font.setWeight(QFont.Weight.Medium)        # 适中的字重
        font.setPixelSize(16)                      # 默认像素大小
        
        return font

    def create_icon_font(self, size=24):
        """创建 Material Icons 字体"""
        font = QFont(self.material_font)
        font.setPixelSize(size)
        return font

    def get_icon_text(self, icon_name):
        """获取 Material Icons 字体对应的 Unicode 字符"""
        icon_map = {
            'home': '\ue88a',         # 主页图标
            'settings': '\ue8b8',     # 设置图标
            'close': '\ue5cd',        # 关闭图标
            'menu': '\ue5d2',         # 菜单图标
            'arrow_back': '\ue5c4',   # 返回箭头
            'arrow_forward': '\ue5c8', # 前进箭头
            'refresh': '\ue5d5',      # 刷新图标
            'search': '\ue8b6',       # 搜索图标
            'info': '\ue88e',         # 信息图标
            'warning': '\ue002',      # 警告图标
            'error': '\ue000',        # 错误图标
            'success': '\ue86c',      # 成功图标
            'article': '\uef42',      # 文章/日志图标
            'dashboard': '\ue871',    # 仪表盘图标
            'person': '\ue7fd',       # 用户图标
            'folder': '\ue2c7',       # 文件夹图标
            'description': '\ue873',  # 描述/文档图标
            'code': '\ue86f',         # 代码图标
            'bug_report': '\ue868',   # Bug报告图标
            'build': '\ue869',        # 构建/工具图标
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
        """应用 Material Icons 字体到控件"""
        if isinstance(widget, (QWidget, QLabel)):
            icon_font = self.create_icon_font(size)
            widget.setFont(icon_font)
        else:
            raise TypeError("不支持的类型,只能应用到QWidget或QLabel ")


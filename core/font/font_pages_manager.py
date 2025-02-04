# 字体管理器 -Pages

from PySide6.QtGui import QFont, QFontDatabase, QAction
from PySide6.QtWidgets import QWidget, QApplication, QLabel
from PySide6.QtCore import Qt
import platform
from core.log.log_manager import log

class FontPagesManager:
    """页面字体管理器"""
    
    def __init__(self):
        self.chinese_font = "Microsoft YaHei"  # 默认微软雅黑
        self.english_font = "Arial"
        self.symbol_font = "Segoe UI Symbol"
        self.material_font = "Material Icons"  # 添加 Material Icons 字体
        
        self._init_fonts()
        
        # 加载 Material Icons 字体
        font_id = QFontDatabase.addApplicationFont("core/font/icons/MaterialIcons-Regular.ttf")
        if font_id < 0:
            log.warning("Material Icons 字体加载失败")
        
        # 默认字体配置
        self.title_font = QFont("Microsoft YaHei", 24, QFont.Bold)  # 标题字体
        self.normal_font = QFont("Microsoft YaHei", 12)  # 普通文本字体
        self.small_font = QFont("Microsoft YaHei", 10)  # 小字体
        self.icon_font = QFont("Material Icons", 24)  # Material Icons 字体配置
        
    def _init_fonts(self):
        # 获取系统可用字体
        font_db = QFontDatabase
        available_fonts = font_db.families()
        
        # 检查并设置备选字体
        if self.chinese_font not in available_fonts:
            self.chinese_font = "SimHei"  # 备用黑体
            
        if self.english_font not in available_fonts:
            self.english_font = "Arial"
    
    def apply_font(self, widget, font_type="normal"):
        """应用字体到控件"""
        try:
            if isinstance(widget, (QWidget, QLabel, QAction)):  # 添加 QAction 支持
                if font_type == "title":
                    widget.setFont(self.title_font)
                elif font_type == "small":
                    widget.setFont(self.small_font)
                else:
                    widget.setFont(self.normal_font)
            else:
                log.warning(f"不支持的控件类型: {type(widget)}")
                
        except Exception as e:
            log.error(f"应用字体失败: {str(e)}")
            
    def apply_title_style(self, widget):
        """应用标题字体"""
        self.apply_font(widget, "title")
        
    def apply_normal_style(self, widget):
        """应用普通字体"""
        self.apply_font(widget, "normal")
        
    def apply_small_style(self, widget):
        """应用小字体"""
        self.apply_font(widget, "small")

    def apply_font_only(self, widget):
        """
        只应用字体，不设置任何颜色
        """
        if isinstance(widget, (QWidget, QApplication)):
            font = QFont()
            font.setFamilies([self.chinese_font, self.english_font, self.symbol_font])
            font.setHintingPreference(QFont.HintingPreference.PreferFullHinting)
            font.setStyleStrategy(
                QFont.StyleStrategy.PreferAntialias | 
                QFont.StyleStrategy.PreferQuality
            )
            font.setKerning(True)
            font.setLetterSpacing(QFont.SpacingType.PercentageSpacing, 100)
            font.setWeight(QFont.Weight.Medium)
            
            if isinstance(widget, QApplication):
                widget.setFont(font)
            else:
                widget.setFont(font)
        else:
            raise TypeError("不支持的类型,只能应用到QWidget或QApplication ")

    def apply_subtitle_style(self, widget):
        """为子标题设置样式喵"""
        # 先应用基础字体
        self.apply_font(widget)
        
        # 创建子标题专用字体
        font = widget.font()
        font.setPointSize(16)  # 子标题大小
        font.setWeight(QFont.Weight.Medium)  # 设置字重
        widget.setFont(font)
        
        # 设置子标题样式
        widget.setStyleSheet("""
            QLabel {
                color: #4A5568;
                margin: 5px 0;
            }
        """)

    def apply_icon_font(self, widget, size=24):
        """应用 Material Icons 字体"""
        try:
            if isinstance(widget, (QWidget, QLabel, QAction)):
                icon_font = QFont(self.material_font)
                icon_font.setPixelSize(size)
                widget.setFont(icon_font)
            else:
                log.warning(f"不支持的控件类型: {type(widget)}")
                
        except Exception as e:
            log.error(f"应用图标字体失败: {str(e)}")
            
    def get_icon_text(self, icon_name):
        """获取 Material Icons 字体对应的 Unicode 字符"""
        icon_map = {
            'home': '',
            'settings': '',
            'close': '',
            'menu': '',
            'arrow_back': '',
            'arrow_forward': '',
            'refresh': '',
            'search': '',
            'info': '',
            'warning': '',
            'error': '',
            'success': '',
            # 可以继续添加更多图标映射
        }
        return icon_map.get(icon_name, '')

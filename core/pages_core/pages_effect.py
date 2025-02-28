from PySide6.QtWidgets import QWidget, QGraphicsBlurEffect, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QColor, QPainterPath
import win32gui
import win32con
import win32api
import ctypes

class PagesEffect:
    @staticmethod
    def apply_mica_effect(widget: QWidget):
        # 获取窗口句柄
        hwnd = widget.winId()
        
        # 设置窗口背景透明
        widget.setAttribute(Qt.WA_TranslucentBackground)
        
        # 获取主窗口部件
        main_widget = widget.findChild(QWidget, "mainWidget")
        if main_widget:
            # 更新样式表以支持Mica效果
            main_widget.setStyleSheet("""
                QWidget#mainWidget {
                    background-color: rgba(255, 255, 255, 220);
                    border-radius: 8px;
                    border: 1px solid rgba(32, 32, 32, 0.1);
                }
            """)
        
        # 定义DWMWINDOWATTRIBUTE枚举值
        DWMWA_SYSTEMBACKDROP_TYPE = 38
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        DWMWA_MICA_EFFECT = 1029
        DWMWA_BORDER_COLOR = 34
        DWMWA_CAPTION_COLOR = 35
        DWMAPI = ctypes.WinDLL("dwmapi")
        
        # 禁用深色模式
        dark_mode = 0
        DWMAPI.DwmSetWindowAttribute(
            hwnd,
            DWMWA_USE_IMMERSIVE_DARK_MODE,
            ctypes.byref(ctypes.c_int(dark_mode)),
            ctypes.sizeof(ctypes.c_int)
        )
        
        # 设置Mica效果
        value = 2  # DWM_SYSTEMBACKDROP_TYPE.DWMSBT_MAINWINDOW
        DWMAPI.DwmSetWindowAttribute(
            hwnd,
            DWMWA_SYSTEMBACKDROP_TYPE,
            ctypes.byref(ctypes.c_int(value)),
            ctypes.sizeof(ctypes.c_int)
        )
        
        # 启用Mica材质
        try:
            mica_effect = 1
            DWMAPI.DwmSetWindowAttribute(
                hwnd,
                DWMWA_MICA_EFFECT,
                ctypes.byref(ctypes.c_int(mica_effect)),
                ctypes.sizeof(ctypes.c_int)
            )
        except:
            pass
        
        # 设置边框颜色
        border_color = 0x00FFFFFF  # 白色，半透明
        DWMAPI.DwmSetWindowAttribute(
            hwnd,
            DWMWA_BORDER_COLOR,
            ctypes.byref(ctypes.c_int(border_color)),
            ctypes.sizeof(ctypes.c_int)
        )
        
        # 设置标题栏颜色
        caption_color = 0x00FFFFFF  # 白色，半透明
        DWMAPI.DwmSetWindowAttribute(
            hwnd,
            DWMWA_CAPTION_COLOR,
            ctypes.byref(ctypes.c_int(caption_color)),
            ctypes.sizeof(ctypes.c_int)
        )
        
        # 刷新窗口
        win32gui.SetWindowPos(
            hwnd, 
            None, 
            0, 0, 0, 0,
            win32con.SWP_NOMOVE | 
            win32con.SWP_NOSIZE | 
            win32con.SWP_NOZORDER |
            win32con.SWP_FRAMECHANGED
        )
        
    @staticmethod
    def apply_gaussian_blur(widget: QWidget, radius: int = 15):  # 增加默认模糊半径
        # 创建模糊效果
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(radius)
        blur.setBlurHints(QGraphicsBlurEffect.QualityHint)
        
        # 设置窗口背景透明
        widget.setAttribute(Qt.WA_TranslucentBackground)
        
        # 获取主窗口部件
        main_widget = widget.findChild(QWidget, "mainWidget")
        if main_widget:
            # 更新样式表以支持模糊效果
            main_widget.setStyleSheet("""
                QWidget#mainWidget {
                    background-color: rgba(255, 255, 255, 160);
                    border-radius: 8px;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }
            """)
            
            # 应用模糊效果
            main_widget.setGraphicsEffect(blur)
        
    @staticmethod
    def apply_blur_effect(widget: QWidget):
        hwnd = widget.winId()
        
        # 设置窗口背景透明
        widget.setAttribute(Qt.WA_TranslucentBackground)
        
        # 获取主窗口部件
        main_widget = widget.findChild(QWidget, "mainWidget")
        if main_widget:
            # 更新样式表以支持Aero效果
            main_widget.setStyleSheet("""
                QWidget#mainWidget {
                    background-color: rgba(255, 255, 255, 200);
                    border-radius: 8px;
                    border: 1px solid rgba(255, 255, 255, 0.3);
                }
            """)
        
        # 定义Blur常量
        WCA_ACCENT_POLICY = 19
        
        class ACCENT_POLICY(ctypes.Structure):
            _fields_ = [
                ('AccentState', ctypes.c_uint),
                ('AccentFlags', ctypes.c_uint),
                ('GradientColor', ctypes.c_uint),
                ('AnimationId', ctypes.c_uint)
            ]

        class WINDOWCOMPOSITIONATTRIBDATA(ctypes.Structure):
            _fields_ = [
                ('Attribute', ctypes.c_int),
                ('Data', ctypes.POINTER(ACCENT_POLICY)),
                ('SizeOfData', ctypes.c_size_t)
            ]

        accent = ACCENT_POLICY()
        accent.AccentState = 3  # ACCENT_ENABLE_BLURBEHIND
        
        data = WINDOWCOMPOSITIONATTRIBDATA()
        data.Attribute = WCA_ACCENT_POLICY
        data.SizeOfData = ctypes.sizeof(accent)
        data.Data = ctypes.pointer(accent)
        
        user32 = ctypes.WinDLL("user32")
        SetWindowCompositionAttribute = user32.SetWindowCompositionAttribute
        SetWindowCompositionAttribute.argtypes = (ctypes.c_int, ctypes.POINTER(WINDOWCOMPOSITIONATTRIBDATA))
        SetWindowCompositionAttribute(int(hwnd), ctypes.byref(data))
        
    @staticmethod
    def remove_effects(widget: QWidget):
        # 移除所有效果
        hwnd = widget.winId()
        
        # 重置DWM属性
        DWMWA_SYSTEMBACKDROP_TYPE = 38
        DWMAPI = ctypes.WinDLL("dwmapi")
        
        value = 0  # DWM_SYSTEMBACKDROP_TYPE.DWMSBT_NONE
        DWMAPI.DwmSetWindowAttribute(
            hwnd,
            DWMWA_SYSTEMBACKDROP_TYPE,
            ctypes.byref(ctypes.c_int(value)),
            ctypes.sizeof(ctypes.c_int)
        )
        
        # 移除模糊效果
        main_widget = widget.findChild(QWidget, "mainWidget")
        if main_widget:
            main_widget.setGraphicsEffect(None)
            main_widget.setStyleSheet("""
                QWidget#mainWidget {
                    background-color: #F8F9FA;
                    border-radius: 8px;
                    border: 1px solid #E0E0E0;
                }
            """)
        
        # 刷新窗口
        win32gui.SetWindowPos(
            hwnd, 
            None, 
            0, 0, 0, 0,
            win32con.SWP_NOMOVE | 
            win32con.SWP_NOSIZE | 
            win32con.SWP_NOZORDER |
            win32con.SWP_FRAMECHANGED
        )

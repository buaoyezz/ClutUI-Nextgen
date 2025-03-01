from PySide6.QtWidgets import QWidget, QGraphicsBlurEffect, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PySide6.QtCore import Qt, QRect, QSize
from PySide6.QtGui import QPainter, QColor, QPainterPath, QBrush, QLinearGradient, QPixmap, QImage
import win32gui
import win32con
import win32api
import ctypes
import platform
import os
import random
import numpy as np

class PagesEffect:
    # 常量定义
    DWMWA_SYSTEMBACKDROP_TYPE = 38
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    DWMWA_MICA_EFFECT = 1029
    DWMWA_BORDER_COLOR = 34
    DWMWA_CAPTION_COLOR = 35
    WCA_ACCENT_POLICY = 19
    
    # 噪声纹理缓存
    _noise_texture = None
    
    @staticmethod
    def _get_main_widget(widget: QWidget) -> QWidget:
        """获取主窗口部件
        
        查找并返回名为"mainWidget"的子部件
        
        Args:
            widget: 要搜索的父部件
            
        Returns:
            QWidget: 找到的主窗口部件，如果未找到则返回None
        """
        if not widget:
            return None
            
        # 查找名为"mainWidget"的子部件
        main_widget = widget.findChild(QWidget, "mainWidget")
        return main_widget
    
    @staticmethod
    def _is_windows_11_or_later() -> bool:
        """检查当前系统是否为Windows 11或更高版本
        
        Returns:
            bool: 如果是Windows 11或更高版本则返回True，否则返回False
        """
        if platform.system() != 'Windows':
            return False
            
        try:
            # 获取Windows版本信息
            version = platform.version().split('.')
            build = int(version[2]) if len(version) > 2 else 0
            
            # Windows 11的构建版本号为22000或更高
            return build >= 22000
        except:
            return False
    
    @staticmethod
    def _generate_noise_texture(width=200, height=200, opacity=0.05):
        """生成噪声纹理图
        
        创建一个带有随机噪点的透明纹理图，用于增强亚克力效果
        
        Args:
            width: 纹理宽度
            height: 纹理高度
            opacity: 噪点不透明度 (0.0-1.0)
            
        Returns:
            QPixmap: 生成的噪声纹理
        """
        # 如果已经有缓存的纹理，直接返回
        if PagesEffect._noise_texture is not None:
            return PagesEffect._noise_texture
            
        # 创建透明图像
        image = QImage(width, height, QImage.Format_ARGB32)
        image.fill(Qt.transparent)
        
        # 获取图像数据
        for y in range(height):
            for x in range(width):
                # 生成随机噪点
                if random.random() < 0.3:  # 噪点密度
                    # 随机灰度值
                    gray = random.randint(200, 255)
                    # 设置像素颜色 (ARGB格式)
                    alpha = int(opacity * 255)
                    image.setPixelColor(x, y, QColor(gray, gray, gray, alpha))
        
        # 转换为QPixmap并缓存
        PagesEffect._noise_texture = QPixmap.fromImage(image)
        return PagesEffect._noise_texture
    
    @staticmethod
    def apply_mica_effect(widget: QWidget):
        """应用Windows 11 Mica效果
        
        此效果在Windows 11上提供半透明的桌面背景材质效果
        """
        # 检查参数有效性
        if not widget:
            return
            
        # 获取窗口句柄 - 修复为直接使用winId()而不是int(winId())
        hwnd = widget.winId()
        
        # 设置窗口背景透明
        widget.setAttribute(Qt.WA_TranslucentBackground)
        
        # 获取主窗口部件
        main_widget = PagesEffect._get_main_widget(widget)
        if main_widget:
            # 更新样式表以支持Mica效果
            main_widget.setStyleSheet("""
                QWidget#mainWidget {
                    background-color: rgba(255, 255, 255, 220);
                    border-radius: 8px;
                    border: 1px solid rgba(32, 32, 32, 0.1);
                }
            """)
        
        # 检查是否为Windows 11
        if not PagesEffect._is_windows_11_or_later():
            # 如果不是Windows 11，回退到模糊效果
            PagesEffect.apply_blur_effect(widget)
            return
        
        try:
            # 加载DWM API
            DWMAPI = ctypes.WinDLL("dwmapi")
            
            # 禁用深色模式
            dark_mode = 0
            DWMAPI.DwmSetWindowAttribute(
                hwnd,
                PagesEffect.DWMWA_USE_IMMERSIVE_DARK_MODE,
                ctypes.byref(ctypes.c_int(dark_mode)),
                ctypes.sizeof(ctypes.c_int)
            )
            
            # 设置Mica效果
            value = 2  # DWM_SYSTEMBACKDROP_TYPE.DWMSBT_MAINWINDOW
            DWMAPI.DwmSetWindowAttribute(
                hwnd,
                PagesEffect.DWMWA_SYSTEMBACKDROP_TYPE,
                ctypes.byref(ctypes.c_int(value)),
                ctypes.sizeof(ctypes.c_int)
            )
            
            # 启用Mica材质
            try:
                mica_effect = 1
                DWMAPI.DwmSetWindowAttribute(
                    hwnd,
                    PagesEffect.DWMWA_MICA_EFFECT,
                    ctypes.byref(ctypes.c_int(mica_effect)),
                    ctypes.sizeof(ctypes.c_int)
                )
            except Exception:
                # 如果不支持DWMWA_MICA_EFFECT，忽略错误
                pass
            
            # 设置边框颜色
            border_color = 0x00FFFFFF  # 白色，半透明
            DWMAPI.DwmSetWindowAttribute(
                hwnd,
                PagesEffect.DWMWA_BORDER_COLOR,
                ctypes.byref(ctypes.c_int(border_color)),
                ctypes.sizeof(ctypes.c_int)
            )
            
            # 设置标题栏颜色
            caption_color = 0x00FFFFFF  # 白色，半透明
            DWMAPI.DwmSetWindowAttribute(
                hwnd,
                PagesEffect.DWMWA_CAPTION_COLOR,
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
        except Exception as e:
            # 如果出现异常，回退到模糊效果
            PagesEffect.apply_blur_effect(widget)
        
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
        """应用Windows Aero模糊效果
        
        此效果使用Windows系统API实现，仅适用于Windows平台
        """
        # 检查参数有效性
        if not widget:
            return
            
        # 获取窗口句柄
        hwnd = widget.winId()
        
        # 设置窗口背景透明
        widget.setAttribute(Qt.WA_TranslucentBackground)
        
        # 获取主窗口部件
        main_widget = PagesEffect._get_main_widget(widget)
        if main_widget:
            # 移除之前的效果
            main_widget.setGraphicsEffect(None)
            
            # 更新样式表以支持Aero效果
            main_widget.setStyleSheet("""
                QWidget#mainWidget {
                    background-color: rgba(255, 255, 255, 200);
                    border-radius: 8px;
                    border: 1px solid rgba(255, 255, 255, 0.3);
                }
            """)
        
        try:
            # 定义Blur常量和结构体
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

            # 创建并配置ACCENT_POLICY
            accent = ACCENT_POLICY()
            accent.AccentState = 3  # ACCENT_ENABLE_BLURBEHIND
            
            # 创建并配置WINDOWCOMPOSITIONATTRIBDATA
            data = WINDOWCOMPOSITIONATTRIBDATA()
            data.Attribute = PagesEffect.WCA_ACCENT_POLICY
            data.SizeOfData = ctypes.sizeof(accent)
            data.Data = ctypes.pointer(accent)
            
            # 加载user32.dll并应用效果
            user32 = ctypes.WinDLL("user32")
            SetWindowCompositionAttribute = user32.SetWindowCompositionAttribute
            SetWindowCompositionAttribute.argtypes = (ctypes.c_int, ctypes.POINTER(WINDOWCOMPOSITIONATTRIBDATA))
            SetWindowCompositionAttribute(int(hwnd), ctypes.byref(data))
            
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
        except Exception as e:
            # 如果出现异常，回退到高斯模糊
            PagesEffect.apply_gaussian_blur(widget)
        
    @staticmethod
    def remove_effects(widget: QWidget):
        """移除所有应用的效果"""
        # 检查参数有效性
        if not widget:
            return
            
        # 获取窗口句柄
        hwnd = widget.winId()
        
        try:
            # 重置DWM属性
            DWMAPI = ctypes.WinDLL("dwmapi")
            
            value = 0  # DWM_SYSTEMBACKDROP_TYPE.DWMSBT_NONE
            DWMAPI.DwmSetWindowAttribute(
                hwnd, 
                PagesEffect.DWMWA_SYSTEMBACKDROP_TYPE, 
                ctypes.byref(ctypes.c_int(value)),
                ctypes.sizeof(ctypes.c_int)
            )
        except Exception:
            pass
            
        # 移除模糊效果
        main_widget = PagesEffect._get_main_widget(widget)
        if main_widget:
            # 移除图形效果
            main_widget.setGraphicsEffect(None)
            
            # 恢复原始的paintEvent（如果被修改过）
            if hasattr(main_widget, "_original_paint_event"):
                main_widget.paintEvent = main_widget._original_paint_event
                delattr(main_widget, "_original_paint_event")
            
            # 更新样式表
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

    @staticmethod
    def apply_aero_effect(widget: QWidget):
        """应用Windows Aero效果
        
        此效果使用Windows Vista/7的Aero Glass效果，适用于Windows平台
        """
        # 检查参数有效性
        if not widget:
            return
            
        # 获取窗口句柄
        hwnd = widget.winId()
        
        # 设置窗口背景透明
        widget.setAttribute(Qt.WA_TranslucentBackground)
        
        # 获取主窗口部件
        main_widget = PagesEffect._get_main_widget(widget)
        if main_widget:
            # 移除之前的效果
            main_widget.setGraphicsEffect(None)
            
            # 更新样式表以支持Aero效果
            main_widget.setStyleSheet("""
                QWidget#mainWidget {
                    background-color: rgba(255, 255, 255, 150);
                    border-radius: 8px;
                    border: 1px solid rgba(255, 255, 255, 0.5);
                }
            """)
        
        try:
            # 定义DWM边距结构体
            class MARGINS(ctypes.Structure):
                _fields_ = [
                    ("cxLeftWidth", ctypes.c_int),
                    ("cxRightWidth", ctypes.c_int),
                    ("cyTopHeight", ctypes.c_int),
                    ("cyBottomHeight", ctypes.c_int)
                ]
            
            # 加载DWM API
            DWMAPI = ctypes.WinDLL("dwmapi")
            
            # 启用DWM扩展框架
            DWMAPI.DwmExtendFrameIntoClientArea.argtypes = [
                ctypes.c_int, 
                ctypes.POINTER(MARGINS)
            ]
            
            # 创建边距，-1表示整个窗口
            margins = MARGINS(-1, -1, -1, -1)
            
            # 扩展框架到客户区
            DWMAPI.DwmExtendFrameIntoClientArea(
                int(hwnd),
                ctypes.byref(margins)
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
        except Exception as e:
            # 如果出现异常，回退到模糊效果
            PagesEffect.apply_blur_effect(widget)

    @staticmethod
    def apply_acrylic_effect(widget: QWidget):
        """应用Windows 11 Acrylic效果
        
        此效果在Windows 11上提供亚克力材质效果，添加噪声纹理提高质量
        """
        # 检查参数有效性
        if not widget:
            return
            
        # 获取窗口句柄
        hwnd = widget.winId()
        
        # 设置窗口背景透明
        widget.setAttribute(Qt.WA_TranslucentBackground)
        
        # 生成噪声纹理
        noise_texture = PagesEffect._generate_noise_texture()
        
        # 获取主窗口部件
        main_widget = PagesEffect._get_main_widget(widget)
        if main_widget:
            # 移除之前的效果
            main_widget.setGraphicsEffect(None)
            
            # 设置噪声纹理作为背景
            main_widget.setAutoFillBackground(False)
            
            # 保存原始的绘制事件
            main_widget._original_paint_event = main_widget.paintEvent
            
            def custom_paint_event(event):
                # 不要直接调用原始的paintEvent，这会导致递归
                # 而是调用QWidget的默认paintEvent实现
                QWidget.paintEvent(main_widget, event)
                
                # 在原始绘制之上叠加噪声纹理
                painter = QPainter(main_widget)
                painter.setOpacity(0.03)  # 设置噪声纹理的透明度
                
                # 平铺绘制噪声纹理
                for x in range(0, main_widget.width(), noise_texture.width()):
                    for y in range(0, main_widget.height(), noise_texture.height()):
                        painter.drawPixmap(x, y, noise_texture)
                
                painter.end()
            
            # 替换绘制事件
            main_widget.paintEvent = custom_paint_event
            
            # 更新样式表以支持Acrylic效果
            main_widget.setStyleSheet("""
                QWidget#mainWidget {
                    background-color: rgba(255, 255, 255, 180);
                    border-radius: 8px;
                    border: 1px solid rgba(255, 255, 255, 0.4);
                }
            """)
        
        # 检查是否为Windows 11
        if not PagesEffect._is_windows_11_or_later():
            # 如果不是Windows 11，回退到模糊效果
            PagesEffect.apply_blur_effect(widget)
            return
            
        try:
            # 加载DWM API
            DWMAPI = ctypes.WinDLL("dwmapi")
            
            # 设置Acrylic效果
            value = 3  # DWM_SYSTEMBACKDROP_TYPE.DWMSBT_TRANSIENTWINDOW (Acrylic)
            DWMAPI.DwmSetWindowAttribute(
                hwnd,
                PagesEffect.DWMWA_SYSTEMBACKDROP_TYPE,
                ctypes.byref(ctypes.c_int(value)),
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
        except Exception as e:
            # 如果出现异常，回退到模糊效果
            PagesEffect.apply_blur_effect(widget)
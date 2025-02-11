from core.ui.card_white import CardWhite
from PySide6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QWidget, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QColor, QDesktopServices
from core.font.font_pages_manager import FontPagesManager
from PySide6.QtCore import QUrl
import time
import os

class ImageLabel(QLabel):
    def __init__(self, pixmap, original_path=None, parent=None):
        super().__init__(parent)
        self.original_path = original_path
        self.setPixmap(pixmap)
        self.setAlignment(Qt.AlignCenter)
        
    def mouseDoubleClickEvent(self, event):
        if self.original_path and os.path.exists(self.original_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.original_path))
        elif self.pixmap():
            # 如果没有原始路径，保存临时文件并打开
            temp_path = os.path.join(os.path.expanduser("~"), ".cache", "clutui_temp.png")
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            self.pixmap().save(temp_path, "PNG")
            QDesktopServices.openUrl(QUrl.fromLocalFile(temp_path))

class CommentCard(CardWhite):
    def __init__(self, comment_text, images=None, user_name="用户", parent=None):
        super().__init__(
            title="",  
            description="",
            parent=parent,
            show_buttons=['点赞', '评论', '转发'] 
        )
        self.user_name = user_name
        self.comment_text = comment_text
        self.images = images if images is not None else []
        self.font_pages_manager = FontPagesManager()
        
        self.setGraphicsEffect(None)
        
        # 设置卡片样式
        self.setStyleSheet("""
            CommentCard {
                background: #FFFFFF;
                border-radius: 8px;
                border: 1px solid #E0E0E0;
                max-width: 850px;
            }
            CommentCard:hover {
                border: 1px solid #2196F3;
            }
        """)
        
        self.setup_comment_ui()
        
    def setup_comment_ui(self):
        # 获取主布局
        main_layout = self.layout()
        
        # 创建新的标题容器
        title_container = QHBoxLayout()
        title_container.setSpacing(12)  # 增加箭头和内容之间的间距
        
        # 获取并移动箭头
        arrow_label = self.findChild(QLabel, "arrow_label")
        if arrow_label:
            arrow_label.setParent(None)
            title_container.addWidget(arrow_label)
        
        # 创建内容容器
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(8)
        
        # 用户信息行
        user_info = QWidget()
        user_layout = QHBoxLayout(user_info)
        user_layout.setContentsMargins(0, 0, 0, 8)
        user_layout.setSpacing(8)
        
        # 用户头像
        avatar = QLabel()
        avatar.setFixedSize(32, 32)
        avatar.setStyleSheet("""
            background: #E0E0E0;
            border-radius: 16px;
        """)
        
        # 用户信息
        info_container = QWidget()
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)
        
        name_label = QLabel(self.user_name)
        self.font_pages_manager.apply_normal_style(name_label)
        name_label.setStyleSheet("""
            color: #333333;
            font-weight: bold;
            font-size: 14px;
        """)
        
        time_label = QLabel(time.strftime("%Y-%m-%d %H:%M"))
        self.font_pages_manager.apply_small_style(time_label)
        time_label.setStyleSheet("color: #999999;")
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(time_label)
        
        user_layout.addWidget(avatar)
        user_layout.addWidget(info_container)
        user_layout.addStretch()
        
        # 评论内容
        comment_label = QLabel(self.comment_text)
        comment_label.setWordWrap(True)
        self.font_pages_manager.apply_normal_style(comment_label)
        comment_label.setStyleSheet("""
            color: #333333;
            padding: 0px;
            margin: 0px;
        """)
        
        content_layout.addWidget(user_info)
        content_layout.addWidget(comment_label)
        
        # 添加图片区域
        if self.images:
            image_container = QWidget()
            image_layout = QHBoxLayout(image_container)
            image_layout.setContentsMargins(0, 8, 0, 0)
            image_layout.setSpacing(8)
            
            # 计算要显示的图片数量
            max_images = 4  # 最多显示4张图片
            total_images = len(self.images)
            display_images = self.images[:max_images]
            
            for i, pixmap in enumerate(display_images):
                if isinstance(pixmap, QPixmap) and not pixmap.isNull():
                    # 使用更高质量的缩放方式
                    # 先缩放到中间尺寸
                    intermediate_pixmap = pixmap.scaled(
                        480, 480,  # 先缩放到更大的尺寸
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    
                    # 再缩放到最终显示尺寸
                    final_pixmap = intermediate_pixmap.scaled(
                        120, 120,  # 最终显示尺寸
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    
                    # 创建图片容器
                    image_container_widget = QWidget()
                    image_container_widget.setFixedSize(120, 120)
                    image_container_layout = QVBoxLayout(image_container_widget)
                    image_container_layout.setContentsMargins(0, 0, 0, 0)
                    image_container_layout.setSpacing(0)
                    
                    # 使用自定义的ImageLabel
                    image_label = ImageLabel(final_pixmap, None)
                    image_label.setFixedSize(120, 120)
                    
                    # 如果是最后一张显示的图片且还有更多图片
                    if i == max_images - 1 and total_images > max_images:
                        # 创建半透明遮罩
                        overlay = QLabel()
                        overlay.setFixedSize(120, 120)
                        overlay.setAlignment(Qt.AlignCenter)
                        self.font_pages_manager.apply_subtitle_style(overlay)
                        overlay.setText(f"+{total_images - max_images}")
                        overlay.setStyleSheet("""
                            QLabel {
                                background: rgba(0, 0, 0, 0.5);
                                color: white;
                                border-radius: 4px;
                                font-size: 24px;
                                font-weight: bold;
                            }
                        """)
                        overlay.raise_()
                        
                        # 将遮罩添加到图片上
                        image_container_layout.addWidget(overlay)
                    
                    image_label.setStyleSheet("""
                        QLabel {
                            border-radius: 4px;
                            background: white;
                            border: 1px solid #E0E0E0;
                            padding: 2px;
                        }
                        QLabel:hover {
                            border: 1px solid #2196F3;
                            background: #F5F5F5;
                        }
                    """)
                    
                    image_container_layout.addWidget(image_label)
                    image_layout.addWidget(image_container_widget)
            
            image_layout.addStretch()
            content_layout.addWidget(image_container)
        
        # 将内容添加到标题容器
        title_container.addWidget(content_widget)
        title_container.addStretch()
        
        # 替换原有的标题布局
        old_title_layout = main_layout.itemAt(0).layout()
        if old_title_layout:
            while old_title_layout.count():
                item = old_title_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            # 添加新的标题布局
            for i in range(title_container.count()):
                item = title_container.itemAt(i)
                if item.widget():
                    old_title_layout.addWidget(item.widget())
                elif item.spacerItem():
                    old_title_layout.addStretch() 
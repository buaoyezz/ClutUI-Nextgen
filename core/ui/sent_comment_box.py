from PySide6.QtWidgets import (QFrame, QLabel, QVBoxLayout, QGraphicsDropShadowEffect,
                             QHBoxLayout, QWidget, QPushButton, QTextEdit, QFileDialog,
                             QMenu, QGridLayout, QScrollArea)
from PySide6.QtCore import Qt, Signal, QMimeData, QSize
from PySide6.QtGui import QColor, QDragEnterEvent, QDropEvent, QTextImageFormat, QTextCursor, QPixmap
from core.font.font_manager import FontManager
from core.font.font_pages_manager import FontPagesManager
import os

class EmojiMenu(QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(280, 260)  # 调整为更宽更短
        self.font_pages_manager = FontPagesManager()
        
        self.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 8px;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QWidget#emojiContainer {
                background: transparent;
            }
            QPushButton {
                border: none;
                background: transparent;
                padding: 0px;
                font-size: 22px;
                min-width: 32px;  /* 增加表情按钮宽度 */
                min-height: 32px;
                margin: 1px;
            }
            QPushButton:hover {
                background: rgba(33, 150, 243, 0.1);
                border-radius: 4px;
            }
        """)
        self.setup_emojis()

    def setup_emojis(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(8)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        container = QWidget()
        container.setObjectName("emojiContainer")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 4, 0)  # 右边留出滚动条的空间
        container_layout.setSpacing(12)
        
        # 表情分类和数据
        emoji_categories = {
            "常用表情": [
                "😀", "😃", "😄", "😁", "😆", "😅", "😂",
                "😊", "😇", "🙂", "🙃", "😉", "😌", "😍",
                "😘", "😗", "😙", "😚", "😋", "😛", "😝",
                "😜", "🤪", "🤨", "🧐", "🤓", "😎", "🤩",
            ],
            "手势": [
                "👍", "👎", "👌", "✌️", "🤞", "🤟", "🤘",
                "👈", "👉", "👆", "👇", "☝️", "✋", "🤚",
                "👋", "🤏", "✍️", "👏", "🙌", "🤝", "🤲",
            ],
            "心形": [
                "❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍",
                "🤎", "💔", "❣️", "💕", "💞", "💓", "💗", "💖",
            ],
        }
        
        for category, emojis in emoji_categories.items():
            # 分类标题
            category_label = QLabel(category)
            self.font_pages_manager.apply_normal_style(category_label)
            category_label.setStyleSheet("""
                color: #666666;
                padding: 4px 0px;
                font-weight: 500;
                font-size: 12px;
            """)
            container_layout.addWidget(category_label)
            
            # 表情网格容器
            emoji_grid = QWidget()
            grid_layout = QGridLayout(emoji_grid)
            grid_layout.setContentsMargins(0, 0, 0, 0)
            grid_layout.setSpacing(0)  # 最小化间距
            
            # 增加每行表情数量到8个
            row, col = 0, 0
            max_cols = 8  # 每行8个表情
            
            for emoji_char in emojis:
                emoji_btn = QPushButton(emoji_char)
                emoji_btn.clicked.connect(lambda checked, e=emoji_char: self.parent().insert_emoji(e))
                grid_layout.addWidget(emoji_btn, row, col)
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
            
            container_layout.addWidget(emoji_grid)
            container_layout.addSpacing(4)  # 分类之间的间距
        
        container_layout.addStretch()
        scroll_area.setWidget(container)
        main_layout.addWidget(scroll_area)

    def mousePressEvent(self, event):
        if self.childAt(event.pos()):
            event.accept()
        else:
            super().mousePressEvent(event)

class CommentBox(QFrame):
    comment_submitted = Signal(str, list)  # 修改信号定义，传递评论文本和图片列表
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.font_manager = FontManager()
        self.font_pages_manager = FontPagesManager()
        self.max_images = 4  # 最大图片数量限制
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)
        
        # 评论输入框
        self.comment_edit = QTextEdit()
        self.comment_edit.setPlaceholderText("写下你的评论...(最多200个字符)")
        self.comment_edit.setAcceptDrops(True)
        self.comment_edit.dragEnterEvent = self.dragEnterEvent
        self.comment_edit.dropEvent = self.dropEvent
        self.comment_edit.textChanged.connect(self._on_text_changed)  # 添加文本变化监听
        self.font_pages_manager.apply_normal_style(self.comment_edit)
        self.comment_edit.setStyleSheet("""
            QTextEdit {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 8px;
                background: #FFFFFF;
                min-height: 80px;
                max-height: 120px;
            }
            QTextEdit:focus {
                border: 1px solid #2196F3;
            }
        """)
        
        # 创建表情菜单
        self.emoji_menu = EmojiMenu(self)
        
        # 底部操作栏
        bottom_container = QWidget()
        bottom_layout = QHBoxLayout(bottom_container)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(8)
        
        # 表情按钮
        emoji_button = QPushButton(self.font_manager.get_icon_text('sentiment_satisfied'))
        self.font_manager.apply_icon_font(emoji_button)
        emoji_button.setStyleSheet("""
            QPushButton {
                border: none;
                padding: 4px;
                border-radius: 4px;
                color: rgba(0, 0, 0, 0.6);
                background: transparent;
            }
            QPushButton:hover {
                background: rgba(33, 150, 243, 0.1);
                color: #2196F3;
            }
        """)
        emoji_button.clicked.connect(self.show_emoji_menu)
        
        # 图片上传按钮
        image_btn = QPushButton(self.font_manager.get_icon_text('image'))
        self.font_manager.apply_icon_font(image_btn, size=20)
        image_btn.clicked.connect(self.select_image)
        image_btn.setStyleSheet(emoji_button.styleSheet())
        
        # 发送按钮
        send_btn = QPushButton("发送")
        self.font_pages_manager.apply_normal_style(send_btn)
        send_btn.setStyleSheet("""
            QPushButton {
                padding: 6px 16px;
                border-radius: 4px;
                background: #2196F3;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background: #1976D2;
            }
            QPushButton:pressed {
                background: #1565C0;
            }
        """)
        send_btn.clicked.connect(self.submit_comment)
        
        bottom_layout.addWidget(emoji_button)
        bottom_layout.addWidget(image_btn)
        bottom_layout.addStretch()
        bottom_layout.addWidget(send_btn)
        
        layout.addWidget(self.comment_edit)
        layout.addWidget(bottom_container)
        
        # 卡片样式
        self.setStyleSheet("""
            CommentBox {
                background: #FFFFFF;
                border-radius: 8px;
                border: 1px solid #E0E0E0;
                max-width: 850px;
            }
        """)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
    def show_emoji_menu(self):
        """显示表情选择菜单"""
        emoji_button = self.sender()
        if emoji_button:
            # 计算菜单位置
            menu_pos = emoji_button.mapToGlobal(emoji_button.rect().topLeft())
            # 向上偏移菜单高度和一些额外空间
            menu_pos.setY(menu_pos.y() - self.emoji_menu.height() - 10)
            
            # 确保菜单不会超出屏幕顶部
            if menu_pos.y() < 0:
                # 如果向上显示会超出屏幕，就向下显示
                menu_pos.setY(emoji_button.mapToGlobal(emoji_button.rect().bottomLeft()).y() + 10)
            
            self.emoji_menu.popup(menu_pos)

    def insert_emoji(self, emoji):
        """插入表情时也需要检查字符数限制"""
        try:
            current_text = self.comment_edit.toPlainText()
            if len(current_text) + len(emoji) > 200:
                from core.utils.notif import show_warning
                show_warning("添加表情后将超出200个字符限制")
                return
                
            self.comment_edit.insertPlainText(emoji)
            
        except Exception as e:
            from core.utils.notif import show_error
            show_error(f"插入表情出错: {str(e)}")

    def select_image(self):
        # 检查当前图片数量
        current_images = 0
        layout = self.layout()
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if (isinstance(widget, QWidget) and widget.layout() and 
                widget.layout().count() > 0 and 
                isinstance(widget.layout().itemAt(0).widget(), QLabel) and 
                widget.layout().itemAt(0).widget().pixmap()):
                current_images += 1
        
        if current_images >= self.max_images:
            from core.utils.notif import show_warning
            show_warning(f"最多只能上传{self.max_images}张图片")
            return
            
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.gif)")
        if file_dialog.exec_():
            file_paths = file_dialog.selectedFiles()
            remaining_slots = self.max_images - current_images
            
            # 只处理剩余可用数量的图片
            for file_path in file_paths[:remaining_slots]:
                self.insert_image(file_path)
            
            # 如果选择的图片超过剩余数量，显示提示
            if len(file_paths) > remaining_slots:
                from core.utils.notif import show_warning
                show_warning(f"已达到最大图片数量限制({self.max_images}张)，多余的图片未被添加")

    def insert_image(self, file_path):
        # 检查当前图片数量
        current_images = 0
        layout = self.layout()
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if (isinstance(widget, QWidget) and widget.layout() and 
                widget.layout().count() > 0 and 
                isinstance(widget.layout().itemAt(0).widget(), QLabel) and 
                widget.layout().itemAt(0).widget().pixmap()):
                current_images += 1
        
        if current_images >= self.max_images:
            from core.utils.notif import show_warning
            show_warning(f"最多只能上传{self.max_images}张图片")
            return
            
        # 创建图片预览容器
        preview = QWidget()
        preview_layout = QHBoxLayout(preview)
        preview_layout.setContentsMargins(4, 4, 4, 4)
        preview_layout.setSpacing(8)
        
        # 添加图片预览
        image_label = QLabel()
        
        # 加载原始图片
        original_pixmap = QPixmap(file_path)
        if not original_pixmap.isNull():
            # 保存原始图片
            image_label.setProperty("original_pixmap", original_pixmap)
            
            # 创建预览图
            preview_size = 60  # 预览尺寸
            preview_pixmap = original_pixmap.scaled(
                preview_size, preview_size,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            image_label.setPixmap(preview_pixmap)
            image_label.setFixedSize(preview_size, preview_size)
            image_label.setAlignment(Qt.AlignCenter)
            
            # 设置样式
            image_label.setStyleSheet("""
                QLabel {
                    background: #F5F5F5;
                    border-radius: 4px;
                    padding: 4px;
                }
            """)
        
        # 添加文件名
        name_label = QLabel(os.path.basename(file_path))
        name_label.setStyleSheet("color: #666666;")
        
        # 添加删除按钮
        delete_btn = QPushButton(self.font_manager.get_icon_text('close'))
        self.font_manager.apply_icon_font(delete_btn, size=16)
        delete_btn.setStyleSheet("""
            QPushButton {
                border: none;
                color: #666666;
                padding: 4px;
            }
            QPushButton:hover {
                color: #f44336;
                background: rgba(244, 67, 54, 0.1);
                border-radius: 4px;
            }
        """)
        delete_btn.clicked.connect(preview.deleteLater)
        
        preview_layout.addWidget(image_label)
        preview_layout.addWidget(name_label)
        preview_layout.addStretch()
        preview_layout.addWidget(delete_btn)
        
        preview.setStyleSheet("""
            QWidget {
                background: #F5F5F5;
                border-radius: 4px;
            }
        """)
        
        # 将预览添加到评论框下方
        layout = self.layout()
        layout.insertWidget(layout.count()-1, preview)

    def dragEnterEvent(self, event: QDragEnterEvent):
        mime_data = event.mimeData()
        if mime_data.hasUrls():
            for url in mime_data.urls():
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                        event.acceptProposedAction()
                        return
        event.ignore()

    def dropEvent(self, event: QDropEvent):
        # 检查当前图片数量
        current_images = 0
        layout = self.layout()
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if (isinstance(widget, QWidget) and widget.layout() and 
                widget.layout().count() > 0 and 
                isinstance(widget.layout().itemAt(0).widget(), QLabel) and 
                widget.layout().itemAt(0).widget().pixmap()):
                current_images += 1
                
        if current_images >= self.max_images:
            from core.utils.notif import show_warning
            show_warning(f"最多只能上传{self.max_images}张图片")
            event.ignore()
            return
            
        mime_data = event.mimeData()
        if mime_data.hasUrls():
            remaining_slots = self.max_images - current_images
            valid_urls = [url for url in mime_data.urls() if 
                         url.isLocalFile() and 
                         url.toLocalFile().lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
            
            # 只处理剩余可用数量的图片
            for url in valid_urls[:remaining_slots]:
                self.insert_image(url.toLocalFile())
                
            # 如果拖放的图片超过剩余数量，显示提示
            if len(valid_urls) > remaining_slots:
                from core.utils.notif import show_warning
                show_warning(f"已达到最大图片数量限制({self.max_images}张)，多余的图片未被添加")
                
            event.acceptProposedAction()

    def _on_text_changed(self):
        """监听文本变化，限制字符数（不计算空格）"""
        try:
            text = self.comment_edit.toPlainText()
            # 计算非空格字符的数量
            non_space_count = len([c for c in text if not c.isspace()])
            
            if non_space_count > 200:
                # 保存当前光标位置
                cursor = self.comment_edit.textCursor()
                current_position = cursor.position()
                
                # 保留前200个非空格字符
                count = 0
                result = ""
                for c in text:
                    if not c.isspace():
                        count += 1
                        if count > 200:
                            break
                    result += c
                
                # 阻断文本变化信号，防止递归
                self.comment_edit.textChanged.disconnect(self._on_text_changed)
                
                # 设置新文本
                self.comment_edit.setPlainText(result)
                
                # 恢复光标位置
                new_cursor = self.comment_edit.textCursor()
                new_cursor.setPosition(min(current_position, len(result)))
                self.comment_edit.setTextCursor(new_cursor)
                
                # 重新连接信号
                self.comment_edit.textChanged.connect(self._on_text_changed)
                
                # 显示警告
                from core.utils.notif import show_warning
                show_warning("评论最多只能输入200个字符（不包含空格）")
                
        except Exception as e:
            from core.utils.notif import show_error
            show_error(f"文本处理出错: {str(e)}")

    def submit_comment(self):
        try:
            comment_text = self.comment_edit.toPlainText().strip()
            
            # 检查是否有非空格内容
            if not comment_text or not any(not c.isspace() for c in comment_text):
                from core.utils.notif import show_warning
                show_warning("评论内容不能为空")
                return
            
            # 检查非空格字符数
            non_space_count = len([c for c in comment_text if not c.isspace()])
            if non_space_count > 200:
                # 保留前200个非空格字符
                count = 0
                result = ""
                for c in comment_text:
                    if not c.isspace():
                        count += 1
                        if count > 200:
                            break
                    result += c
                comment_text = result
            
            # 获取所有图片预览
            images = []
            layout = self.layout()
            for i in range(layout.count()):
                widget = layout.itemAt(i).widget()
                if isinstance(widget, QWidget) and widget.layout():
                    # 检查是否为图片预览容器
                    first_child = widget.layout().itemAt(0)
                    if first_child and isinstance(first_child.widget(), QLabel):
                        label = first_child.widget()
                        # 获取原始图片
                        original_pixmap = label.property("original_pixmap")
                        if original_pixmap and not original_pixmap.isNull():
                            images.append(original_pixmap)
            
            # 发送评论文本和图片列表
            self.comment_submitted.emit(comment_text, images)
            
            # 清理输入框和图片预览
            self.comment_edit.clear()
            layout = self.layout()
            # 只删除图片预览容器
            for i in reversed(range(layout.count())):
                widget = layout.itemAt(i).widget()
                if (isinstance(widget, QWidget) and widget.layout() and 
                    widget.layout().count() > 0 and 
                    isinstance(widget.layout().itemAt(0).widget(), QLabel) and 
                    widget.layout().itemAt(0).widget().pixmap()):
                    widget.deleteLater()
                    
        except Exception as e:
            from core.utils.notif import show_error
            show_error(f"发送评论出错: {str(e)}")

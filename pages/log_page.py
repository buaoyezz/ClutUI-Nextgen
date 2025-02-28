from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QLabel, 
                             QHBoxLayout, QLineEdit, QPushButton, QScrollBar)
from PySide6.QtCore import Qt, QTimer, QRegularExpression
from PySide6.QtGui import QTextCharFormat, QColor, QTextCursor
from core.log.log_manager import log
from core.ui.scroll_style import ScrollStyle
from core.font.font_pages_manager import FontPagesManager
from core.i18n import i18n
import os
import re

class LogPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_filter = 'ALL'  # 添加当前过滤级别的记录
        self.font_manager = FontPagesManager()  # 添加字体管理器
        self.last_content = ""  # 添加变量保存上次的内容
        self.last_update_time = 0  # 添加变量记录上次更新时间
        self.auto_scroll = True  # 添加自动滚动标志
        self.setup_ui()
        self.load_logs()
        
        # 修改定时器间隔为更合理的值
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.check_logs_update)
        self.update_timer.start(2000)  # 改为2秒检查一次
        
        # 连接语言变更信号
        i18n.language_changed.connect(self.update_text)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # 标题
        self.title_label = QLabel(i18n.get_text("system_log"))
        self.font_manager.apply_title_style(self.title_label)  # 应用标题字体
        self.title_label.setStyleSheet("""
            QLabel {
                color: #1F2937;
                background: transparent;
                font-size: 24px;
                font-weight: 600;
                letter-spacing: 0.5px;
            }
        """)
        layout.addWidget(self.title_label)

        # 搜索栏样式优化
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.font_manager.apply_normal_style(self.search_input)  # 应用普通字体
        self.search_input.setPlaceholderText(i18n.get_text("search_placeholder"))
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                font-size: 13px;
                background: white;
                letter-spacing: 0.2px;
            }
            QLineEdit:focus {
                border: 1px solid #2196F3;
            }
        """)
        self.search_input.textChanged.connect(self.search_logs)  # 改为实时搜索
        
        # 添加自动滚动按钮
        self.auto_scroll_btn = QPushButton(i18n.get_text("auto_scroll"))
        self.auto_scroll_btn.setCheckable(True)
        self.auto_scroll_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                font-size: 13px;
                background: white;
                color: #666666;
            }
            QPushButton:checked {
                background: #2196F3;
                color: white;
                border: 1px solid #1976D2;
            }
            QPushButton:hover {
                background: #E3F2FD;
            }
            QPushButton:checked:hover {
                background: #1976D2;
            }
        """)
        self.font_manager.apply_normal_style(self.auto_scroll_btn)
        self.auto_scroll_btn.clicked.connect(self.toggle_auto_scroll)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.auto_scroll_btn)
        layout.addLayout(search_layout)

        # 修改日志统计区域为可点击的过滤按钮
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(10)
        
        self.stats_buttons = {
            'INFO': QPushButton("INFO: 0"),
            'WARN': QPushButton("WARN: 0"),
            'DEBUG': QPushButton("DEBUG: 0"),
            'ERROR': QPushButton("ERROR: 0"),
            'ALL': QPushButton("显示全部")
        }
        
        stats_styles = {
            'INFO': ("#2E7D32", "#E8F5E9"),   # 墨绿色
            'WARN': ("#FFC107", "#FFF8E1"),   # 黄色
            'DEBUG': ("#9C27B0", "#F3E5F5"),  # 浅紫色
            'ERROR': ("#F44336", "#FFEBEE"),  # 红色
            'ALL': ("#757575", "#F5F5F5")     # 灰色
        }
        
        for level, button in self.stats_buttons.items():
            main_color, bg_color = stats_styles[level]
            button.setCheckable(True)
            button.setStyleSheet(f"""
                QPushButton {{
                    padding: 5px 15px;
                    background: {bg_color};
                    border: 2px solid {main_color};
                    border-radius: 5px;
                    font-size: 12px;
                    color: {main_color};
                    font-weight: bold;
                }}
                QPushButton:checked {{
                    background: {main_color};
                    color: white;
                }}
                QPushButton:hover {{
                    background: {main_color};
                    color: white;
                }}
            """)
            button.clicked.connect(lambda checked, l=level: self.filter_logs(l))
            self.font_manager.apply_small_style(button)  # 应用小字体
            stats_layout.addWidget(button)
        
        # 默认选中"显示全部"按钮
        self.stats_buttons['ALL'].setChecked(True)
        
        stats_layout.addStretch()
        layout.addLayout(stats_layout)

        # 日志显示区域
        self.log_display = QTextEdit()
        self.font_manager.apply_normal_style(self.log_display)  # 应用普通字体
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet(f"""
            QTextEdit {{
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 10px;
                padding: 20px;
                font-family: "Consolas", "Microsoft YaHei UI", monospace;
                font-size: 13px;
                line-height: 1.5;
            }}
            {ScrollStyle.get_style()}
        """)
        
        # 自定义滚动条样式
        scroll_bar = QScrollBar()
        scroll_bar.setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background: #F0F0F0;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #BDBDBD;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        self.log_display.setVerticalScrollBar(scroll_bar)
        
        layout.addWidget(self.log_display)

        # 设置日志显示区域的最小高度
        self.log_display.setMinimumHeight(300)

    def search_logs(self):
        search_text = self.search_input.text().strip()
        if not search_text:
            self.load_logs()
            return
        
        # 获取当前HTML内容并保存原始格式
        current_html = self.log_display.toHtml()
        
        # 只高亮搜索文本，不改变其他样式
        highlight_format = 'background-color: #FFE4B5'
        
        # 使用正则表达式来只匹配文本内容，不匹配HTML标签内的内容
        pattern = f'(?<!<[^>]*){re.escape(search_text)}'
        highlighted_text = re.sub(
            pattern,
            r'<span style="{}">\g<0></span>'.format(highlight_format),
            current_html,
            flags=re.IGNORECASE
        )
        
        # 计算匹配数量（排除HTML标签中的匹配）
        match_count = len(re.findall(pattern, current_html, re.IGNORECASE))
        
        if match_count > 0:
            # 添加搜索统计信息
            info_text = f'<div style="color: #666666; margin-bottom: 10px; padding: 5px; background-color: #F5F5F5; border-radius: 5px;">找到 {match_count} 处匹配项 "{search_text}"</div>'
            # 确保在表格之前插入统计信息
            table_start = highlighted_text.find('<table')
            if table_start != -1:
                highlighted_text = highlighted_text[:table_start] + info_text + highlighted_text[table_start:]
            else:
                highlighted_text = info_text + highlighted_text
        
        self.log_display.setHtml(highlighted_text)

    def filter_logs(self, level: str):
        # 更新按钮状态和当前过滤级别
        self.current_filter = level
        for btn_level, button in self.stats_buttons.items():
            button.setChecked(btn_level == level)
        
        self.apply_filter()  # 应用过滤

    def apply_filter(self):
        try:
            # 获取最新的日志文件
            log_dir = os.path.join(os.path.expanduser('~'), '.clutui_nextgen_example', 'logs')
            latest_log = max(
                [os.path.join(log_dir, f) for f in os.listdir(log_dir) if f.endswith('.log')],
                key=os.path.getmtime
            )
            
            with open(latest_log, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 过滤并格式化日志内容
            formatted_content = []
            for line in content.splitlines():
                if not line.strip() or line.strip().startswith('==='):
                    continue
                    
                if self.current_filter == 'ALL' or (f'│ {self.current_filter}' in line):
                    parts = line.split('│')
                    if len(parts) >= 3:
                        # 完整保留时间戳，不再截断
                        timestamp = parts[0].strip()
                        level = parts[1].strip()      # INFO/DEBUG/etc
                        
                        # 处理消息部分，提取文件路径和行号
                        full_message = '│'.join(parts[2:]).strip()
                        
                        # 使用正则表达式匹配文件路径和行号
                        file_match = re.match(r'(.*?):(\d+)\s*\|\s*(.*)', full_message)
                        if file_match:
                            file_path = file_match.group(1).strip()
                            line_num = file_match.group(2)
                            message = file_match.group(3).strip()
                            file_info = f"{file_path:<30} :{line_num}"
                        else:
                            file_info = ""
                            message = full_message
                        
                        # 根据日志级别设置颜色
                        if 'INFO' in level:
                            level_color = "#2E7D32"  # 墨绿色
                        elif 'WARNING' in level:
                            level_color = "#FFC107"
                        elif 'DEBUG' in level:
                            level_color = "#9C27B0"  # 浅紫色
                        elif 'ERROR' in level:
                            level_color = "#F44336"
                        else:
                            level_color = "#333333"
                        
                        # 修改时间戳的显示宽度
                        formatted_line = (
                            '<tr style="line-height: 1.5;">'
                            f'<td style="width: 150px; padding-right: 10px; white-space: nowrap; color: #666666;">{timestamp}</td>'  # 增加宽度到150px
                            f'<td style="width: 60px; padding: 0 10px; white-space: nowrap; color: {level_color}; font-weight: bold;">{level}</td>'
                            f'<td style="width: 350px; padding: 0 10px; white-space: pre; color: #0066CC; font-family: Consolas;">{file_info}</td>'
                            f'<td style="padding-left: 10px; word-break: break-all;">{message}</td>'
                            '</tr>'
                        )
                        formatted_content.append(formatted_line)
            
            # 使用表格包装所有内容以保持对齐
            html_content = (
                '<table style="border-collapse: collapse; width: 100%; '
                'font-family: Consolas, \'Microsoft YaHei UI\', monospace; font-size: 13px; '
                'table-layout: fixed;">'
                f'{"".join(formatted_content)}'
                '</table>'
            )
            
            self.log_display.setHtml(html_content)
            self.update_stats(content)
            
        except Exception as e:
            log.error(f"过滤日志失败: {str(e)}")
            self.log_display.setText(f"过滤日志失败: {str(e)}")

    def update_stats(self, content):
        # 使用更准确的正则表达式来匹配日志级别
        patterns = {
            'INFO': r'\[.*?\] │ INFO',     # 匹配新的日志格式
            'WARN': r'\[.*?\] │ WARNING',  # 匹配新的日志格式
            'DEBUG': r'\[.*?\] │ DEBUG',   # 匹配新的日志格式
            'ERROR': r'\[.*?\] │ ERROR'    # 匹配新的日志格式
        }
        
        # 统计各级别日志数量
        for level, pattern in patterns.items():
            count = len(re.findall(pattern, content))
            self.stats_buttons[level].setText(f"{level}: {count}")

    def check_logs_update(self):
        try:
            log_dir = os.path.join(os.path.expanduser('~'), '.clutui_nextgen_example', 'logs')
            latest_log = max(
                [os.path.join(log_dir, f) for f in os.listdir(log_dir) if f.endswith('.log')],
                key=os.path.getmtime
            )
            
            with open(latest_log, 'r', encoding='utf-8') as f:
                current_content = f.read()
            
            if current_content != self.last_content:
                self.last_content = current_content
                self.load_logs(force_update=False)
                
        except Exception as e:
            log.error(f"检查日志更新失败: {str(e)}")

    def load_logs(self, force_update=True):
        try:
            # 保存当前搜索文本和滚动条位置
            search_text = self.search_input.text().strip()
            current_scroll = self.log_display.verticalScrollBar().value()
            was_at_bottom = current_scroll == self.log_display.verticalScrollBar().maximum()
            
            # 获取当前显示的内容
            current_content = self.log_display.toHtml()
            
            # 如果不是强制更新且内容没有变化，则直接返回
            if not force_update and current_content == self.last_content:
                return
                
            # 获取最新的日志文件
            log_dir = os.path.join(os.path.expanduser('~'), '.clutui_nextgen_example', 'logs')
            if not os.path.exists(log_dir):
                self.log_display.setText("日志目录不存在")
                return
                
            log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
            if not log_files:
                self.log_display.setText("没有找到日志文件")
                return

            # 应用过滤器前暂时禁用更新
            self.log_display.setUpdatesEnabled(False)
            
            # 应用当前的过滤器
            self.apply_filter()
            
            # 如果有搜索文本，重新应用搜索
            if search_text:
                self.search_logs()
                
            # 修改滚动条位置逻辑
            if self.auto_scroll:
                # 如果开启了自动滚动，总是滚动到底部
                self.log_display.verticalScrollBar().setValue(
                    self.log_display.verticalScrollBar().maximum()
                )
            else:
                # 保持原有的滚动位置逻辑
                if was_at_bottom:
                    self.log_display.verticalScrollBar().setValue(
                        self.log_display.verticalScrollBar().maximum()
                    )
                else:
                    self.log_display.verticalScrollBar().setValue(current_scroll)
            
            # 重新启用更新并刷新显示
            self.log_display.setUpdatesEnabled(True)
            self.log_display.update()

        except Exception as e:
            log.error(f"加载日志文件失败: {str(e)}")
            self.log_display.setText(f"加载日志文件时出错: {str(e)}")

    def toggle_auto_scroll(self):
        self.auto_scroll = self.auto_scroll_btn.isChecked()
        if self.auto_scroll:
            # 立即滚动到底部
            self.log_display.verticalScrollBar().setValue(
                self.log_display.verticalScrollBar().maximum()
            )

    def update_text(self):
        self.title_label.setText(i18n.get_text("system_log"))
        self.search_input.setPlaceholderText(i18n.get_text("search_placeholder"))
        self.auto_scroll_btn.setText(i18n.get_text("auto_scroll"))
        for btn_level, button in self.stats_buttons.items():
            button.setText(f"{btn_level}: 0")

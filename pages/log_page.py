from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QLabel, 
                             QHBoxLayout, QLineEdit, QPushButton)
from PySide6.QtCore import Qt, QTimer, QRegularExpression
from PySide6.QtGui import QTextCharFormat, QColor, QTextCursor
from core.log.log_manager import log
from core.ui.scroll_style import ScrollStyle
import os
import re

class LogPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_filter = 'ALL'  # 添加当前过滤级别的记录
        self.setup_ui()
        self.load_logs()
        
        # 创建定时器，每秒更新一次日志
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.load_logs)
        self.update_timer.start(1000)  # 1000毫秒 = 1秒

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # 标题
        title = QLabel("系统日志")
        title.setStyleSheet("""
            QLabel {
                color: #333333;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        layout.addWidget(title)

        # 搜索栏样式优化
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入关键字搜索日志内容")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                font-size: 13px;
                background: white;
            }
        """)
        self.search_input.textChanged.connect(self.search_logs)  # 改为实时搜索
        search_layout.addWidget(self.search_input)
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
            stats_layout.addWidget(button)
        
        # 默认选中"显示全部"按钮
        self.stats_buttons['ALL'].setChecked(True)
        
        stats_layout.addStretch()
        layout.addLayout(stats_layout)

        # 日志显示区域
        self.log_display = QTextEdit()
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
        layout.addWidget(self.log_display)

        # 设置日志显示区域的最小高度
        self.log_display.setMinimumHeight(300)

    def search_logs(self):
        search_text = self.search_input.text().strip()
        if not search_text:
            self.load_logs()
            return
        
        # 获取当前HTML内容
        current_html = self.log_display.toHtml()
        
        # 创建高亮样式的搜索结果
        highlight_format = 'background-color: #FFE4B5'
        highlighted_text = current_html.replace(
            search_text,
            f'<span style="{highlight_format}">{search_text}</span>',
            flags=re.IGNORECASE
        )
        
        # 计算匹配数量
        match_count = highlighted_text.count(highlight_format)
        
        if match_count > 0:
            # 添加搜索统计信息
            info_text = f'<div style="color: #666666; margin-bottom: 10px; padding: 5px; background-color: #F5F5F5; border-radius: 5px;">找到 {match_count} 处匹配项 "{search_text}"</div>'
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
                        timestamp = parts[0].strip()  # [17:15:32]
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
                        
                        # 使用等宽字体和固定宽度来保证对齐
                        formatted_line = (
                            '<tr style="line-height: 1.5;">'
                            f'<td style="width: 80px; padding-right: 10px; white-space: nowrap; color: #666666;">{timestamp}</td>'
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

    def load_logs(self):
        try:
            # 保存当前搜索文本和滚动条位置
            search_text = self.search_input.text().strip()
            current_scroll = self.log_display.verticalScrollBar().value()
            was_at_bottom = current_scroll == self.log_display.verticalScrollBar().maximum()
            
            # 获取最新的日志文件
            log_dir = os.path.join(os.path.expanduser('~'), '.clutui_nextgen_example', 'logs')
            if not os.path.exists(log_dir):
                self.log_display.setText("日志目录不存在")
                return
                
            log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
            if not log_files:
                self.log_display.setText("没有找到日志文件")
                return

            # 应用当前的过滤器
            self.apply_filter()
                
            # 如果有搜索文本，重新应用搜索
            if search_text:
                self.search_logs()
                
            # 恢复滚动条位置
            if was_at_bottom:
                self.log_display.verticalScrollBar().setValue(
                    self.log_display.verticalScrollBar().maximum()
                )
            else:
                self.log_display.verticalScrollBar().setValue(current_scroll)

        except Exception as e:
            log.error(f"加载日志文件失败: {str(e)}")
            self.log_display.setText(f"加载日志文件时出错: {str(e)}")

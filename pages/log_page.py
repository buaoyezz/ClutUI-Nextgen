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

        # 日志统计区域样式优化
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(10)
        
        self.stats_labels = {
            'INFO': QLabel("INFO: 0"),
            'WARN': QLabel("WARN: 0"),
            'DEBUG': QLabel("DEBUG: 0"),
            'ERROR': QLabel("ERROR: 0")
        }
        
        stats_styles = {
            'INFO': "#4CAF50",   # 绿色
            'WARN': "#FFC107",   # 黄色
            'DEBUG': "#2196F3",  # 蓝色
            'ERROR': "#F44336"   # 红色
        }
        
        for level, label in self.stats_labels.items():
            label.setStyleSheet(f"""
                QLabel {{
                    padding: 5px 15px;
                    background: white;
                    border: 2px solid {stats_styles[level]};
                    border-radius: 5px;
                    font-size: 12px;
                    color: {stats_styles[level]};
                    font-weight: bold;
                }}
            """)
            stats_layout.addWidget(label)
        
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
                padding: 10px;
                font-family: "Consolas", "Microsoft YaHei UI", monospace;
                font-size: 13px;
                line-height: 1.5;
            }}
            {ScrollStyle.get_style()}
        """)
        layout.addWidget(self.log_display)

    def search_logs(self):
        search_text = self.search_input.text().strip()
        if not search_text:
            self.load_logs()
            return
        
        # 保存当前文本
        current_text = self.log_display.toPlainText()
        self.log_display.clear()
        self.log_display.setText(current_text)
        
        # 创建文本光标和格式
        cursor = self.log_display.textCursor()
        format = QTextCharFormat()
        format.setBackground(QColor("#FFE4B5"))
        
        regex = QRegularExpression(QRegularExpression.escape(search_text))
        regex.setPatternOptions(QRegularExpression.CaseInsensitiveOption)
        
        match_count = 0
        pos = 0
        
        # 开始搜索和高亮
        while True:
            match = regex.match(self.log_display.toPlainText(), pos)
            if not match.hasMatch():
                break
            cursor.setPosition(match.capturedStart())
            cursor.setPosition(match.capturedEnd(), QTextCursor.KeepAnchor)
            cursor.mergeCharFormat(format)
            pos = match.capturedEnd()
            match_count += 1
        
        # 在顶部添加搜索统计信息
        if match_count > 0:
            info_text = f"找到 {match_count} 处匹配项 \"{search_text}\""
            self.log_display.insertHtml(
                f'<div style="color: #666666; margin-bottom: 10px; '
                f'padding: 5px; background-color: #F5F5F5; '
                f'border-radius: 5px;">{info_text}</div><br>'
            )

    def update_stats(self, content):
        # 使用更准确的正则表达式来匹配日志级别
        patterns = {
            'INFO': r'\[.*?\] INFO',    # 匹配 [时间戳] INFO 格式
            'WARN': r'\[.*?\] WARN',    # 匹配 [时间戳] WARN 格式
            'DEBUG': r'\[.*?\] DEBUG',  # 匹配 [时间戳] DEBUG 格式
            'ERROR': r'\[.*?\] ERROR'   # 匹配 [时间戳] ERROR 格式
        }
        
        # 统计各级别日志数量
        for level, pattern in patterns.items():
            count = len(re.findall(pattern, content))
            self.stats_labels[level].setText(f"{level}: {count}")

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

            # 获取最新的日志文件
            latest_log = max(
                [os.path.join(log_dir, f) for f in log_files],
                key=os.path.getmtime
            )

            # 读取日志内容
            with open(latest_log, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # 如果有搜索文本，重新应用搜索
                if search_text:
                    self.log_display.setText(content)
                    self.search_logs()
                else:
                    self.log_display.setText(content)
                    
                self.update_stats(content)
                
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

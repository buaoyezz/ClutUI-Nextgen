import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Optional
import colorama
from colorama import Fore, Style

class ColoredFormatter(logging.Formatter):
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
    }
    
    def __init__(self, fmt: str, datefmt: Optional[str] = None):
        super().__init__(fmt, datefmt)
        colorama.init()
    
    def format(self, record: logging.LogRecord) -> str:
        # 保存原始的属性
        original_levelname = record.levelname
        original_pathname = record.pathname
        original_lineno = record.lineno
        
        # 获取实际的调用文件信息
        if hasattr(record, 'pathname'):
            # 获取调用栈信息来确定真实的调用位置
            import inspect
            frame = inspect.currentframe()
            # 向上查找直到找到非日志模块的调用者
            while frame:
                module_name = frame.f_globals.get('__name__', '')
                if not module_name.startswith('logging') and 'log_manager' not in module_name:
                    filename = os.path.basename(frame.f_code.co_filename)
                    lineno = frame.f_lineno
                    record.pathname = filename
                    record.lineno = lineno
                    break
                frame = frame.f_back
            
        # 为不同级别添加颜色
        if record.levelname in self.COLORS:
            record.levelname = (f"{self.COLORS[record.levelname]}"
                              f"{record.levelname:^8}"
                              f"{Style.RESET_ALL}")
        
        # 为文件路径和行号添加颜色
        record.pathname = f"{Fore.BLUE}{record.pathname}{Style.RESET_ALL}"
        record.lineno = str(record.lineno)
        
        # 格式化消息
        result = super().format(record)
        
        # 恢复原始属性
        record.levelname = original_levelname
        record.pathname = original_pathname
        record.lineno = original_lineno
        
        return result

class LogManager:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LogManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if LogManager._initialized:
            return
            
        LogManager._initialized = True
        
        # 创建日志目录
        self.log_dir = os.path.join(os.path.expanduser('~'), '.clutui_nextgen_example', 'logs')
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 创建日志文件名
        current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.log_file = os.path.join(self.log_dir, f'clutui_nextgen_{current_time}.log')
        
        # 创建主日志记录器
        self.logger = logging.getLogger('ClutCleaner')
        self.logger.setLevel(logging.DEBUG)
        
        # 清除可能存在的处理器
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # 创建格式化器
        file_formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)-8s [%(filename)s:%(lineno)s] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_formatter = ColoredFormatter(
            '[%(asctime)s] │ %(levelname)s │ %(pathname)s:%(lineno)s │ %(message)s',  
            datefmt='%H:%M:%S'  # 只显示时间，不显示日期
        )
        
        # 创建文件处理器
        file_handler = RotatingFileHandler(
            self.log_file,
            maxBytes=10*1024*1024,
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # 启动信息
        self.info("="*50)
        self.info("日志系统初始化完成")
        self.info(f"日志文件路径: {self.log_file}")
        self.info("="*50)
    
    def debug(self, message: str) -> None:
        self.logger.debug(message)
    
    def info(self, message: str) -> None:
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        self.logger.error(message)
    
    def critical(self, message: str) -> None:
        self.logger.critical(message)
    
    def exception(self, message: str) -> None:
        self.logger.exception(message)
    
    def get_logger(self) -> logging.Logger:
        return self.logger

# 全局访问点
log = LogManager()


"""
使用方法：

from core.log.log_manager import log

# 测试不同级别的日志
log.debug("这是一条调试信息")
log.info("这是一条普通信息")
log.warning("这是一条警告信息")
log.error("这是一条错误信息")
log.critical("这是一条严重错误信息")

try:
    1/0
except Exception as e:
    log.exception("发生了一个异常")

"""
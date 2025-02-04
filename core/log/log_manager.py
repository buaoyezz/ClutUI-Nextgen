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
        'DEBUG': '',  # 软件内不使用颜色
        'INFO': '',
        'WARNING': '',
        'ERROR': '',
        'CRITICAL': '',
    }
    
    def __init__(self, fmt: str, datefmt: Optional[str] = None, use_colors: bool = True):
        # 修改格式化字符串，使用固定宽度
        fmt = ('[%(asctime)s] │ %(levelname)-8s │ %(pathname)-25s:%(lineno)-4d │ %(message)s')
        super().__init__(fmt, datefmt)
        self.use_colors = use_colors
        if use_colors:
            colorama.init()
            self.COLORS = {
                'DEBUG': Fore.CYAN,
                'INFO': Fore.GREEN,
                'WARNING': Fore.YELLOW,
                'ERROR': Fore.RED,
                'CRITICAL': Fore.RED + Style.BRIGHT,
            }
    
    def format(self, record: logging.LogRecord) -> str:
        # 保存原始的属性
        original_levelname = record.levelname
        original_pathname = record.pathname
        
        # 获取实际的调用文件信息
        if hasattr(record, 'pathname'):
            import inspect
            frame = inspect.currentframe()
            caller_frame = None
            
            while frame:
                module_name = frame.f_globals.get('__name__', '')
                if (not module_name.startswith('logging') and 
                    not module_name.startswith('core.log')):
                    caller_frame = frame
                    break
                frame = frame.f_back
            
            if caller_frame:
                filename = os.path.basename(caller_frame.f_code.co_filename)
                # 确保文件名不超过25个字符，如果超过则截断
                if len(filename) > 25:
                    filename = filename[:22] + "..."
                record.pathname = filename
                record.lineno = caller_frame.f_lineno
        
        # 根据是否使用颜色来格式化
        if self.use_colors:
            if record.levelname in self.COLORS:
                record.levelname = (f"{self.COLORS[record.levelname]}"
                                  f"{record.levelname}"
                                  f"{Style.RESET_ALL}")
            record.pathname = f"{Fore.BLUE}{record.pathname}{Style.RESET_ALL}"
        
        # 格式化消息
        result = super().format(record)
        
        # 恢复原始属性
        record.levelname = original_levelname
        record.pathname = original_pathname
        
        return result

class LogManager:
    _instance = None
    _initialized = False
    _active_filters = set()
    
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
        
        # 创建两种格式化器
        console_formatter = ColoredFormatter(
            '[%(asctime)s] │ %(levelname)s │ %(pathname)s:%(lineno)s │ %(message)s',  
            datefmt='%H:%M:%S',
            use_colors=True  # 控制台使用颜色
        )
        
        file_formatter = ColoredFormatter(
            '[%(asctime)s] │ %(levelname)s │ %(pathname)s:%(lineno)s │ %(message)s',  
            datefmt='%H:%M:%S',
            use_colors=False  # 文件不使用颜色
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
        
        # 修改过滤器实现
        class LevelFilter(logging.Filter):
            def __init__(self, log_manager):
                super().__init__()
                self.log_manager = log_manager

            def filter(self, record):
                # 检查是否应该显示此记录
                if not self.log_manager._active_filters:
                    return True  # 没有过滤器时显示所有日志
                
                return record.levelname in self.log_manager._active_filters

        # 为每个处理器添加过滤器
        self.level_filter = LevelFilter(self)
        for handler in self.logger.handlers:
            handler.addFilter(self.level_filter)
        
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
    
    def set_level_filter(self, level: str) -> None:
        """设置日志等级过滤器
        
        Args:
            level: 日志等级 ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'ALL')
        """
        # 清除之前的过滤器
        self._active_filters.clear()
        
        # 如果不是 ALL，则设置新的过滤级别
        if level != 'ALL':
            self._active_filters.add(level)
            
        # 强制更新处理器的过滤器
        for handler in self.logger.handlers:
            handler.removeFilter(self.level_filter)
            handler.addFilter(self.level_filter)

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
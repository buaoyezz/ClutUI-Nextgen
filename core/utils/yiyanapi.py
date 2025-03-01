import requests
import random
import time
from core.log.log_manager import log
from core.thread.thread_manager import thread_manager
from typing import Callable, List, Tuple, Optional
from PySide6.QtCore import QObject, Signal

class YiyanAPI(QObject):
    # 定义信号
    hitokoto_ready = Signal(str)
    
    def __init__(self):
        super().__init__()
        # 备用的一言列表，当API请求失败时使用 
        self.fallback_quotes = [
            "ClutUI Nextgen Welcome ",
            "冷知识: ClutUI Nextgen 支持多种背景的效果",
            "冷知识: ClutUI Nextgen 支持开启自启动设置啦",
            "冷知识: ClutUI Nextgen 支持多种语言啦",
            "冷知识: ClutUI Nextgen 支持自定义主题颜色",
            "冷知识: 按下F1可以查看快捷键帮助",
            "提示: 右键点击托盘图标可以快速访问常用功能",
            "提示: 在设置中可以自定义界面字体大小",
            "ClutUI Nextgen - 让您的工作更高效",
            "今天也是充满可能性的一天",
        ]
        
        # 缓存最近获取的一言，避免频繁请求API
        self.cached_quotes = []
        self.max_cache_size = 10
        self.last_request_time = 0
        self.cache_ttl = 3600  # 缓存有效期(秒)
        
    def get_hitokoto_async(self):
        """异步获取一言，立即返回一个临时值，并在后台获取新的一言"""
        def fetch_hitokoto():
            result = self.get_hitokoto_sync()
            # 使用信号发送结果到主线程
            self.hitokoto_ready.emit(result)
            
        # 使用线程管理器提交任务
        thread_manager.submit_task("fetch_hitokoto", fetch_hitokoto)
        
        # 优先从缓存中返回，如果缓存为空则返回备用语句
        if self.cached_quotes:
            return random.choice(self.cached_quotes)
        return random.choice(self.fallback_quotes)
        
    def get_hitokoto_sync(self) -> str:
        """同步获取一言，如果API失败则返回备用语句"""
        # 检查缓存是否有效
        current_time = time.time()
        if (current_time - self.last_request_time < self.cache_ttl and 
            len(self.cached_quotes) > 0):
            log.debug("使用缓存的一言")
            return random.choice(self.cached_quotes)
            
        try:
            # 添加请求头 
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Connection': 'keep-alive',
                'Referer': 'https://hitokoto.cn/',
                'Origin': 'https://hitokoto.cn',
                'X-User': 'ClutUI-Nextgen'
            }
            
            apis = [
                ('https://v1.hitokoto.cn/?c=a&encode=json', lambda r: r.json()['hitokoto']),
                ('https://api.oick.cn/yiyan/api.php', lambda r: r.text),
                ('https://api.apiopen.top/api/sentences', lambda r: r.json()['result']['name']),
                ('https://v1.jinrishici.com/all.json', lambda r: r.json()['content']),
                ('https://api.xygeng.cn/one', lambda r: r.json()['data']['content']),
                ('https://saying.api.azwcl.com/saying/get', lambda r: r.json()['data']['content'])
            ]
            
            random.shuffle(apis)
            
            for api_url, parse_func in apis:
                result = self._try_request_with_retry(api_url, parse_func, headers)
                if result:
                    # 更新缓存
                    self._update_cache(result)
                    return result
            
            # 如果所有API都失败了，返回备用语句
            log.warning("所有API请求都失败了，使用备用语句")
            return random.choice(self.fallback_quotes)
                
        except Exception as e:
            log.error(f"获取一言/诗词失败: {str(e)}")
            return random.choice(self.fallback_quotes)
            
    def _try_request_with_retry(self, api_url: str, parse_func: Callable, 
                               headers: dict, max_retries: int = 2) -> Optional[str]:
        """尝试请求API，支持重试机制"""
        for attempt in range(max_retries + 1):
            try:
                response = requests.get(api_url, headers=headers, timeout=3)
                
                if response.status_code == 200:
                    return parse_func(response)
                else:
                    log.warning(f"API {api_url} 返回状态码: {response.status_code}, 尝试 {attempt+1}/{max_retries+1}")
                    if attempt < max_retries:
                        time.sleep(0.5)  # 重试前等待
                    continue
                    
            except Exception as e:
                log.warning(f"API {api_url} 请求失败: {str(e)}, 尝试 {attempt+1}/{max_retries+1}")
                if attempt < max_retries:
                    time.sleep(0.5)  # 重试前等待
                continue
        
        return None
        
    def _update_cache(self, quote: str) -> None:
        """更新一言缓存"""
        if quote not in self.cached_quotes:
            if len(self.cached_quotes) >= self.max_cache_size:
                self.cached_quotes.pop(0)  # 移除最旧的缓存
            self.cached_quotes.append(quote)
            
        self.last_request_time = time.time()

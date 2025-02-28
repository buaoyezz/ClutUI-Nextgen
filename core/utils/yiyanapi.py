import requests
import random
from core.log.log_manager import log
from core.thread.thread_manager import thread_manager
from typing import Callable
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
        ]
        
    def get_hitokoto_async(self):
        """异步获取一言"""
        def fetch_hitokoto():
            result = self.get_hitokoto_sync()
            # 使用信号发送结果到主线程
            self.hitokoto_ready.emit(result)
            
        # 使用线程管理器提交任务
        thread_manager.submit_task("fetch_hitokoto", fetch_hitokoto)
        
        # 立即返回一个临时的一言
        return random.choice(self.fallback_quotes)
        
    def get_hitokoto_sync(self):
        # 获取一言，如果API失败则返回备用语句 
        try:
            # 添加请求头 
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Connection': 'keep-alive',
                'X-User': 'ClutUI-Nextgen'
            }
            
            apis = [
                ('https://v1.hitokoto.cn/', lambda r: r.json()['hitokoto']),
                ('https://api.oick.cn/yiyan/api.php', lambda r: r.json()['text']),
                ('https://api.apiopen.top/api/sentences', lambda r: r.json()['result']['name']),
                ('https://v1.jinrishici.com/all.json', lambda r: r.json()['content'])
            ]
            
            random.shuffle(apis)
            
            for api_url, parse_func in apis:
                try:
                    response = requests.get(api_url, headers=headers, timeout=3)
                    
                    if response.status_code == 200:
                        return parse_func(response)
                    else:
                        log.warning(f"API {api_url} 返回状态码: {response.status_code}")
                        continue
                        
                except Exception as e:
                    log.warning(f"API {api_url} 请求失败: {str(e)}")
                    continue
            
            # 如果所有API都失败了，返回备用语句
            log.warning("所有API请求都失败了，使用备用语句")
            return random.choice(self.fallback_quotes)
                
        except Exception as e:
            log.error(f"获取一言/诗词失败: {str(e)}")
            return random.choice(self.fallback_quotes)

import requests
import random
from core.log.log_manager import log

class YiyanAPI:
    def __init__(self):
        # 备用的一言列表，当API请求失败时使用 
        self.fallback_quotes = [
            "生活就像一盒巧克力，你永远不知道下一颗是什么味道",
            "保持简单，保持整洁",
            "整理空间，整理心情", 
            "让我们一起开始清理之旅吧",
            "干净整洁的环境，清晰的思维",
            "收拾房间，收拾心情",
            "整洁的环境，美好的心情",
            "让生活更轻松一点",
            "为美好生活增添一份整洁",
            "从清理开始，让生活更美好"
        ]
        
    def get_hitokoto_sync(self):
        # 获取一言，如果API失败则返回备用语句 
        try:
            # 添加请求头 
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'X-User': 'Clut-Cleaner'
            }
            
            # 随机选择API 
            apis = [
                ('https://v1.hitokoto.cn/', lambda r: r.json()['hitokoto']),
                ('https://v1.jinrishici.com/all.json', lambda r: r.json()['content'])
            ]
            api_url, parse_func = random.choice(apis)
            
            # 使用timeout参数避免请求卡住 
            response = requests.get(api_url, headers=headers, timeout=3)
            
            if response.status_code == 200:
                return parse_func(response)
            else:
                log.warning(f"API返回状态码: {response.status_code}")
                return random.choice(self.fallback_quotes)
                
        except Exception as e:
            log.error(f"获取一言/诗词失败: {str(e)}")
            return random.choice(self.fallback_quotes)

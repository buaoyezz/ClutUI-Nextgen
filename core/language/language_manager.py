from PySide6.QtCore import QObject, Signal
from core.i18n import i18n
from core.log.log_manager import log

class LanguageManager(QObject):
    # 定义信号
    language_changed = Signal(str)
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LanguageManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            super().__init__()
            self._initialized = True
            self._pages = []
            log.info("初始化语言管理器")
            
    def register_page(self, page):
        if page not in self._pages:
            self._pages.append(page)
            log.info(f"注册页面到语言管理器: {page.__class__.__name__}")
            
    def unregister_page(self, page):
        if page in self._pages:
            self._pages.remove(page)
            log.info(f"从语言管理器移除页面: {page.__class__.__name__}")
            
    def change_language(self, lang):
        try:
            # 设置新语言
            i18n.set_language(lang)
            
            # 更新所有注册的页面
            for page in self._pages:
                if hasattr(page, 'refresh_ui_texts'):
                    page.refresh_ui_texts()
            
            # 发送语言改变信号
            self.language_changed.emit(lang)
            log.info(f"语言已更改为: {lang}")
            
        except Exception as e:
            log.error(f"更改语言时出错: {str(e)}")
            
    def get_current_language(self):
        return i18n.current_language
        
    def get_available_languages(self):
        return {
            "简体中文": "zh",
            "繁體中文": "zh_hk",
            "English": "en",
            "Origin": "origin"
        }
        
language_manager = LanguageManager() 
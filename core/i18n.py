import json
import os
from typing import Dict, List, Optional, Callable
from PySide6.QtCore import QObject, Signal, QEvent, QCoreApplication

class I18nManager(QObject):
    language_changed = Signal(str)  # 语言变更信号
    
    _instance = None
    _current_language = 'zh'
    _fallback_language = 'en'
    _translations: Dict[str, Dict[str, str]] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(I18nManager, cls).__new__(cls)
            cls._instance._load_translations()
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            super().__init__()
            self._initialized = True
    
    def _load_translations(self):
        locales_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'locales')
        for file in os.listdir(locales_dir):
            if file.endswith('.json'):
                lang = file.split('.')[0]
                with open(os.path.join(locales_dir, file), 'r', encoding='utf-8') as f:
                    self._translations[lang] = json.load(f)
    
    @property
    def current_language(self) -> str:
        return self._current_language
    
    @property
    def available_languages(self) -> List[str]:
        return list(self._translations.keys())
    
    def set_language(self, lang: str):
        if lang not in self._translations:
            return
            
        if self._current_language != lang:
            # 清理所有通知
            from core.utils.notif import Notification
            Notification.clear_all_notifications()
            
            self._current_language = lang
            # 发送Qt语言变更事件
            event = QEvent(QEvent.LanguageChange)
            QCoreApplication.sendEvent(QCoreApplication.instance(), event)
            # 发送自定义信号
            self.language_changed.emit(lang)
    
    def get_text(self, key: str, *args, **kwargs) -> str:
        try:
            text = self._translations[self._current_language][key]
        except KeyError:
            try:
                text = self._translations[self._fallback_language][key]
            except KeyError:
                return key
                
        if args or kwargs:
            try:
                return text.format(*args, **kwargs)
            except (IndexError, KeyError):
                return text
        return text

i18n = I18nManager() 
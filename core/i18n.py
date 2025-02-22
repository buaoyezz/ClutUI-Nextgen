import json
import os
from typing import Dict, List, Optional, Callable
from PySide6.QtCore import QObject, Signal

class I18nManager(QObject):
    language_changed = Signal(str)  # 语言变更信号
    
    _instance = None
    _current_language = 'zh'
    _fallback_language = 'en'
    _translations: Dict[str, Dict[str, str]] = {}
    _callbacks: List[Callable] = []
    _is_notifying = False  # 添加标志位防止递归
    
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
            self._current_language = lang
            if not self._is_notifying:
                self._notify_language_change()
    
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
    
    def add_language_change_callback(self, callback: Callable):
        if callback not in self._callbacks:
            self._callbacks.append(callback)
    
    def remove_language_change_callback(self, callback: Callable):
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def _notify_language_change(self):
        if self._is_notifying:
            return
            
        try:
            self._is_notifying = True
            # 先发送信号
            self.language_changed.emit(self._current_language)
            # 再调用回调函数
            for callback in self._callbacks[:]:  # 创建副本避免在迭代时修改
                try:
                    callback()
                except Exception as e:
                    print(f"Error in language change callback: {e}")
        finally:
            self._is_notifying = False

i18n = I18nManager() 
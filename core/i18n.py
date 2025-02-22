import json
import os
from typing import Dict

class I18nManager:
    _instance = None
    _current_language = 'zh'
    _translations: Dict[str, Dict[str, str]] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(I18nManager, cls).__new__(cls)
            cls._instance._load_translations()
        return cls._instance
    
    def _load_translations(self):
        locales_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'locales')
        for file in os.listdir(locales_dir):
            if file.endswith('.json'):
                lang = file.split('.')[0]
                with open(os.path.join(locales_dir, file), 'r', encoding='utf-8') as f:
                    self._translations[lang] = json.load(f)
    
    @property
    def current_language(self):
        return self._current_language
    
    def set_language(self, lang: str):
        if lang in self._translations:
            self._current_language = lang
        else:
            raise ValueError(f"Language {lang} not supported")
    
    def get_text(self, key: str) -> str:
        try:
            return self._translations[self._current_language][key]
        except KeyError:
            return key

i18n = I18nManager() 
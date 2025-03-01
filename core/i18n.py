import json
import os
import sys
from typing import Dict, List, Optional, Callable
from PySide6.QtCore import QObject, Signal, QEvent, QCoreApplication
from core.log.log_manager import log
from core.utils.resource_manager import ResourceManager

class I18nManager(QObject):
    language_changed = Signal()
    
    def __init__(self):
        super().__init__()
        self.current_language = "en"
        self.translations = {}
        self.base_translations = {}
        self.resource_manager = ResourceManager()
        self.load_base_translations()
        
    def load_base_translations(self):
        try:
            base_path = ResourceManager.get_resource_path(os.path.join("locales", "base.json"))
            if os.path.exists(base_path):
                with open(base_path, 'r', encoding='utf-8') as f:
                    self.base_translations = json.load(f)
                log.info(f"已加载基础翻译文件")
            else:
                log.warning(f"基础翻译文件不存在: {base_path}")
        except Exception as e:
            log.error(f"加载基础翻译文件失败: {str(e)}")
    
    def set_language(self, language):
        return self.load_language(language)
            
    def load_language(self, language):
        try:
            lang_path = ResourceManager.get_resource_path(os.path.join("locales", f"{language}.json"))
            if os.path.exists(lang_path):
                with open(lang_path, 'r', encoding='utf-8') as f:
                    lang_translations = json.load(f)
                    
                # 合并基础翻译和语言特定翻译
                self.translations = {**self.base_translations, **lang_translations}
                self.current_language = language
                self.language_changed.emit()
                log.info(f"已加载语言: {language}")
                return True
            else:
                log.warning(f"语言文件不存在: {lang_path}")
                return False
        except Exception as e:
            log.error(f"加载语言失败: {str(e)}")
            return False
            
    def get_text(self, key, default=None):
        # 处理嵌套键，如 "urls.changelog"
        if "." in key:
            parts = key.split(".")
            value = self.translations
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return default or key
            return value
            
        # 普通键
        return self.translations.get(key, default or key)

# 创建全局实例
i18n = I18nManager() 
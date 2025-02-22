from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from core.ui.card_white import CardWhite
from core.ui.white_combox import WhiteComboBox
from core.ui.switch import QSwitch
from core.font.font_pages_manager import FontPagesManager
from core.i18n import i18n
from PySide6.QtCore import Qt
import winreg
import os
import sys
import json

class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.font_pages_manager = FontPagesManager()
        # 语言显示映射
        self.lang_display = {
            "zh": "简体中文",
            "en": "English",
            "zh_hk": "繁體中文",
            "origin": "Origin"
        }
        # 反向映射
        self.lang_map = {v: k for k, v in self.lang_display.items()}
        
        # 从配置文件读取语言设置
        try:
            with open('config.json', 'r') as f:
                config = json.loads(f.read())
                saved_lang = config.get('language')
                if saved_lang:
                    i18n.set_language(saved_lang)
        except:
            pass
            
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)
        self.setup_ui()
        
    def setup_ui(self):
        # 语言设置卡片
        self.language_card = CardWhite(
            i18n.get_text("language_settings"),
            i18n.get_text("language_settings_desc"),
            False
        )
        self.language_card.setStyleSheet("""
            CardWhite {
                background: #FFFFFF;
                border-radius: 12px;
                border: 2px solid #2196F3;
            }
        """)
        
        language_layout = QHBoxLayout()
        language_layout.setContentsMargins(24, 0, 24, 20)
    
        self.language_label = QLabel(i18n.get_text("interface_language"))
        self.font_pages_manager.apply_normal_style(self.language_label)
        
        # 语言选择框
        self.language_combo = WhiteComboBox()
        self.language_combo.setFocusPolicy(Qt.NoFocus)
        
        # 添加语言选项
        for lang_code, display_name in self.lang_display.items():
            self.language_combo.addItem(display_name, lang_code)
        
        # 设置当前语言
        current_lang = i18n.current_language
        current_index = self.language_combo.findData(current_lang)
        if current_index >= 0:
            self.language_combo.setCurrentIndex(current_index)
        
        # 连接信号
        self.language_combo.currentIndexChanged.connect(self._on_language_selection_changed)
        
        self.language_combo.setStyleSheet("""
            QComboBox {
                background: white;
                border: 2px solid #2196F3;
                border-radius: 8px;
                color: #333333;
                padding: 4px 12px;
                min-height: 32px;
                font-size: 14px;
                letter-spacing: 0.3px;
                outline: none;
            }
            QComboBox:focus {
                outline: none;
                border: 2px solid #2196F3;
            }
            QComboBox::drop-down {
                border: none;
                width: 24px;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
            QComboBox QAbstractItemView {
                background: white;
                border: 2px solid #2196F3;
                border-radius: 8px;
                outline: none;
                selection-background-color: rgba(33, 150, 243, 0.1);
                selection-color: #2196F3;
            }
            QComboBox QAbstractItemView::item {
                min-height: 32px;
                padding: 4px 12px;
                letter-spacing: 0.3px;
                outline: none;
            }
            QComboBox QAbstractItemView::item:hover {
                background: rgba(33, 150, 243, 0.05);
            }
        """)
        
        language_layout.addWidget(self.language_label)
        language_layout.addWidget(self.language_combo)
        language_layout.addStretch()
        
        self.language_card.layout().addLayout(language_layout)
        
        # 开机自启动卡片
        self.startup_card = CardWhite(
            i18n.get_text("auto_start"),
            i18n.get_text("auto_start_desc"),
            False
        )
        self.startup_card.setStyleSheet("""
            CardWhite {
                background: #FFFFFF;
                border-radius: 12px;
                border: 2px solid #2196F3;
            }
        """)
        
        startup_layout = QHBoxLayout()
        startup_layout.setContentsMargins(24, 0, 24, 20)
        
        self.startup_label = QLabel(i18n.get_text("auto_start"))
        self.font_pages_manager.apply_normal_style(self.startup_label)
        
        self.startup_switch = QSwitch()
        self.startup_switch.setChecked(self.is_startup_enabled())
        self.startup_switch.stateChanged.connect(self.on_startup_changed)
        
        startup_layout.addWidget(self.startup_label)
        startup_layout.addWidget(self.startup_switch)
        startup_layout.addStretch()
        
        self.startup_card.layout().addLayout(startup_layout)
        
        # 添加自动保存配置卡片
        self.auto_save_card = CardWhite(
            i18n.get_text("auto_save"),
            i18n.get_text("auto_save_desc"),
            False
        )
        self.auto_save_card.setStyleSheet("""
            CardWhite {
                background: #FFFFFF;
                border-radius: 12px;
                border: 2px solid #2196F3;
            }
        """)
        
        auto_save_layout = QHBoxLayout()
        auto_save_layout.setContentsMargins(24, 0, 24, 20)
        
        self.auto_save_label = QLabel(i18n.get_text("auto_save"))
        self.font_pages_manager.apply_normal_style(self.auto_save_label)
        
        self.auto_save_switch = QSwitch()
        self.auto_save_switch.setChecked(self.is_auto_save_enabled())
        self.auto_save_switch.stateChanged.connect(self.on_auto_save_changed)
        
        auto_save_layout.addWidget(self.auto_save_label)
        auto_save_layout.addWidget(self.auto_save_switch)
        auto_save_layout.addStretch()
        
        self.auto_save_card.layout().addLayout(auto_save_layout)
        
        # 添加卡片到主布局
        self.layout.addWidget(self.language_card)
        self.layout.addWidget(self.startup_card)
        self.layout.addWidget(self.auto_save_card)
        self.layout.addStretch()
        
        # 注册语言变更回调
        i18n.add_language_change_callback(self.update_text)

    def update_text(self):
        # 更新语言卡片
        self.language_card.title_label.setText(i18n.get_text("language_settings"))
        self.language_card.description_label.setText(i18n.get_text("language_settings_desc"))
        self.language_label.setText(i18n.get_text("interface_language"))
        
        # 更新自启动卡片
        self.startup_card.title_label.setText(i18n.get_text("auto_start"))
        self.startup_card.description_label.setText(i18n.get_text("auto_start_desc"))
        self.startup_label.setText(i18n.get_text("auto_start"))
        
        # 更新自动保存卡片文本
        self.auto_save_card.title_label.setText(i18n.get_text("auto_save"))
        self.auto_save_card.description_label.setText(i18n.get_text("auto_save_desc"))
        self.auto_save_label.setText(i18n.get_text("auto_save"))
        
    def _on_language_selection_changed(self, index):
        lang_code = self.language_combo.itemData(index)
        if lang_code:
            i18n.set_language(lang_code)
            # 保存语言设置到配置文件
            try:
                config = {}
                try:
                    with open('config.json', 'r') as f:
                        config = json.loads(f.read())
                except:
                    pass
                    
                config['language'] = lang_code
                
                with open('config.json', 'w') as f:
                    json.dump(config, f, indent=4)
            except Exception as e:
                print(f"{i18n.get_text('save_config_error')}: {e}")
            
    def is_startup_enabled(self):
        # 先检查配置文件中的设置
        try:
            with open('config.json', 'r') as f:
                config = json.loads(f.read())
                return config.get('auto_start', False)
        except:
            return False
            
    def on_startup_changed(self, enabled):
        try:
            # 更新注册表
            if getattr(sys, 'frozen', False):
                app_path = sys.executable
            else:
                app_path = os.path.abspath(sys.argv[0])
                
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_WRITE | winreg.KEY_SET_VALUE
            )
            
            try:
                if enabled:
                    winreg.SetValueEx(
                        key,
                        "ClutUI",
                        0,
                        winreg.REG_SZ,
                        app_path
                    )
                else:
                    try:
                        winreg.DeleteValue(key, "ClutUI")
                    except WindowsError:
                        pass
            finally:
                winreg.CloseKey(key)
                
            # 保存到配置文件
            config = {}
            try:
                with open('config.json', 'r') as f:
                    config = json.loads(f.read())
            except:
                pass
                
            config['auto_start'] = bool(enabled)
            
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=4)
                
        except Exception as e:
            print(f"{i18n.get_text('startup_setting_error')}: {e}")

    def is_auto_save_enabled(self):
        # 从配置文件读取自动保存设置
        try:
            with open('config.json', 'r') as f:
                config = json.loads(f.read())
                return config.get('auto_save', False)
        except:
            return False
            
    def on_auto_save_changed(self, enabled):
        # 保存自动保存设置到配置文件
        try:
            config = {}
            try:
                with open('config.json', 'r') as f:
                    config = json.loads(f.read())
            except:
                pass
                
            config['auto_save'] = bool(enabled)
            
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"{i18n.get_text('save_config_error')}: {e}")

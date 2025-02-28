class ScrollStyle:
    
    @staticmethod
    def get_style(theme="default"):
        # 主题颜色配置
        themes = {
            "default": {
                "background": "transparent",
                "handle": "rgba(144, 147, 153, 0.3)",
                "handle_hover": "rgba(144, 147, 153, 0.5)",
                "handle_pressed": "rgba(144, 147, 153, 0.7)"
            },
            "dark": {
                "background": "transparent",
                "handle": "rgba(200, 200, 200, 0.3)",
                "handle_hover": "rgba(200, 200, 200, 0.5)",
                "handle_pressed": "rgba(200, 200, 200, 0.7)"
            },
            "light": {
                "background": "#F0F0F0",
                "handle": "#BDBDBD",
                "handle_hover": "#9E9E9E",
                "handle_pressed": "#757575"
            }
        }
        
        # 获取选定主题的颜色
        colors = themes.get(theme, themes["default"])
        
        return f"""
            QScrollBar:vertical {{
                border: none;
                background: {colors['background']};
                width: 8px;
                margin: 4px 4px 4px 4px;
            }}
            
            QScrollBar::handle:vertical {{
                background: {colors['handle']};
                border-radius: 4px;
                min-height: 30px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background: {colors['handle_hover']};
            }}
            
            QScrollBar::handle:vertical:pressed {{
                background: {colors['handle_pressed']};
            }}
            
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
            
            /* 水平滚动条 */
            QScrollBar:horizontal {{
                border: none;
                background: {colors['background']};
                height: 8px;
                margin: 4px 4px 4px 4px;
            }}
            
            QScrollBar::handle:horizontal {{
                background: {colors['handle']};
                border-radius: 4px;
                min-width: 30px;
            }}
            
            QScrollBar::handle:horizontal:hover {{
                background: {colors['handle_hover']};
            }}
            
            QScrollBar::handle:horizontal:pressed {{
                background: {colors['handle_pressed']};
            }}
            
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
            
            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal {{
                background: transparent;
            }}
        """
    
    @staticmethod
    def apply_to_widget(widget, theme="default"):
        widget.setStyleSheet(ScrollStyle.get_style(theme)) 
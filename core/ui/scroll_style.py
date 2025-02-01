class ScrollStyle:
    
    @staticmethod
    def get_style():
        return """
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 6px;
                margin: 0px;
            }
            
            QScrollBar::handle:vertical {
                background: rgba(0, 0, 0, 0.2);
                border-radius: 3px;
                min-height: 30px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: rgba(0, 0, 0, 0.3);
            }
            
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: none;
            }
            
            /* 水平滚动条 */
            QScrollBar:horizontal {
                border: none;
                background: transparent;
                height: 6px;
                margin: 0px;
            }
            
            QScrollBar::handle:horizontal {
                background: rgba(0, 0, 0, 0.2);
                border-radius: 3px;
                min-width: 30px;
            }
            
            QScrollBar::handle:horizontal:hover {
                background: rgba(0, 0, 0, 0.3);
            }
            
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                width: 0px;
            }
            
            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal {
                background: none;
            }
        """ 
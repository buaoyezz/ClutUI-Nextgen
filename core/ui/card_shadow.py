from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtGui import QColor

class CardShadow:
    @staticmethod
    def get_shadow(parent):
        shadow = QGraphicsDropShadowEffect(parent)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 1)
        return shadow 
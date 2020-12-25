from PyQt5.QtCore import QRect, Qt
from PyQt5.QtGui import QPixmap, QPainter, QImage
from PyQt5.QtWidgets import QLabel

from pieces.piece import Alliance


class Tile(QLabel):
    def __init__(self, parent):
        super().__init__(parent)


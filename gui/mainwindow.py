from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QMainWindow, QWidget, QGridLayout

from chess_board.board import Board
from pieces.piece import EmptyPiece
from resolutions import monitor_size


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()

        self.w_partial, self.h_partial = monitor_size()

        self.setStyleSheet("background: white")

        # Init Window
        self.setWindowTitle("Chess")
        self.setGeometry(320, 180, int(1280 * self.w_partial), int(720 * self.h_partial))

        self.main_widget = MainWindow(self)
        self.setCentralWidget(self.main_widget)


class MainWindow(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.main_layout = QGridLayout(self)
        self.board = Board()
        print(self.board.white_player.is_check())


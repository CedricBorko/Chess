from PyQt5.QtCore import QModelIndex
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout

from chess_board.board import Board
from pieces.piece import Piece
from pieces.player import Player
from resolutions import monitor_size


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()

        self.w_partial, self.h_partial = monitor_size()

        # Init Window
        self.setWindowTitle("Chess")
        self.setGeometry(320, 180, int(1280 * self.w_partial), int(720 * self.h_partial))

        self.main_widget = MainWindow(self)
        self.setCentralWidget(self.main_widget)


class MainWindow(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.main_layout = QHBoxLayout(self)
        self.board = Board(self, [Piece((0, 0), Player.White)])



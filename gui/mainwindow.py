from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QMainWindow, QWidget, QGridLayout

from chess_board.board import Board
from pieces.alliance import Alliance
from pieces.rook import Rook
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
        self.b = Board()
        self.b.set_up()
        self.tile_size = 50
        self.selected_piece = None

    def paintEvent(self, QPaintEvent):
        qp = QPainter(self)

        if self.selected_piece is not None and self.selected_piece in self.b.current_player.get_active_pieces():
            qp.fillRect(QRect(self.selected_piece.x * self.tile_size, self.selected_piece.y * self.tile_size,
                              self.tile_size, self.tile_size), Qt.yellow)
            for move in self.selected_piece.legal_moves:
                qp.fillRect(QRect(move.x * self.tile_size, move.y * self.tile_size,
                                  self.tile_size, self.tile_size), Qt.lightGray)

        for i in range(len(self.b.board)):
            piece = self.b.get_piece(i)

            rect = QRect((i % 8) * self.tile_size, (i // 8) * self.tile_size, self.tile_size, self.tile_size)
            qp.drawRect(rect)
            if piece:
                qp.drawText(rect, Qt.AlignCenter, self.b.get_piece(i).Name)
            else:
                qp.drawText(rect, Qt.AlignCenter, "")

    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.LeftButton:
            x, y = QMouseEvent.pos().x() // self.tile_size, QMouseEvent.pos().y() // self.tile_size
            index = y * 8 + x
            if 0 <= x < 8 and 0 <= y < 8:
                if self.selected_piece is not None:
                    selected_move = self.selected_piece.get_move(index)
                    if selected_move is not None and self.selected_piece in self.b.current_player.get_active_pieces():
                        if selected_move.move():
                            self.update()
                            # print(self.b.board[index].legal_moves)
                            self.selected_piece = None
                            return
                self.selected_piece = self.b.get_piece(index)
                self.update()

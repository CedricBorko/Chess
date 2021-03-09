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
        self.board.setup()
        for i in range(1, 9):
            for letter in "abcdefgh":
                piece = self.board.letter_code(letter, i)
                if not isinstance(piece, EmptyPiece):
                    piece.calculate_legal_moves(self.board)
                    print(self.board.letter_code(letter, i).legal_moves)

    """def paintEvent(self, QPaintEvent):
        qp = QPainter(self)

        if self.selected_piece is not None:
            qp.fillRect(QRect(self.selected_piece.col * self.tile_size, self.selected_piece.row * self.tile_size,
                              self.tile_size, self.tile_size), Qt.yellow)
            for move in self.selected_piece.legal_moves:
                qp.fillRect(QRect(move.col * self.tile_size, move.row * self.tile_size,
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
                    if selected_move is not None:
                        temp_board = selected_move.execute()
                        if temp_board.is_valid():
                            self.b = temp_board
                            self.b.update()
                            print(self.b.current_player)
                        else:
                            temp_board = selected_move.undo()
                            self.selected_piece.legal_moves.remove(selected_move)

                        self.selected_piece = None
                        self.update()
                        return
                self.selected_piece = self.b.get_piece(index)
                self.update()"""

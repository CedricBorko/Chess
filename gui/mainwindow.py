import copy

from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QMainWindow, QWidget, QGridLayout

from chess_board.board import Board
from chess_board.utils import letter_code_to_number
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

        while True:
            if self.board.current_player.is_checkmate():
                print(self.board.current_player.opponent().__class__.__name__, "wins!")
                break

            if self.board.current_player.is_stalemate():
                print("Tie!")
                break
            mover = input("> ")
            letter, number = mover[0], int(mover[1])
            piece = self.board.letter_code(letter, number)
            self.board.calculate_legal_moves()

            if piece.alliance != self.board.current_player.alliance:
                continue
            if len(piece.legal_moves) == 0:
                continue
            if isinstance(piece, EmptyPiece):
                continue

            updated_legal_moves = []
            copied_board = copy.deepcopy(self.board)
            for move in piece.legal_moves:
                piece.make_move(copied_board, move)
                if not copied_board.current_player.is_check(copied_board):
                    updated_legal_moves.append(move)
                copied_board = copy.deepcopy(self.board)

            piece.legal_moves = updated_legal_moves
            print(piece.legal_moves)
            if len(piece.legal_moves) == 0:
                continue

            move = input("> ")
            letter, number = move[0], int(move[1])
            target = letter_code_to_number(letter, number)

            move = piece.get_move(target)
            piece.make_move(self.board, move)
            self.board.current_player.next_player()
            print("-" * 50)
            print(self.board)

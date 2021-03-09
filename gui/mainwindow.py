import copy

from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QImage
from PySide6.QtWidgets import QMainWindow, QWidget, QGridLayout

from chess_board.board import Board
from chess_board.utils import letter_code_to_number, valid_target
from pieces.king import King
from pieces.piece import EmptyPiece
from resolutions import monitor_size


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()

        self.w_partial, self.h_partial = monitor_size()

        self.setStyleSheet("background: white")

        # Init Window
        self.setWindowTitle("Chess")
        self.setGeometry(300, 100, 1000, 1000)

        self.main_widget = MainWindow(self)
        self.setCentralWidget(self.main_widget)


class MainWindow(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.main_layout = QGridLayout(self)
        self.selected_piece = None
        self.board = Board()

        """while True:
            print("-" * 50)

            if self.board.current_player.is_checkmate():
                print(self.board.current_player.opponent().__class__.__name__, "wins!")
                break

            if self.board.current_player.is_stalemate():
                print("Tie!")
                break

            print(self.board.current_player.__class__.__name__, "'s turn")

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

            
            print(piece.legal_moves)
            if len(piece.legal_moves) == 0:
                continue

            move = input("> ")
            letter, number = move[0], int(move[1])
            target = letter_code_to_number(letter, number)

            move = piece.get_move(target)
            try:
                piece.make_move(self.board, move)
            except AttributeError:
                continue

            if isinstance(piece, King):
                self.board.current_player.king.first_move = False

            self.board.current_player.next_player()
            print(self.board)"""

    def paintEvent(self, QPaintEvent):
        qp = QPainter(self)

        if self.selected_piece is not None and not isinstance(self.selected_piece, EmptyPiece):
            x, y = self.selected_piece.position % 8, self.selected_piece.position // 8
            for move in self.selected_piece.legal_moves:
                qp.fillRect(move.target % 8 * 100, move.target // 8 * 100, 100, 100, Qt.green)

        for i in range(64):
            piece = self.board.get_piece(i)
            if not isinstance(piece, EmptyPiece):
                qp.drawImage(QRect(i % 8 * 100, i // 8 * 100, 100, 100),
                             QImage(f"pieces/images/{piece.alliance.lower()}/{piece.__class__.__name__}.png"))

        for i in range(8):
            for j in range(8):
                qp.drawRect(i * 100, j * 100, 100, 100)

    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.LeftButton:
            x, y = QMouseEvent.pos().x() // 100, QMouseEvent.pos().y() // 100
            pos = y * 8 + x
            if self.selected_piece is None:
                if valid_target(pos):
                    if not isinstance(self.board.get_piece(pos), EmptyPiece):
                        self.selected_piece = self.board.get_piece(pos)
                        updated_legal_moves = []
                        copied_board = copy.deepcopy(self.board)
                        for move in self.selected_piece.legal_moves:
                            self.selected_piece.make_move(copied_board, move)
                            if not copied_board.current_player.is_check(copied_board):
                                updated_legal_moves.append(move)
                            copied_board = copy.deepcopy(self.board)

                        self.selected_piece.legal_moves = updated_legal_moves

                        self.update()
            else:
                move = self.selected_piece.get_move(pos)
                if move is not None and self.board.current_player.alliance == self.selected_piece.alliance:
                    self.selected_piece.make_move(self.board, move)
                    self.selected_piece = None
                    self.board.current_player.next_player()
                    self.board.calculate_legal_moves()
                    self.update()
                else:
                    piece = self.board.get_piece(pos)
                    if not isinstance(piece, EmptyPiece):
                        self.selected_piece = piece
                        self.update()

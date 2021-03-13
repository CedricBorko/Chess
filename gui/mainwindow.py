import copy
from concurrent.futures import ProcessPoolExecutor
from threading import Thread

from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QImage, QFont, QColor, QBrush, QPen
from PySide6.QtWidgets import QMainWindow, QWidget, QGridLayout, QLabel, QHBoxLayout, QGroupBox, QPushButton

from board_.board import Board
from board_.move import AttackMove, PromotionMove, CastleMove, EnPassantMove, EnPassantAttackMove, Move
from board_.utils import valid_target
from pieces.bishop import Bishop
from pieces.king import King
from pieces.knight import Knight
from pieces.piece import EmptyPiece
from pieces.queen import Queen
from pieces.rook import Rook
from resolutions import monitor_size


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()

        self.w_partial, self.h_partial = monitor_size()

        self.setStyleSheet("background: white")

        # Init Window
        self.setWindowTitle("Chess")
        self.setGeometry(300, 80, 1400, 1000)

        self.main_widget = MainWindow(self)
        self.setCentralWidget(self.main_widget)


class MainWindow(QWidget):
    TILE_SIZE = 100

    def __init__(self, parent):
        super().__init__(parent)

        self.main_layout = QGridLayout(self)
        self.selected_piece = None
        self.stale_mate = self.check_mate = False
        self.promotion_move = None
        self.promoting = False
        self.moves_done = []
        self.board = Board()

        self.moves_label = QLabel(self)
        self.moves_label.setGeometry(900, 0, 500, 1000)
        self.moves_label.setFont(QFont("Arial", 16))
        self.moves_label.setAlignment(Qt.AlignHCenter)

        self.promotion_view = QGroupBox(self)
        self.promotion_view.setGeometry(700 // 2 - 200, 500 // 2 - 100, 800, 400)
        self.promotion_view.setLayout(QHBoxLayout())
        self.promotion_view.setVisible(False)

        self.promotions = [QPushButton("Queen", self), QPushButton("Knight", self),
                           QPushButton("Bishop", self), QPushButton("Rook", self)]

        for p in self.promotions:
            p.clicked.connect(self.choose_promotion)
            self.promotion_view.layout().addWidget(p)

    def paintEvent(self, QPaintEvent):
        qp = QPainter(self)
        qp.setPen(QPen(Qt.black, 3))
        qp.setRenderHint(QPainter.Antialiasing)

        for i in range(8):
            for j in range(8):
                if (i + j) % 2 == 0:
                    qp.setBrush(QBrush(QColor("#F2D9BB")))
                else:
                    qp.setBrush(QBrush(QColor("#BF8A6B")))
                qp.drawRect(i * self.TILE_SIZE, j * self.TILE_SIZE, self.TILE_SIZE, self.TILE_SIZE)

        if self.selected_piece is not None:
            qp.setBrush(QBrush(QColor("#6495ED")))
            qp.drawRect(self.selected_piece.position % 8 * self.TILE_SIZE,
                        self.selected_piece.position // 8 * self.TILE_SIZE,
                        self.TILE_SIZE, self.TILE_SIZE)

        if self.selected_piece is not None and not isinstance(self.selected_piece, EmptyPiece):
            if self.selected_piece.alliance == self.board.current_player.alliance:
                for move in self.selected_piece.legal_moves:
                    if isinstance(move, AttackMove) or isinstance(move, EnPassantAttackMove) \
                        or (isinstance(move, PromotionMove) and move.attacked_piece is not None):

                        qp.setBrush(QBrush(QColor("#FF495A")))
                    else:
                        qp.setBrush(QBrush(QColor("#80F576")))

                    qp.drawRect(move.target % 8 * self.TILE_SIZE, move.target // 8 * self.TILE_SIZE,
                                self.TILE_SIZE, self.TILE_SIZE)

        for i in range(64):
            piece = self.board.get_piece(i)
            if not isinstance(piece, EmptyPiece):
                qp.drawImage(QRect(i % 8 * self.TILE_SIZE, i // 8 * self.TILE_SIZE, self.TILE_SIZE, self.TILE_SIZE),
                             QImage(f"pieces/images/set1/{piece.alliance.lower()}/{piece.__class__.__name__}.png"))

        qp.setFont(QFont("Arial", 32))

        for l, (letter, number) in enumerate(zip("abcdefgh", "87654321")):
            qp.drawText(QRect(l * self.TILE_SIZE, self.TILE_SIZE * 8, self.TILE_SIZE, self.TILE_SIZE), Qt.AlignCenter,
                        letter)
            qp.drawText(QRect(self.TILE_SIZE * 8, l * self.TILE_SIZE, self.TILE_SIZE, self.TILE_SIZE), Qt.AlignCenter,
                        number)

        if self.check_mate:
            qp.drawText(QRect(0, 0, self.width(), self.height()), Qt.AlignCenter,
                        "Checkmate " + self.board.current_player.opponent().__str__() + " wins!")

        if self.stale_mate:
            qp.drawText(QRect(0, 0, self.width(), self.height()), Qt.AlignCenter, "Tie!")

    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.LeftButton:
            x, y = QMouseEvent.pos().x() // self.TILE_SIZE, QMouseEvent.pos().y() // self.TILE_SIZE
            pos = y * 8 + x

            if not (self.check_mate or self.stale_mate):
                if valid_target(pos):
                    if self.selected_piece is None:
                        if not isinstance(self.board.get_piece(pos), EmptyPiece):
                            self.selected_piece = self.board.get_piece(pos)
                            self.update_legal_moves()
                            self.update()
                    else:
                        if not isinstance(self.board.get_piece(pos), EmptyPiece):
                            self.update_legal_moves()
                            self.update()

                        move = self.selected_piece.get_move(pos)

                        if move is not None and self.board.current_player.alliance == self.selected_piece.alliance:
                            if isinstance(move, PromotionMove) and not self.promoting:
                                self.promotion_view.setVisible(True)
                                self.promoting = True
                                self.promotion_move = move

                            if not self.promoting:

                                if isinstance(move, EnPassantMove):
                                    if move not in self.board.active_en_passant:
                                        self.board.active_en_passant.append(move)

                                if isinstance(self.selected_piece, King):
                                    self.board.current_player.king_first_move = False

                                move.execute(self.board)

                                self.moves_done.append(move)
                                self.moves_label.setText('\n'.join(map(str, self.moves_done)))
                                self.selected_piece = None
                                self.board.current_player.next_player()
                                self.board.calculate_legal_moves()
                                if self.board.current_player.is_check(self.board):
                                    self.check_mate = self.board.current_player.is_checkmate()
                                else:
                                    self.stale_mate = self.board.current_player.is_stalemate()

                                self.update()
                        else:
                            piece = self.board.get_piece(pos)
                            if not isinstance(piece, EmptyPiece):
                                self.selected_piece = piece
                                self.update()

        elif QMouseEvent.button() == Qt.RightButton:
            if len(self.moves_done) > 0 and not (self.check_mate or self.stale_mate):
                move = self.moves_done.pop()
                move.undo(self.board)
                self.board.current_player.next_player()
                self.selected_piece = None
                self.board.calculate_legal_moves()
                self.moves_label.setText('\n'.join(map(str, self.moves_done)))
                self.update()

    def choose_promotion(self):
        name = self.sender().text()
        if self.promotion_move is not None:
            pieces = {"Queen": Queen(self.promotion_move.target, self.selected_piece.alliance),
                      "Knight": Knight(self.promotion_move.target, self.selected_piece.alliance),
                      "Bishop": Bishop(self.promotion_move.target, self.selected_piece.alliance),
                      "Rook": Rook(self.promotion_move.target, self.selected_piece.alliance)}
            piece = pieces[name]

            self.promotion_move.promotion_to = piece
            self.moves_done.append(self.promotion_move)
            self.promoting = False
            self.promotion_view.setVisible(False)

            self.promotion_move.execute(self.board)
            self.moves_label.setText('\n'.join(map(str, self.moves_done)))
            self.selected_piece = None
            self.promotion_move = None
            self.board.current_player.next_player()
            self.board.calculate_legal_moves()

            if self.board.current_player.is_check(self.board):
                self.check_mate = self.board.current_player.is_checkmate()
            else:
                self.stale_mate = self.board.current_player.is_stalemate()

            self.update()

    def update_legal_moves(self):
        updated_legal_moves = []
        copied_board = copy.deepcopy(self.board)
        for move in self.selected_piece.legal_moves:
            move.execute(copied_board)
            if not copied_board.current_player.is_check(copied_board):
                updated_legal_moves.append(move)
            copied_board = copy.deepcopy(self.board)

        if isinstance(self.selected_piece, King):
            for m in self.selected_piece.legal_moves:
                if isinstance(m, CastleMove) and self.board.current_player.is_check(self.board):
                    updated_legal_moves.remove(m)

        self.selected_piece.legal_moves = updated_legal_moves

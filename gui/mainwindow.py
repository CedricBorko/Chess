import copy
import time
from threading import Thread

from PySide6.QtCore import Qt, QRect, QSize, QPoint
from PySide6.QtGui import QPainter, QImage, QFont, QColor, QBrush, QPen, QIcon, QPixmap, QPainterPath
from PySide6.QtWidgets import QMainWindow, QWidget, QGridLayout, QLabel, QHBoxLayout, QGroupBox, QPushButton, \
    QSizePolicy

from board_.board import Board
from board_.move import AttackMove, PromotionMove, CastleMove, EnPassantMove, EnPassantAttackMove
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

        # Init Window
        self.setWindowTitle("Chess")
        self.setStyleSheet("QWidget{background: rgb(48, 48, 48)}"
                           "QLabel{color: white; border: 1px solid white}")

        self.setMinimumSize(900, 600)

        self.main_widget = MainWidget(self)
        self.setCentralWidget(self.main_widget)
        self.main_widget.setMinimumSize(self.width(), self.height())

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.showNormal()
        elif e.key() == Qt.Key_F11:
            self.showFullScreen()

    def resizeEvent(self, QResizeEvent):
        self.main_widget.setMinimumSize(self.width(), self.height())
        self.main_widget.resizeEvent(QResizeEvent)


class MainWidget(QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.TILE_SIZE = 100
        self.OFFSET = self.TILE_SIZE // 2
        self.main_layout = QGridLayout(self)
        self.selected_piece = None
        self.stale_mate = self.check_mate = False
        self.promotion_move = None
        self.promoting = False
        self.board = Board()

        self.moves_label = QLabel(self)
        self.moves_label.setFont(QFont("TW Cen Mt", 14))
        self.moves_label.setAlignment(Qt.AlignHCenter)
        self.moves_label.setWordWrap(True)

        self.promotion_view = QGroupBox(self)
        self.promotion_view.setLayout(QGridLayout())
        self.promotion_view.setVisible(False)

        self.promotions = [QPushButton(self), QPushButton(self),
                           QPushButton(self), QPushButton(self)]

        for i, p in enumerate(self.promotions):
            p.clicked.connect(self.choose_promotion)
            p.setObjectName(["Bishop", "Knight", "Queen", "Rook"][i])
            p.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.promotion_view.layout().addWidget(p, i % 2, i // 2)

    def paintEvent(self, QPaintEvent):
        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing)
        qp.setPen(Qt.NoPen)

        for i in range(8):
            for j in range(8):
                qp.setPen(Qt.NoPen)
                if (i + j) % 2 == 0:
                    qp.setBrush(QBrush(QColor("#758C51")))
                else:
                    qp.setBrush(QBrush(QColor("#F2F0D8")))
                qp.drawRect(self.OFFSET + i * self.TILE_SIZE,
                            self.OFFSET + j * self.TILE_SIZE,
                            self.TILE_SIZE, self.TILE_SIZE)

                if i % 8 == 0:
                    qp.setPen(QPen(Qt.black))
                    qp.setFont(QFont("TW Cen Mt", self.height() // 40))
                    qp.drawText(QRect(self.OFFSET + i * self.TILE_SIZE,
                                      self.OFFSET + j * self.TILE_SIZE,
                                      self.TILE_SIZE, self.TILE_SIZE), "12345678"[7-j])

                if j == 7:
                    qp.setPen(QPen(Qt.black))
                    qp.drawText(QRect(self.OFFSET + i * self.TILE_SIZE,
                                      self.OFFSET + j * self.TILE_SIZE,
                                      self.TILE_SIZE, self.TILE_SIZE), "abcdefgh"[i], Qt.AlignBottom | Qt.AlignLeft)


        if self.selected_piece is not None:
            qp.setPen(QPen(QColor("#ffcc00"), 3))
            qp.setBrush(Qt.NoBrush)
            qp.drawRect(self.OFFSET + self.selected_piece.position % 8 * self.TILE_SIZE,
                        self.OFFSET + self.selected_piece.position // 8 * self.TILE_SIZE, self.TILE_SIZE, self.TILE_SIZE)
        qp.setPen(Qt.NoPen)
        for i in range(64):
            piece = self.board.get_piece(i)
            if not isinstance(piece, EmptyPiece):
                qp.drawImage(QRect(self.OFFSET + i % 8 * self.TILE_SIZE,
                                   self.OFFSET + i // 8 * self.TILE_SIZE,
                                   self.TILE_SIZE, self.TILE_SIZE),
                             QImage(f"pieces/images/set1/{piece.alliance.lower()}/{piece.__class__.__name__}.png"))

        if self.selected_piece is not None and not isinstance(self.selected_piece, EmptyPiece):
            if self.selected_piece.alliance == self.board.current_player.alliance:
                for move in self.selected_piece.legal_moves:
                    c = QColor(70, 70, 70)
                    c.setAlpha(120)
                    if isinstance(move, AttackMove) or isinstance(move, EnPassantAttackMove) \
                        or (isinstance(move, PromotionMove) and move.attacked_piece is not None):

                        qp.setBrush(QBrush(c))
                        path = QPainterPath()
                        path.addEllipse(QPoint(self.OFFSET + self.TILE_SIZE // 2 + move.target % 8 * self.TILE_SIZE,
                                    self.OFFSET + self.TILE_SIZE // 2 + move.target // 8 * self.TILE_SIZE),
                                        self.TILE_SIZE // 2, self.TILE_SIZE // 2)

                        path.addEllipse(QPoint(self.OFFSET + self.TILE_SIZE // 2 + move.target % 8 * self.TILE_SIZE,
                                              self.OFFSET + self.TILE_SIZE // 2 + move.target // 8 * self.TILE_SIZE),
                                       self.TILE_SIZE * 0.35, self.TILE_SIZE * 0.35)
                        qp.drawPath(path)

                    else:
                        qp.setBrush(QBrush(c))
                        qp.drawEllipse(QPoint(self.OFFSET + self.TILE_SIZE // 2 + move.target % 8 * self.TILE_SIZE,
                                    self.OFFSET + self.TILE_SIZE // 2 + move.target // 8 * self.TILE_SIZE),
                                    self.TILE_SIZE // 4, self.TILE_SIZE // 4)

        if self.check_mate:
            qp.drawText(QRect(0, 0, self.width(), self.height()), Qt.AlignCenter,
                        "Checkmate " + self.board.current_player.opponent().__str__() + " wins!")

        if self.stale_mate:
            qp.drawText(QRect(0, 0, self.width(), self.height()), Qt.AlignCenter, "Tie!")

    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.LeftButton:
            x = (-self.OFFSET + QMouseEvent.pos().x()) // self.TILE_SIZE
            y = (-self.OFFSET + QMouseEvent.pos().y()) // self.TILE_SIZE
            if 0 <= y < 8 and 0 <= x < 8:
                pos = y * 8 + x
            else:
                return
            if not (self.check_mate or self.stale_mate):
                if valid_target(pos):
                    if self.selected_piece is None:
                        if not isinstance(self.board.get_piece(pos), EmptyPiece):
                            self.selected_piece = self.board.get_piece(pos)
                            t = Thread(target=self.update_legal_moves)
                            t.start()
                            t.join()
                            self.update()

                    else:
                        piece = self.board.get_piece(pos)
                        if not isinstance(piece, EmptyPiece) and not piece == self.selected_piece:
                            t = Thread(target=self.update_legal_moves)
                            t.start()
                            t.join()
                            self.update()

                        move = self.selected_piece.get_move(pos)

                        if move is not None and self.board.current_player.alliance == self.selected_piece.alliance:
                            if isinstance(move, PromotionMove) and not self.promoting:
                                for p in self.promotions:
                                    p.setIcon(QIcon(
                                        f"pieces/images/set1/{self.selected_piece.alliance}/{p.objectName()}.png"))
                                    p.setIconSize(QSize(self.TILE_SIZE, self.TILE_SIZE))
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

                                self.board.moves_done.append(move)
                                self.board.current_player.moves_done.append(move)
                                self.moves_label.setText(''.join(map(str, self.board.moves_done)))
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
            if len(self.board.moves_done) > 0 and not (self.check_mate or self.stale_mate):
                move = self.board.moves_done.pop()
                move.undo(self.board)
                self.board.current_player.next_player()
                self.board.current_player.moves_done.remove(move)
                self.selected_piece = None
                self.board.calculate_legal_moves()
                self.moves_label.setText('\n'.join(map(str, self.board.moves_done)))
                self.update()

    def choose_promotion(self):
        if self.promotion_move is not None:
            pieces = {"Queen": Queen(self.promotion_move.target, self.selected_piece.alliance),
                      "Knight": Knight(self.promotion_move.target, self.selected_piece.alliance),
                      "Bishop": Bishop(self.promotion_move.target, self.selected_piece.alliance),
                      "Rook": Rook(self.promotion_move.target, self.selected_piece.alliance)}

            piece = pieces[self.sender().objectName()]

            self.promotion_move.promotion_to = piece
            self.board.moves_done.append(self.promotion_move)
            self.board.current_player.moves_done.append(self.promotion_move)
            self.promoting = False
            self.promotion_view.setVisible(False)

            self.promotion_move.execute(self.board)
            self.moves_label.setText('\n'.join(map(str, self.board.moves_done)))
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
        if self.selected_piece.alliance == self.board.current_player.alliance:
            updated_legal_moves = []
            copied_board = copy.deepcopy(self.board)
            for move in self.selected_piece.legal_moves:
                move.execute(copied_board)
                if not copied_board.current_player.is_check(copied_board):
                    updated_legal_moves.append(move)
                move.undo(copied_board)

            if isinstance(self.selected_piece, King):
                for m in self.selected_piece.legal_moves:
                    if isinstance(m, CastleMove) and self.board.current_player.is_check(self.board):
                        updated_legal_moves.remove(m)

            self.selected_piece.legal_moves = updated_legal_moves

    def resizeEvent(self, QResizeEvent):
        self.TILE_SIZE = self.parent().height() // 9
        self.OFFSET = self.TILE_SIZE // 2
        self.moves_label.setGeometry(self.OFFSET * 2 + 8 * self.TILE_SIZE, self.OFFSET,
                                     self.width() - 8 * self.TILE_SIZE - self.OFFSET * 3,
                                     self.height() - 2 * self.OFFSET)
        self.promotion_view.setGeometry(self.OFFSET + self.TILE_SIZE * 2, self.OFFSET + self.TILE_SIZE * 2,
                                        self.TILE_SIZE * 4, self.TILE_SIZE * 4)
        for p in self.promotions:
            p.setIconSize(QSize(self.TILE_SIZE, self.TILE_SIZE))
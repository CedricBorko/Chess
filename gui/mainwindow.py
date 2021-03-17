import copy
import time
from threading import Thread

from PySide6.QtCore import Qt, QRect, QSize, QPoint
from PySide6.QtGui import QPainter, QImage, QFont, QColor, QBrush, QPen, QIcon, QPixmap, QPainterPath
from PySide6.QtWidgets import QMainWindow, QWidget, QGridLayout, QLabel, QHBoxLayout, QGroupBox, QPushButton, \
    QSizePolicy, QScrollArea

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
        self.setStyleSheet("QWidget{background: rgb(48, 48, 48); border: none}"
                           "QLabel{color: white; border: none; padding: 10px}"
                           "QPushButton{border: none; color: white}"
                           "QPushButton:hover{background: #ffcc00; color: black}"
                           "QScrollBar:vertical{background: rgb(83, 83, 83); width: 5px; border: none}"
                           "QScrollBar:add-page:vertical{background: rgb(83, 83, 83)}"
                           "QScrollBar:sub-page:vertical{background: rgb(83, 83, 83)}"
                           "QScrollBar:handle:vertical{background: #ffcc00;}")

        self.main_widget = MainWidget(self)
        self.setMinimumSize(900, 600)
        self.showMaximized()
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

        self.main_layout = QGridLayout(self)
        self.TILE_SIZE = 100
        self.OFFSET = self.TILE_SIZE // 2

        self.selected_piece = None
        self.stale_mate = self.check_mate = False
        self.promotion_move = None
        self.promoting = False
        self.board = Board()
        self.move_index = len(self.board.moves_done)
        self.board_states = []
        self.winner = None

        self.moves_widget = QWidget(self)
        self.moves_widget.setLayout(QGridLayout())
        self.moves_widget.layout().setAlignment(Qt.AlignTop)
        self.moves_widget.layout().setContentsMargins(0, 0, 0, 0)
        white_moves = QLabel("White", self)
        white_moves.setFont(QFont("TW Cen Mt", 16))
        black_moves = QLabel("Black", self)
        black_moves.setFont(QFont("TW Cen Mt", 16))
        self.moves_widget.layout().addWidget(white_moves, 0, 0, 1, 1)
        self.moves_widget.layout().addWidget(black_moves, 0, 1, 1, 1)
        self.move_buttons = []

        self.info_widget = QWidget(self)
        self.info_widget.setLayout(QGridLayout())
        self.info_widget.layout().setContentsMargins(0, 0, 0, 0)
        self.info_widget.layout().addWidget(self.moves_widget, 0, 0, 1, 2)

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

        self.scroll_area = QScrollArea(self.moves_widget)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea{background: rgb(43, 43, 43);"
                                             "border: 1px solid rgba(83, 83, 83, 0.6)}")

        self.scroll_area_widget = QWidget()
        self.scroll_area.setWidget(self.scroll_area_widget)

        self.scroll_area_widget.setLayout(QGridLayout())
        self.scroll_area_widget.layout().setAlignment(Qt.AlignTop)

        self.moves_widget.layout().addWidget(self.scroll_area, 1, 0, 1, 2)

        self.restart_button = QPushButton("Restart", self)
        self.restart_button.hide()
        self.moves_widget.layout().addWidget(self.restart_button, 2, 0, 1, 2)
        self.restart_button.clicked.connect(self.restart)

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
                                      self.TILE_SIZE, self.TILE_SIZE), "12345678"[7 - j])

                if j == 7:
                    qp.setPen(QPen(Qt.black))
                    qp.drawText(QRect(self.OFFSET + i * self.TILE_SIZE,
                                      self.OFFSET + j * self.TILE_SIZE,
                                      self.TILE_SIZE, self.TILE_SIZE), "abcdefgh"[i], Qt.AlignBottom | Qt.AlignLeft)

        if self.selected_piece is not None:
            qp.setPen(QPen(QColor("#ffcc00"), 3, Qt.DashLine))
            qp.setBrush(Qt.NoBrush)
            qp.drawRect(self.OFFSET + self.selected_piece.position % 8 * self.TILE_SIZE,
                        self.OFFSET + self.selected_piece.position // 8 * self.TILE_SIZE, self.TILE_SIZE,
                        self.TILE_SIZE)

        if self.check_mate or self.stale_mate:

            if 0 <= self.move_index < len(self.move_buttons) - 1:
                qp.setPen(QPen(QColor("#ffcc00"), 10, Qt.DotLine))
                pos1 = self.board.moves_done[self.move_index].coming_from
                pos2 = self.board.moves_done[self.move_index].target
                qp.drawLine(self.OFFSET + pos1 % 8 * self.TILE_SIZE + self.TILE_SIZE // 2,
                            self.OFFSET + pos1 // 8 * self.TILE_SIZE + self.TILE_SIZE // 2,
                            self.OFFSET + pos2 % 8 * self.TILE_SIZE + self.TILE_SIZE // 2,
                            self.OFFSET + pos2 // 8 * self.TILE_SIZE + self.TILE_SIZE // 2
                            )
                qp.setBrush(QBrush(QColor("#ffcc00")))
                qp.setPen(Qt.NoPen)
                qp.drawRect(self.OFFSET + pos1 % 8 * self.TILE_SIZE,
                            self.OFFSET + pos1 // 8 * self.TILE_SIZE,
                            self.TILE_SIZE, self.TILE_SIZE)

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

        qp.setPen(QPen(Qt.white))
        qp.setFont(QFont("TW Cen Mt", 16))

        if self.winner is not None:
            if self.check_mate:
                qp.drawText(QRect(self.OFFSET, 0, self.TILE_SIZE * 8, self.OFFSET), Qt.AlignCenter,
                            "Checkmate " + self.winner.__str__() + " wins!")

            if self.stale_mate:
                qp.drawText(QRect(self.OFFSET, 0, self.TILE_SIZE * 8, self.OFFSET), Qt.AlignCenter, "Tie!")

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
                                    if self.selected_piece.alliance == "Black":
                                        p.setStyleSheet("QPushButton{background: white}"
                                                        "QPushButton:hover{background: #ffcc00; color: black}")
                                    else:
                                        p.setStyleSheet("")
                                self.update()
                                self.promotion_view.setVisible(True)
                                self.promoting = True
                                self.promotion_move = move

                            if not self.promoting:

                                if isinstance(self.selected_piece, King):
                                    self.board.current_player.king_first_move = False

                                self.board_states.append(copy.deepcopy(self.board))
                                self.board.moves_done.append(move)
                                self.board.current_player.moves_done.append(move)
                                self.add_move_button(move)
                                move.execute(self.board)

                                self.selected_piece = None
                                self.board.current_player.next_player()
                                in_check = self.board.current_player.is_check(self.board)
                                has_moves = len(self.board.current_player.get_possible_moves()) > 0

                                if self.board.current_player.is_check(self.board):
                                    self.check_mate = in_check and not has_moves
                                else:
                                    self.stale_mate = not in_check and not has_moves

                                if self.check_mate or self.stale_mate:
                                    self.move_index = len(self.move_buttons)
                                    self.winner = self.board.current_player.opponent()
                                    self.selected_piece = self.board.current_player.active_pieces(self.board)[0]
                                    self.board_states.append(copy.deepcopy(self.board))
                                    self.add_move_button()
                                    self.restart_button.show()

                                self.update()
                        else:
                            piece = self.board.get_piece(pos)
                            if not isinstance(piece, EmptyPiece):
                                self.selected_piece = piece
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
            self.board_states.append(copy.deepcopy(self.board))

            self.add_move_button(self.promotion_move)

            self.promoting = False
            self.promotion_view.setVisible(False)
            self.promotion_move.execute(self.board)
            self.selected_piece = None
            self.promotion_move = None
            self.board.current_player.next_player()

            in_check = self.board.current_player.is_check(self.board)
            has_moves = len(self.board.current_player.get_possible_moves()) > 0

            if self.board.current_player.is_check(self.board):
                self.check_mate = in_check and not has_moves
            else:
                self.stale_mate = not in_check and not has_moves

            if self.check_mate or self.stale_mate:
                self.move_index = len(self.move_buttons)
                self.winner = self.board.current_player.opponent()
                self.selected_piece = self.board.current_player.active_pieces(self.board)[0]
                self.board_states.append(copy.deepcopy(self.board))
                self.add_move_button()
                self.restart_button.show()

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
                for move in updated_legal_moves:
                    if isinstance(move, CastleMove) and self.board.current_player.is_check(self.board):
                        updated_legal_moves.remove(move)

            self.selected_piece.legal_moves = updated_legal_moves

    def resizeEvent(self, QResizeEvent):
        self.TILE_SIZE = self.parent().height() // 9
        self.OFFSET = self.TILE_SIZE // 2
        self.info_widget.setGeometry(self.OFFSET * 2 + 8 * self.TILE_SIZE, self.OFFSET,
                                     self.width() - 8 * self.TILE_SIZE - self.OFFSET * 3,
                                     self.TILE_SIZE * 8)

        self.promotion_view.setGeometry(self.OFFSET + self.TILE_SIZE * 2, self.OFFSET + self.TILE_SIZE * 2,
                                        self.TILE_SIZE * 4, self.TILE_SIZE * 4)
        self.restart_button.setMinimumHeight(self.OFFSET)
        for move_label in self.move_buttons:
            move_label.setMaximumHeight(self.OFFSET)
            move_label.setFont(QFont("TW Cen Mt", self.height() // 60))

        for p in self.promotions:
            p.setIconSize(QSize(self.TILE_SIZE, self.TILE_SIZE))

    def add_move_button(self, move=None):
        col = 0 if self.selected_piece.alliance == "White" else 1
        row = len(self.board.current_player.moves_done)
        if move is not None:
            move_button = MoveButton(self, len(self.board.moves_done),
                                     str(len(self.move_buttons) + 1) + ". " + move.__str__())
            move_button.setMaximumHeight(self.OFFSET)
            move_button.setFont(QFont("TW Cen Mt", self.height() // 60))
            self.move_buttons.append(move_button)
            self.scroll_area_widget.layout().addWidget(move_button, row, col, 1, 1)
        else:
            row += 2
            move_button = MoveButton(self, len(self.board.moves_done) + 1, "Checkmate")
            move_button.setMaximumHeight(self.OFFSET)
            move_button.setFont(QFont("TW Cen Mt", self.height() // 60))
            self.move_buttons.append(move_button)
            self.scroll_area_widget.layout().addWidget(move_button, row, 0, 2, 2)

        self.selected_piece = None

    def set_board_state(self):
        if self.stale_mate or self.check_mate:
            index = self.sender().index - 1
            self.board.pieces = self.board_states[index].pieces
            self.move_index = index
            self.update()
            for b in self.move_buttons:
                b.setStyleSheet("QPushButton{border: none; color: white}"
                                "QPushButton:hover{background: #ffcc00; color: black}")
            self.move_buttons[index].setStyleSheet("QPushButton{background: #ffcc00; color: black}")

    def restart(self):
        self.selected_piece = None
        self.stale_mate = self.check_mate = False
        self.promotion_move = None
        self.promoting = False
        self.board = Board()
        self.move_index = len(self.board.moves_done)
        self.board_states = []
        self.winner = None
        for b in self.move_buttons:
            b.setVisible(False)
            del b

        self.move_buttons = []
        self.restart_button.hide()
        self.update()


class MoveButton(QPushButton):
    def __init__(self, parent, index, move):
        super().__init__(parent)
        self.index = index
        self.move = move

        self.setParent(parent)
        self.clicked.connect(self.parent().set_board_state)
        self.setText(self.move)

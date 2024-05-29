import copy
from threading import Thread

from PySide6.QtCore import QPoint, QRect, QSize, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QIcon,
    QKeyEvent,
    QMouseEvent,
    QPainter,
    QPainterPath,
    QPaintEvent,
    QPen,
    QResizeEvent,
)
from PySide6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QGridLayout,
    QGroupBox,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from chess.engine.board import Board, is_valid_position, LETTERS
from chess.engine.move import AttackMove, CastleMove, EnPassantAttackMove, PromotionMove
from chess.engine.board import position_to_coordinate
from chess.engine.pieces.bishop import Bishop
from chess.engine.pieces import King
from chess.engine.pieces.knight import Knight

from chess.engine.pieces import Queen
from chess.engine.pieces.rook import Rook
from gui.io import load_piece_graphics

# COLOR_LIGHT = "#F2F0D8"
# COLOR_DARK = "#758C51"
# COLOR_LIGHT = "#f6dabc"
# COLOR_DARK = "#c0917b"
COLOR_LIGHT = QColor("#eeeed2")
COLOR_DARK = QColor("#769656")
COLOR_HIGHLIGHT = QColor("#f7f783")
COLOR_MOVE = QColor("#2e2d2d")
COLOR_MOVE.setAlpha(190)


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()

        # Init Window
        self.setWindowTitle("Chess")
        self.setStyleSheet(
            """
                QMainWindow{background: #efefef}
                QWidget{background: #22008f9b; border: none}
                QLabel{color: white; border: none; padding: 10px}
                QPushButton{border: none; color: white}
                QPushButton:hover{background: #ffcc00; color: black}
                QScrollBar:vertical{background: rgb(83, 83, 83); width: 5px; border: none}
                QScrollBar:add-page:vertical{background: rgb(83, 83, 83)}
                QScrollBar:sub-page:vertical{background: rgb(83, 83, 83)}
                QScrollBar:handle:vertical{background: #ffcc00;}
            """
        )

        self.board_view = BoardView()
        self.setMinimumSize(1280, 720)
        self.showMaximized()
        self.setCentralWidget(self.board_view)
        self.board_view.setMinimumSize(self.width(), self.height())

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape and self.isFullScreen():
            self.showMaximized()

        if event.key() == Qt.Key.Key_F11 and not self.isFullScreen():
            self.showFullScreen()

    def resizeEvent(self, event: QResizeEvent):
        self.board_view.setMinimumSize(self.width(), self.height())
        self.board_view.resizeEvent(event)


class PromotionDialog(QDialog):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setModal(True)

        self.coordinate_label = QLabel()
        self.setLayout(QVBoxLayout())

        self.options_layout = QGridLayout()
        self.options_group = QButtonGroup()
        self.options_group.setExclusive(True)

        self.queen_option = QPushButton("Queen")
        self.queen_option.setCheckable(True)

        self.rook_option = QPushButton("Rook")
        self.rook_option.setCheckable(True)

        self.bishop_option = QPushButton("Bishop")
        self.bishop_option.setCheckable(True)

        self.knight_option = QPushButton("Knight")
        self.knight_option.setCheckable(True)

        self.confirm_button = QPushButton("Confirm")

        self.options_group.addButton(self.queen_option)
        self.options_group.addButton(self.rook_option)
        self.options_group.addButton(self.bishop_option)
        self.options_group.addButton(self.knight_option)

        self.options_layout.addWidget(self.queen_option, 0, 0)
        self.options_layout.addWidget(self.rook_option, 0, 1)
        self.options_layout.addWidget(self.bishop_option, 1, 0)
        self.options_layout.addWidget(self.knight_option, 1, 1)

        self.layout().setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout().addWidget(self.coordinate_label)
        self.layout().addLayout(self.options_layout)
        self.layout().addWidget(self.confirm_button)

        self.confirm_button.clicked.connect(self.accept)

    def promote(self, coordinate: str) -> None:
        self.queen_option.setChecked(True)
        self.coordinate_label.setText(coordinate.upper())

        self.exec()


class BoardView(QWidget):
    def __init__(self):
        super().__init__()

        self.main_layout = QGridLayout(self)
        self.TILE_SIZE = 80
        self.OFFSET = self.TILE_SIZE // 2
        self.piece_graphics = load_piece_graphics()

        self.selected_piece = None
        self.stale_mate = self.check_mate = False
        self.promotion_move = None
        self.promoting = False
        self.board = Board()

        for piece in self.board.all_active_pieces():
            piece.calculate_legal_moves(self.board)

        self.move_index = self.board.fullmove_number
        self.board_states = []
        self.winner = None

        self.dialog = PromotionDialog()
        self.dialog.accepted.connect(self.on_promote)

        self.moves_widget = QWidget(self)
        self.moves_widget.setLayout(QGridLayout())
        self.moves_widget.layout().setAlignment(Qt.AlignmentFlag.AlignTop)
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

        self.promotions = [
            QPushButton(self),
            QPushButton(self),
            QPushButton(self),
            QPushButton(self),
        ]

        for i, p in enumerate(self.promotions):
            p.clicked.connect(self.choose_promotion)
            p.setObjectName(["Bishop", "Knight", "Queen", "Rook"][i])
            p.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.promotion_view.layout().addWidget(p, i % 2, i // 2)

        self.scroll_area = QScrollArea(self.moves_widget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(
            "QScrollArea{background: rgb(43, 43, 43);"
            "border: 1px solid rgba(83, 83, 83, 0.6)}"
        )

        self.scroll_area_widget = QWidget()
        self.scroll_area.setWidget(self.scroll_area_widget)

        self.scroll_area_widget.setLayout(QGridLayout())
        self.scroll_area_widget.layout().setAlignment(Qt.AlignmentFlag.AlignTop)

        self.moves_widget.layout().addWidget(self.scroll_area, 1, 0, 1, 2)

        self.restart_button = QPushButton("Restart", self)
        self.restart_button.setFont(QFont("TW Cen Mt", 16))
        self.restart_button.hide()
        self.moves_widget.layout().addWidget(self.restart_button, 2, 0, 1, 2)
        self.restart_button.clicked.connect(self.restart)

    def on_promote(self) -> None:
        piece_name = self.dialog.options_group.checkedButton().text()
        if self.promotion_move is None:
            return

        self.promotion_move.piece_to_promote = {
            "Queen": Queen(self.promotion_move.target, self.selected_piece.alliance),
            "Knight": Knight(self.promotion_move.target, self.selected_piece.alliance),
            "Bishop": Bishop(self.promotion_move.target, self.selected_piece.alliance),
            "Rook": Rook(self.promotion_move.target, self.selected_piece.alliance),
        }[piece_name]

        self.promotion_move.execute(self.board)
        self.promotion_move = None

    def draw_tiles(self, painter: QPainter) -> None:
        for i in range(64):
            row, column = divmod(i, 8)

            color = COLOR_DARK if (row + column) % 2 == 1 else COLOR_LIGHT
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor("#2e2d2d"), 3.0))

            painter.drawRect(
                self.OFFSET + column * self.TILE_SIZE,
                self.OFFSET + row * self.TILE_SIZE,
                self.TILE_SIZE,
                self.TILE_SIZE,
            )

    def draw_coordinates(self, painter: QPainter) -> None:
        painter.setFont(QFont("Raleway", 14))
        painter.setPen(QPen(QColor("#ffffff"), 3.0))

        for i in range(8):
            painter.drawText(
                QRect(
                    self.OFFSET + i * self.TILE_SIZE + self.TILE_SIZE // 2 - 12,
                    self.OFFSET // 2,
                    24,
                    24,
                ),
                LETTERS[i].upper(),
                Qt.AlignmentFlag.AlignCenter,
            )

            painter.drawText(
                QRect(
                    self.OFFSET // 2,
                    self.OFFSET + i * self.TILE_SIZE + self.TILE_SIZE // 2 - 12,
                    24,
                    24,
                ),
                str(7 - i + 1),
                Qt.AlignmentFlag.AlignCenter,
            )

    def draw_selected_piece(self, painter: QPainter) -> None:
        if self.selected_piece is None:
            return

        painter.setBrush(QBrush(COLOR_HIGHLIGHT))
        painter.setPen(QPen(QColor("#2e2d2d"), 3.0))

        painter.drawRect(
            self.OFFSET + self.selected_piece.position % 8 * self.TILE_SIZE,
            self.OFFSET + self.selected_piece.position // 8 * self.TILE_SIZE,
            self.TILE_SIZE,
            self.TILE_SIZE,
        )

    def draw_current_move(self, painter: QPainter) -> None:
        if self.move_index not in range(len(self.move_buttons)):
            return

        painter.setPen(QPen(COLOR_HIGHLIGHT, 10))
        selected_move = self.board.moves[self.move_index]

        painter.drawLine(
            self.OFFSET
            + selected_move.origin % 8 * self.TILE_SIZE
            + self.TILE_SIZE // 2,
            self.OFFSET
            + selected_move.origin // 8 * self.TILE_SIZE
            + self.TILE_SIZE // 2,
            self.OFFSET
            + selected_move.target % 8 * self.TILE_SIZE
            + self.TILE_SIZE // 2,
            self.OFFSET
            + selected_move.target // 8 * self.TILE_SIZE
            + self.TILE_SIZE // 2,
        )
        painter.setBrush(QBrush(COLOR_HIGHLIGHT))
        painter.setPen(Qt.PenStyle.NoPen)
        path = self.get_ring_path(selected_move)
        painter.drawPath(path)

    def draw_pieces(self, painter: QPainter) -> None:
        SIZE = self.TILE_SIZE * 3 // 4
        for i in range(64):
            piece = self.board.state[i]
            rect = QRect(
                self.OFFSET + i % 8 * self.TILE_SIZE + (self.TILE_SIZE - SIZE) // 2,
                self.OFFSET + i // 8 * self.TILE_SIZE + (self.TILE_SIZE - SIZE) // 2,
                SIZE,
                SIZE,
            )
            if piece is not None:
                painter.drawImage(rect, self.piece_graphics[piece.abbreviation])

    def draw_legal_moves(self, painter: QPainter) -> None:
        if self.selected_piece.alliance != self.board.active_player:
            return

        for move in self.selected_piece.legal_moves:
            painter.setBrush(QBrush(COLOR_MOVE))
            if self.board.get_piece_at(move.target) is not None:
                path = self.get_ring_path(move)
                painter.drawPath(path)
            else:
                painter.drawText(
                    QRect(
                        self.OFFSET + move.target % 8 * self.TILE_SIZE,
                        self.OFFSET + move.target // 8 * self.TILE_SIZE,
                        self.TILE_SIZE,
                        self.TILE_SIZE,
                    ),
                    str(move.__class__.__name__),
                    Qt.AlignmentFlag.AlignLeft,
                )
                painter.drawEllipse(
                    QPoint(
                        self.OFFSET
                        + self.TILE_SIZE // 2
                        + move.target % 8 * self.TILE_SIZE,
                        self.OFFSET
                        + self.TILE_SIZE // 2
                        + move.target // 8 * self.TILE_SIZE,
                    ),
                    self.TILE_SIZE // 6,
                    self.TILE_SIZE // 6,
                )

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.draw_tiles(painter)
        self.draw_coordinates(painter)
        self.draw_selected_piece(painter)

        if self.check_mate or self.stale_mate:
            self.draw_current_move(painter)

        self.draw_pieces(painter)

        if self.selected_piece is not None:
            self.draw_legal_moves(painter)

        painter.setPen(QPen(Qt.GlobalColor.white))
        painter.setFont(QFont("Raleway", 16))

        if self.winner is not None:
            if self.check_mate:
                painter.drawText(
                    QRect(self.OFFSET, 0, self.TILE_SIZE * 8, self.OFFSET),
                    Qt.AlignmentFlag.AlignCenter,
                    "Checkmate " + self.winner.__str__() + " wins!",
                )

            if self.stale_mate:
                painter.drawText(
                    QRect(self.OFFSET, 0, self.TILE_SIZE * 8, self.OFFSET),
                    Qt.AlignmentFlag.AlignCenter,
                    "Tie!",
                )

    def get_ring_path(self, move):
        path = QPainterPath()
        path.addEllipse(
            QPoint(
                self.OFFSET + self.TILE_SIZE // 2 + move.target % 8 * self.TILE_SIZE,
                self.OFFSET + self.TILE_SIZE // 2 + move.target // 8 * self.TILE_SIZE,
            ),
            self.TILE_SIZE // 2 - 8,
            self.TILE_SIZE // 2 - 8,
        )
        path.addEllipse(
            QPoint(
                self.OFFSET + self.TILE_SIZE // 2 + move.target % 8 * self.TILE_SIZE,
                self.OFFSET + self.TILE_SIZE // 2 + move.target // 8 * self.TILE_SIZE,
            ),
            self.TILE_SIZE // 4 + 8,
            self.TILE_SIZE // 4 + 8,
        )
        return path

    def get_board_position_from_mouse(self, mouse_position: QPoint) -> int:
        x = (-self.OFFSET + mouse_position.x()) // self.TILE_SIZE
        y = (-self.OFFSET + mouse_position.y()) // self.TILE_SIZE
        return y * 8 + x

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() != Qt.MouseButton.LeftButton:
            self.board.undo()
            self.update()
            return super().mousePressEvent(event)

        if self.check_mate or self.stale_mate:
            return super().mousePressEvent(event)

        position = self.get_board_position_from_mouse(event.pos())
        if not is_valid_position(position):
            self.selected_piece = None
            return super().mousePressEvent(event)

        if self.selected_piece is None:
            self.selected_piece = self.board.state[position]

            t = Thread(target=self.update_legal_moves)
            t.start()
            t.join()
            self.update()

        else:
            piece = self.board.get_piece_at(position)
            if piece is not None and piece is not self.selected_piece:
                t = Thread(target=self.update_legal_moves)
                t.start()
                t.join()
                self.update()

            move = self.selected_piece.get_move(position)

            if isinstance(move, PromotionMove):
                self.promotion_move = move
                self.dialog.promote(position_to_coordinate(move.target))
                self.board.moves.append(move)

                self.selected_piece = None
                self.board.next_turn()

                self.update()
                return super().mousePressEvent(event)

            if (
                move is not None
                and self.board.active_player == self.selected_piece.alliance
            ):
                self.board_states.append(copy.deepcopy(self.board))
                self.board.moves.append(move)
                move.execute(self.board)

                self.selected_piece = None
                self.board.next_turn()

                is_checked = self.board.is_checked(self.board.active_player)
                can_move = self.board.active_player_can_move()

                self.check_mate = is_checked and not can_move
                self.stale_mate = not (is_checked or can_move)

                if self.check_mate or self.stale_mate:
                    self.move_index = len(self.move_buttons)
                    self.winner = self.board.active_player.opponent()
                    self.board_states.append(copy.deepcopy(self.board))
                    self.add_move_button()
                    self.restart_button.show()

                self.update()
            else:
                piece = self.board.state[position]
                if piece is not None:
                    self.selected_piece = piece
                    self.update()

    def choose_promotion(self):
        if self.promotion_move is not None:
            pieces = {
                "Queen": Queen(
                    self.promotion_move.target, self.selected_piece.alliance
                ),
                "Knight": Knight(
                    self.promotion_move.target, self.selected_piece.alliance
                ),
                "Bishop": Bishop(
                    self.promotion_move.target, self.selected_piece.alliance
                ),
                "Rook": Rook(self.promotion_move.target, self.selected_piece.alliance),
            }

            piece = pieces[self.sender().objectName()]

            self.promotion_move.piece_to_promote = piece
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
                self.selected_piece = self.board.current_player.active_pieces(
                    self.board
                )[0]
                self.board_states.append(copy.deepcopy(self.board))
                self.add_move_button()
                self.restart_button.show()

            self.update()

    def update_legal_moves(self) -> None:
        if self.selected_piece.alliance != self.board.active_player:
            return
        

        updated_legal_moves = set()
        copied_board = copy.deepcopy(self.board)

        for move in self.selected_piece.legal_moves:
            move.execute(copied_board)
            print(copied_board, copied_board.is_checked(copied_board.active_player.opponent()))
            if not copied_board.is_checked(copied_board.active_player):
                updated_legal_moves.add(move)
            move.undo(copied_board)

        # if isinstance(self.selected_piece, King):
        #     for move in updated_legal_moves:
        #         if isinstance(
        #             move, CastleMove
        #         ) and self.board.active_player.is_check(self.board):
        #             updated_legal_moves.discard(move)

        self.selected_piece.legal_moves = updated_legal_moves

    def resizeEvent(self, event: QResizeEvent):
        self.TILE_SIZE = self.height() // 9
        self.OFFSET = self.TILE_SIZE // 2
        self.info_widget.setGeometry(
            self.OFFSET * 2 + 8 * self.TILE_SIZE,
            self.OFFSET,
            self.width() - 8 * self.TILE_SIZE - self.OFFSET * 3,
            self.TILE_SIZE * 8,
        )

        self.promotion_view.setGeometry(
            self.OFFSET + self.TILE_SIZE * 2,
            self.OFFSET + self.TILE_SIZE * 2,
            self.TILE_SIZE * 4,
            self.TILE_SIZE * 4,
        )
        self.restart_button.setMinimumHeight(self.OFFSET)
        for move_label in self.move_buttons:
            move_label.setMaximumHeight(self.OFFSET)
            move_label.setFont(QFont("TW Cen Mt", self.height() // 60))

        for p in self.promotions:
            p.setIconSize(QSize(self.TILE_SIZE, self.TILE_SIZE))

    def add_move_button(self, move=None):
        return
        col = 0 if self.selected_piece.alliance == "White" else 1
        row = len(self.board.active_player.moves_done)
        if move is not None:
            move_button = MoveButton(
                self,
                len(self.board.moves_done),
                str(len(self.move_buttons) + 1) + ". " + move.__str__(),
            )
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
                b.setStyleSheet(
                    "QPushButton{border: none; color: white}"
                    "QPushButton:hover{background: #ffcc00; color: black}"
                )
            self.move_buttons[index].setStyleSheet(
                "QPushButton{background: #ffcc00; color: black}"
            )

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

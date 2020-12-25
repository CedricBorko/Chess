import typing

from PyQt5.QtCore import QModelIndex, Qt, QAbstractListModel

from pieces.bishop import Bishop
from pieces.king import King
from pieces.knight import Knight
from pieces.pawn import Pawn
from pieces.piece import Alliance
from pieces.queen import Queen
from pieces.rook import Rook


class BoardModel(QAbstractListModel):

    def __init__(self):
        super().__init__()

        self.board = self.standard_board()
        self.white_pieces = self.active_pieces(Alliance.White)
        self.black_pieces = self.active_pieces(Alliance.Black)

        self.white_legal_moves = self.calculate_standard_legal_moves(self.white_pieces)
        self.black_legal_moves = self.calculate_standard_legal_moves(self.black_pieces)

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.board)

    def flags(self, index: QModelIndex):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def data(self, index: QModelIndex, role: int = ...):

        if role == Qt.DisplayRole:
            row = index.row()
            return self.board[row]

        if role == Qt.ToolTipRole:
            row = index.row()
            return self.board[row]

    def setData(self, index: QModelIndex, value: typing.Any, role: int = ...) -> bool:

        row = index.row()

        if value:
            self.board[row] = value
            self.dataChanged(index, index)
            return True

        return False

    def get_piece(self, index):
        return self.board[index]

    def calculate_standard_legal_moves(self, pieces):
        legal_moves = []
        for p in pieces:
            p.calculate_legal_moves(self)
            moves = p.legal_moves
            legal_moves.append(moves)
        return legal_moves

    def active_pieces(self, alliance):
        pieces = set()
        for p in self.board:
            if p is not None:
                if p.alliance == alliance:
                    pieces.add(p)
        return pieces

    @staticmethod
    def standard_board():
        black = [Rook(0, Alliance.Black),
                 Knight(1, Alliance.Black),
                 Bishop(2, Alliance.Black),
                 Queen(3, Alliance.Black),
                 King(4, Alliance.Black),
                 Bishop(5, Alliance.Black),
                 Knight(6, Alliance.Black),
                 Rook(7, Alliance.Black)]
        black_pawns = [Pawn(i, Alliance.Black) for i in range(8, 16)]

        empty = [None for _ in range(32)]

        white_pawns = [Pawn(i, Alliance.White) for i in range(48, 56)]
        white = [Rook(56, Alliance.White),
                 Knight(57, Alliance.White),
                 Bishop(58, Alliance.White),
                 Queen(59, Alliance.White),
                 King(60, Alliance.White),
                 Bishop(61, Alliance.White),
                 Knight(62, Alliance.White),
                 Rook(63, Alliance.White)]
        return black + black_pawns + empty + white_pawns + white


b = BoardModel()
print(b.black_legal_moves)


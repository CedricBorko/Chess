import typing

from PyQt5.QtCore import QModelIndex, Qt, QAbstractListModel

from pieces.bishop import Bishop
from pieces.king import King
from pieces.knight import Knight
from pieces.pawn import Pawn
from pieces.piece import Alliance
from pieces.queen import Queen
from pieces.rook import Rook


class Board(QAbstractListModel):

    def __init__(self):
        super().__init__()

        self.__pieces = self.standard_board()

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.__pieces)

    def flags(self, index: QModelIndex):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def data(self, index: QModelIndex, role: int = ...):

        if role == Qt.DisplayRole:
            row = index.row()
            return self.__pieces[row]

        if role == Qt.ToolTipRole:
            row = index.row()
            return self.__pieces[row]

    def setData(self, index: QModelIndex, value: typing.Any, role: int = ...) -> bool:

        row = index.row()

        if value:
            self.__pieces[row] = value
            self.dataChanged(index, index)
            return True

        return False

    def get_piece(self, index):
        return self.__pieces[index]

    def get_board(self):
        return self.__pieces

    @staticmethod
    def standard_board():
        row_1 = [Rook(0, Alliance.Black), Knight(1, Alliance.Black), Bishop(2, Alliance.Black),
                 Queen(3, Alliance.Black), King(4, Alliance.Black), Bishop(5, Alliance.Black),
                 Knight(6, Alliance.Black), Rook(7, Alliance.Black)]
        row_2 = [Pawn(i, Alliance.Black) for i in range(8, 16)]
        rows_3_to_6 = [None for _ in range(32)]
        row_7 = [Pawn(i, Alliance.White) for i in range(48, 56)]
        row_8 = [Rook(56, Alliance.White), Knight(57, Alliance.White), Bishop(58, Alliance.White),
                 Queen(59, Alliance.White), King(60, Alliance.White), Bishop(61, Alliance.White),
                 Knight(62, Alliance.White), Rook(63, Alliance.White)]
        return row_1 + row_2 + rows_3_to_6 + row_7 + row_8


b = Board()
for piece in b.get_board():
    if piece is not None:
        piece.calculate_legal_moves(b)
        print(piece.position, piece.Name, piece.legal_moves)

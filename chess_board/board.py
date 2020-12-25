import typing
from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt


class Board(QAbstractTableModel):

    def __init__(self, parent, pieces):
        super().__init__(parent)

        self.__pieces = pieces

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.__pieces)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return len(self.__pieces[0])

    def flags(self, index: QModelIndex):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def data(self, index: QModelIndex, role: int = ...):

        if role == Qt.DisplayRole:
            row = index.row()
            column = index.column()
            return self.__pieces[row][column]

        if role == Qt.ToolTipRole:
            row = index.row()
            column = index.column()
            return self.__pieces[row][column].__repr__()

    def setData(self, index: QModelIndex, value: typing.Any, role: int = ...) -> bool:

        row = index.row()
        column = index.column()

        if value:
            self.__pieces[row][column] = value
            self.dataChanged(index, index)
            return True

        return False







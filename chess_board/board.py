import typing

from PyQt5.QtCore import QModelIndex, Qt

from pieces.bishop import Bishop
from pieces.king import King
from pieces.knight import Knight
from pieces.pawn import Pawn
from pieces.piece import Alliance
from pieces.queen import Queen
from pieces.rook import Rook
from player.player import BlackPlayer, WhitePlayer


class Board:

    def __init__(self):
        super().__init__()

        self.board = []
        self.white_pieces = []
        self.black_pieces = []

        self.white_legal_moves = []
        self.black_legal_moves = []

        self.white_player = None
        self.black_player = None

        self.current_player = None

    def get_piece(self, index):
        return self.board[index]

    def set_piece(self, old, new, piece):
        self.board[new] = piece
        self.board[old] = None

    def set_up(self):
        self.board = self.standard_board()
        self.white_pieces = self.active_pieces(Alliance.White)
        self.black_pieces = self.active_pieces(Alliance.Black)

        self.white_legal_moves = self.calculate_standard_legal_moves(self.white_pieces)
        self.black_legal_moves = self.calculate_standard_legal_moves(self.black_pieces)

        self.white_player = WhitePlayer(self, self.white_legal_moves)
        self.black_player = BlackPlayer(self, self.black_legal_moves)

        self.current_player = self.white_player

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

    def is_tile_empty(self, pos):
        return self.board[pos] is None

    def is_valid(self):
        return not self.current_player.is_check(self)

    def update(self):
        for piece in self.board:
            if piece is not None:
                piece.calculate_legal_moves(self)

    def next_player(self):
        if self.current_player == self.white_player:
            self.current_player = self.black_player
        else:
            self.current_player = self.white_player

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
                 King(59, Alliance.White),
                 Queen(60, Alliance.White),
                 Bishop(61, Alliance.White),
                 Knight(62, Alliance.White),
                 Rook(63, Alliance.White)]
        return black + black_pawns + empty + white_pawns + white
        # return black + empty + white

import string
import time

from board_.move import AttackMove, Move, PromotionMove, CastleMove, EnPassantMove, EnPassantAttackMove
from pieces.alliance import get_direction
from pieces.bishop import Bishop
from pieces.king import King
from pieces.knight import Knight
from pieces.pawn import Pawn
from pieces.piece import Alliance, EmptyPiece
from pieces.queen import Queen
from pieces.rook import Rook
from player.player import BlackPlayer, WhitePlayer


class Board:
    def __init__(self):
        super().__init__()

        self.pieces = [EmptyPiece(i) for i in range(64)]
        self.white_player = WhitePlayer(self, Alliance.White)
        self.black_player = BlackPlayer(self, Alliance.Black)

        self.moves_done = []
        self.current_player = self.white_player

        self.create_standard_board()

    def calculate_legal_moves(self):
        for piece in self.current_player.active_pieces(self):
            piece.calculate_legal_moves(self)

    def get_alliance_pieces(self, alliance):
        return [piece for piece in self.pieces if piece.alliance == alliance]

    def get_piece(self, index):
        return self.pieces[index]

    def create_standard_board(self):
        self.pieces = [Rook(0, Alliance.Black, original_rook=True), Knight(1, Alliance.Black),
                       Bishop(2, Alliance.Black), Queen(3, Alliance.Black),
                       King(4, Alliance.Black), Bishop(5, Alliance.Black),
                       Knight(6, Alliance.Black), Rook(7, Alliance.Black, original_rook=True)]

        self.pieces += [Pawn(i, Alliance.Black) for i in range(8, 16)]

        self.pieces += [EmptyPiece(i) for i in range(16, 48)]

        self.pieces += [Pawn(i, Alliance.White) for i in range(48, 56)]

        self.pieces += [Rook(56, Alliance.White, original_rook=True), Knight(57, Alliance.White),
                        Bishop(58, Alliance.White), Queen(59, Alliance.White),
                        King(60, Alliance.White), Bishop(61, Alliance.White),
                        Knight(62, Alliance.White), Rook(63, Alliance.White, original_rook=True)]

        self.calculate_legal_moves()

    def __str__(self):
        output = ' '.join([self.get_piece(i).__str__() for i in range(0, 8)]) + " 8" + "\n"
        output += ' '.join([self.get_piece(i).__str__() for i in range(8, 16)]) + " 7" + "\n"
        output += ' '.join([self.get_piece(i).__str__() for i in range(16, 24)]) + " 6" + "\n"
        output += ' '.join([self.get_piece(i).__str__() for i in range(24, 32)]) + " 5" + "\n"
        output += ' '.join([self.get_piece(i).__str__() for i in range(32, 40)]) + " 4" + "\n"
        output += ' '.join([self.get_piece(i).__str__() for i in range(40, 48)]) + " 3" + "\n"
        output += ' '.join([self.get_piece(i).__str__() for i in range(48, 56)]) + " 2" + "\n"
        output += ' '.join([self.get_piece(i).__str__() for i in range(56, 64)]) + " 1" + "\n"
        output += ' '.join("abcdefgh")
        return output

    def set_piece(self, index, piece):
        self.pieces[index] = piece

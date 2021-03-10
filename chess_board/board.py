import string

from chess_board.move import AttackMove, Move, PromotionMove
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

        self.current_player = self.white_player
        self.setup()
        self.calculate_legal_moves()

    def setup(self):
        self.create_standard_board()
        print(self)

    def calculate_legal_moves(self):
        for i in range(64):
            piece = self.pieces[i]
            if not isinstance(piece, EmptyPiece):
                self.pieces[i].calculate_legal_moves(self)

    def get_alliance_pieces(self, alliance):
        return [piece for piece in self.pieces if piece.alliance == alliance]

    def get_piece(self, index):
        return self.pieces[index]

    def create_standard_board(self):
        """self.pieces = [EmptyPiece(i) for i in range(64)]
        self.set_piece(0, Rook(0, Alliance.Black), EmptyPiece(0))
        self.set_piece(4, King(4, Alliance.Black), EmptyPiece(4))
        self.set_piece(55, Pawn(55, Alliance.Black), EmptyPiece(55))
        self.set_piece(8, Pawn(8, Alliance.White), EmptyPiece(8))
        self.set_piece(60, King(60, Alliance.White), EmptyPiece(60))
        self.set_piece(63, Rook(63, Alliance.White), EmptyPiece(63))"""
        self.pieces = [Rook(0, Alliance.Black), Knight(1, Alliance.Black),
                       Bishop(2, Alliance.Black), Queen(3, Alliance.Black),
                       King(4, Alliance.Black), Bishop(5, Alliance.Black),
                       Knight(6, Alliance.Black), Rook(7, Alliance.Black)]

        self.pieces += [Pawn(i, Alliance.Black) for i in range(8, 16)]

        self.pieces += [EmptyPiece(i) for i in range(16, 48)]

        self.pieces += [Pawn(i, Alliance.White) for i in range(48, 56)]

        self.pieces += [Rook(56, Alliance.White), Knight(57, Alliance.White),
                        Bishop(58, Alliance.White), Queen(59, Alliance.White),
                        King(60, Alliance.White), Bishop(61, Alliance.White),
                        Knight(62, Alliance.White), Rook(63, Alliance.White)]

        self.white_player.king = self.get_piece(60)
        self.black_player.king = self.get_piece(4)

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

    def letter_code(self, letter, number):
        x = string.ascii_lowercase.index(letter)
        y = 8 - number
        return self.get_piece(y * 8 + x)

    def set_piece(self, target, new_piece, old_piece):
        self.pieces[old_piece.position] = EmptyPiece(old_piece.position)
        self.pieces[target] = new_piece

    def undo(self, move):
        destination = move.target
        if isinstance(move, AttackMove):
            moved_piece = move.piece
            other_piece = move.attacked_piece
            self.set_piece(moved_piece.position, moved_piece, EmptyPiece(moved_piece.position))
            self.set_piece(other_piece.position, other_piece, EmptyPiece(other_piece.position))
        elif isinstance(move, Move):
            moved_piece = move.piece
            self.set_piece(moved_piece.position, moved_piece, EmptyPiece(moved_piece.position))
            self.set_piece(destination, EmptyPiece(destination), EmptyPiece(destination))
        elif isinstance(move, PromotionMove):
            if move.other_piece is None:
                self.set_piece(move.pawn.position, move.pawn, EmptyPiece(move.target))
            else:
                self.set_piece(move.pawn.position, move.pawn, EmptyPiece(move.target))
                self.set_piece(move.target, move.other_piece, EmptyPiece(move.target))
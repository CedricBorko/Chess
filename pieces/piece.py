from chess_board.move import CastleMove, PromotionMove, EnPassantAttackMove, EnPassantMove
from chess_board.utils import pos_to_letter_code
from pieces.alliance import Alliance, get_direction


class Piece:
    ABBREVIATION = ""

    def __init__(self, position, alliance):
        self.NAME = self.__class__.__name__
        self.position = position
        self.alliance = alliance

        self.legal_moves = []

    def __repr__(self):
        return "{} {}".format(self.alliance, self.NAME)

    def __str__(self):
        return self.ABBREVIATION if self.alliance == Alliance.White else self.ABBREVIATION.lower()

    def show(self):
        return f"{self.NAME} {self.alliance} {pos_to_letter_code(self.position)}"

    def is_black(self):
        return self.alliance == Alliance.Black

    def is_white(self):
        return self.alliance == Alliance.White

    @property
    def col(self):
        return self.position % 8

    @property
    def row(self):
        return self.position // 8

    def __eq__(self, other):
        return self.position == other.position and self.alliance == other.alliance

    def get_move(self, target):
        for move in self.legal_moves:
            if move.target == target:
                return move

    def make_move(self, board, move):
        from pieces.rook import Rook
        from pieces.king import King
        from pieces.queen import Queen
        from pieces.pawn import Pawn
        if isinstance(move, CastleMove):
            if move.king_side:
                new_king = King(move.target, self.alliance)
                new_rook = Rook(new_king.position - 1, self.alliance)
            else:
                new_king = King(move.target, self.alliance)
                new_rook = Rook(new_king.position + 1, self.alliance)

            board.current_player.king = new_king
            board.set_piece(new_rook.position, new_rook, EmptyPiece(move.target - 1))
            board.set_piece(new_king.position, new_king, EmptyPiece(self.position))
            t = new_king.position + (1 if move.king_side else - 2)
            board.set_piece(t, EmptyPiece(t), EmptyPiece(t))


        elif isinstance(move, PromotionMove):
            if move.promotion_to is None:
                move.promotion_to = Queen(move.target, self.alliance)
            board.set_piece(move.target,
                            move.promotion_to,
                            EmptyPiece(move.pawn.position))
        elif isinstance(move, EnPassantAttackMove):
            board.set_piece(move.target, Pawn(move.target, move.piece.alliance), EmptyPiece(move.piece.position))
            board.set_piece(move.attacked_piece.position,
                            EmptyPiece(move.attacked_piece.position),
                            move.attacked_piece)
        else:
            new_piece = self.__class__(move.target, move.piece.alliance)
            board.set_piece(move.target, new_piece, self)

            if isinstance(new_piece, King):
                board.current_player.king = new_piece


class EmptyPiece(Piece):
    ABBREVIATION = "·"

    def __init__(self, position, alliance=None):
        super().__init__(position, alliance)

    @staticmethod
    def calculate_legal_moves(board):
        return []

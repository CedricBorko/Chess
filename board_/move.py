import copy
from board_.utils import pos_to_letter_code
from pieces.piece import EmptyPiece


class Move:
    def __init__(self, piece, target):
        self.piece = piece
        self.target = target
        self.coming_from = copy.deepcopy(self.piece.position)

    def __str__(self):
        return f"{self.piece.show()} ➜ {pos_to_letter_code(self.target)}"

    def __repr__(self):
        return f"{self.piece.show()} ➜ {pos_to_letter_code(self.target)}"

    def execute(self, board):
        new_piece = self.piece.__class__(self.target, self.piece.alliance)

        board.set_piece(self.target, new_piece)
        board.set_piece(self.coming_from, EmptyPiece())

    def undo(self, board):
        from pieces.piece import EmptyPiece

        new_piece = self.piece.__class__(self.coming_from, self.piece.alliance)

        board.set_piece(self.coming_from, new_piece)
        board.set_piece(self.target, EmptyPiece())


class AttackMove(Move):
    def __init__(self, piece, target, attacked_piece):
        super().__init__(piece, target)
        self.attacked_piece = attacked_piece

    def __repr__(self):
        return f"{self.piece.show()} ➜ {self.attacked_piece.show()}"

    def __str__(self):
        return f"{self.piece.show()} ➜ {self.attacked_piece.show()}"

    def execute(self, board):
        from pieces.piece import EmptyPiece

        new_piece = self.piece.__class__(self.target, self.piece.alliance)

        board.set_piece(self.target, new_piece)
        board.set_piece(self.coming_from, EmptyPiece())

    def undo(self, board):
        moved_piece = self.piece.__class__(self.coming_from, self.piece.alliance)
        attacked_piece = self.attacked_piece.__class__(self.target, self.attacked_piece.alliance)

        board.set_piece(self.coming_from, moved_piece)
        board.set_piece(self.target, attacked_piece)


class CastleMove(Move):
    def __init__(self, piece, target, king_side=True):
        super().__init__(piece, target)
        self.king_side = king_side

    def execute(self, board):
        from pieces.piece import EmptyPiece
        from pieces.rook import Rook
        from pieces.king import King

        new_king = King(self.target, self.piece.alliance)

        if self.king_side:
            new_rook = Rook(self.target - 1, self.piece.alliance)
        else:
            new_rook = Rook(self.target + 1, self.piece.alliance)

        board.set_piece(new_rook.position, new_rook)
        board.set_piece(new_king.position, new_king)
        board.set_piece(self.coming_from, EmptyPiece())
        board.set_piece(self.target + (1 if self.king_side else - 2), EmptyPiece())

    def undo(self, board):
        from pieces.piece import EmptyPiece
        from pieces.rook import Rook

        king = self.piece.__class__(self.coming_from, self.piece.alliance)
        rook = Rook(self.coming_from + (3 if self.king_side else -4), self.piece.alliance, original_rook=True)

        if self.king_side:
            board.set_piece(self.coming_from, king)
            board.set_piece(rook.position, rook)
        else:
            board.set_piece(self.coming_from, king)
            board.set_piece(rook.position, rook)

        board.set_piece(self.target, EmptyPiece())
        board.set_piece(self.target - (1 if self.king_side else -1), EmptyPiece())

        board.current_player.opponent().king_first_move = True


class PromotionMove(Move):
    def __init__(self, piece, target, attacked_piece=None):
        super().__init__(piece, target)
        self.attacked_piece = attacked_piece
        self.promotion_to = None

    def __repr__(self):
        return f"{self.piece.show()} ➜ {self.promotion_to.show()}"

    def __str__(self):
        return f"{self.piece.show()} ➜ {self.promotion_to.show()}"

    def execute(self, board):
        from pieces.piece import EmptyPiece
        from pieces.queen import Queen

        if self.promotion_to is None:
            self.promotion_to = Queen(self.target, self.piece.alliance)

        board.set_piece(self.target, self.promotion_to)
        board.set_piece(self.coming_from, EmptyPiece())

    def undo(self, board):

        if self.attacked_piece is not None:
            attacked_piece = self.attacked_piece.__class__(self.target, self.attacked_piece.alliance)
            board.set_piece(self.target, attacked_piece)
        else:
            board.set_piece(self.target, EmptyPiece())

        moving_piece = self.piece.__class__(self.coming_from, self.piece.alliance)
        board.set_piece(self.coming_from, moving_piece)


class EnPassantMove(Move):
    def __init__(self, piece, target, jumped_position):
        super().__init__(piece, target)
        self.jumped_position = jumped_position

    def __eq__(self, other):
        return self.target == other.target and self.piece == other.piece

    def execute(self, board):
        new_piece = self.piece.__class__(self.target, self.piece.alliance)
        board.set_piece(self.target, new_piece)
        board.set_piece(self.coming_from, EmptyPiece())


class EnPassantAttackMove(Move):
    def __init__(self, piece, target, en_passant_move):
        super().__init__(piece, target)
        self.attacked_piece = en_passant_move.piece
        self.attacked_piece.position = en_passant_move.target
        self.en_passant_move = en_passant_move

    def __repr__(self):
        return f"{self.piece.show()} ➜ {self.attacked_piece.show()}"

    def __str__(self):
        return f"{self.piece.show()} ➜ {self.attacked_piece.show()}"

    def execute(self, board):
        from pieces.piece import EmptyPiece
        from pieces.pawn import Pawn

        board.set_piece(self.target, Pawn(self.target, self.piece.alliance))
        board.set_piece(self.coming_from, EmptyPiece())
        board.set_piece(self.attacked_piece.position, EmptyPiece())

    def undo(self, board):
        from pieces.piece import EmptyPiece

        attacked_piece = self.attacked_piece.__class__(self.attacked_piece.position, self.attacked_piece.alliance)
        attacking_piece = self.piece.__class__(self.coming_from, self.piece.alliance)

        board.set_piece(self.attacked_piece.position, attacked_piece)
        board.set_piece(self.coming_from, attacking_piece)
        board.set_piece(self.target, EmptyPiece())

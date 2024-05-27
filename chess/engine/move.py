from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from chess.engine.board import Board
    from chess.engine.pieces import Piece


class Move:
    def __init__(self, moving_piece: Piece, target: int):
        self.moving_piece = moving_piece

        self.origin = int(moving_piece.position)
        self.target = target

    def __str__(self):
        from chess.engine.board import position_to_coordinate

        return f"{self.moving_piece.show()}, {position_to_coordinate(self.target)}"

    def __repr__(self):
        return f"{self.moving_piece.show()}, {position_to_coordinate(self.target)}"

    def execute(self, board: Board):
        board.set_piece_at(self.target, self.moving_piece)

    def undo(self, board: Board):
        board.set_piece_at(self.origin, self.moving_piece)

    def __eq__(self, other: Move) -> bool:
        return self.moving_piece is other.moving_piece and self.target == other.target

    def __hash__(self):
        return hash((self.origin, self.target))


class AttackMove(Move):
    def __init__(self, moving_piece, target, attacked_piece):
        super().__init__(moving_piece, target)
        self.attacked_piece = attacked_piece

    def __repr__(self):
        return f"{self.moving_piece.show()}, {self.attacked_piece.show()}"

    def __str__(self):
        return f"{self.moving_piece.show()}, {self.attacked_piece.show()}"

    def execute(self, board):
        from chess.engine.pieces.piece import NullPiece

        new_piece = self.moving_piece.__class__(self.target, self.moving_piece.alliance)

        board.set_piece(self.target, new_piece)
        board.set_piece(self.origin, NullPiece())

    def undo(self, board):
        moved_piece = self.moving_piece.__class__(self.origin, self.moving_piece.alliance)
        attacked_piece = self.attacked_piece.__class__(self.target, self.attacked_piece.alliance)

        board.set_piece(self.origin, moved_piece)
        board.set_piece(self.target, attacked_piece)


class CastleMove(Move):
    def __init__(self, moving_piece, target, king_side = True):
        super().__init__(moving_piece, target)
        self.king_side = king_side

    def execute(self, board):
        from chess.engine.pieces.piece import NullPiece
        from chess.engine.pieces.rook import Rook
        from chess.engine.pieces import King

        new_king = King(self.target, self.moving_piece.alliance)

        if self.king_side:
            new_rook = Rook(self.target - 1, self.moving_piece.alliance)
        else:
            new_rook = Rook(self.target + 1, self.moving_piece.alliance)

        board.set_piece_at(new_rook.position, new_rook)
        board.set_piece_at(new_king.position, new_king)
        board.set_piece_at(self.origin, NullPiece())
        board.set_piece_at(self.target + (1 if self.king_side else - 2), NullPiece())

    def undo(self, board):
        from chess.engine.pieces.rook import Rook

        king = self.moving_piece.__class__(self.origin, self.moving_piece.alliance)
        rook = Rook(self.origin + (3 if self.king_side else -4), self.moving_piece.alliance, original_rook=True)

        if self.king_side:
            board.set_piece(self.origin, king)
            board.set_piece(rook.position, rook)
        else:
            board.set_piece(self.origin, king)
            board.set_piece(rook.position, rook)

        board.set_piece(self.target, NullPiece())
        board.set_piece(self.target - (1 if self.king_side else -1), NullPiece())

        board.current_player.opponent().king_first_move = True


class PromotionMove(Move):
    def __init__(self, moving_piece, target, attacked_piece = None):
        super().__init__(moving_piece, target)
        self.attacked_piece = attacked_piece
        self.promotion_to = None

    def __repr__(self):
        return f"{self.moving_piece.show()}, {self.promotion_to.show()}"

    def __str__(self):
        return f"{self.moving_piece.show()}, {self.promotion_to.show()}"

    def execute(self, board):
        from chess.engine.pieces.piece import NullPiece
        from chess.engine.pieces import Queen

        if self.promotion_to is None:
            self.promotion_to = Queen(self.target, self.moving_piece.alliance)

        board.set_piece(self.target, self.promotion_to)
        board.set_piece(self.origin, NullPiece())

    def undo(self, board):
        if self.attacked_piece is not None:
            attacked_piece = self.attacked_piece.__class__(self.target, self.attacked_piece.alliance)
            board.set_piece(self.target, attacked_piece)
        else:
            board.set_piece(self.target, NullPiece())

        moving_piece = self.moving_piece.__class__(self.origin, self.moving_piece.alliance)
        board.set_piece(self.origin, moving_piece)


class PawnJumpMove(Move):
    def __init__(self, moving_piece, target, jumped_position):
        super().__init__(moving_piece, target)
        self.jumped_position = jumped_position

    def execute(self, board: Board) -> None:
        board.set_piece_at(self.target, self.moving_piece)


class EnPassantAttackMove(Move):
    def __init__(self, moving_piece, target, en_passant_move):
        super().__init__(moving_piece, target)
        self.attacked_piece = en_passant_move.moving_piece
        self.attacked_piece.position = en_passant_move.target
        self.en_passant_move = en_passant_move

    def __repr__(self):
        return f"{self.moving_piece.show()}, {self.attacked_piece.show()}"

    def __str__(self):
        return f"{self.moving_piece.show()}, {self.attacked_piece.show()}"

    def execute(self, board):
        from chess.engine.pieces.piece import NullPiece
        from chess.engine.pieces.pawn import Pawn

        board.set_piece(self.target, Pawn(self.target, self.moving_piece.alliance))
        board.set_piece(self.origin, NullPiece())
        board.set_piece(self.attacked_piece.position, NullPiece())

    def undo(self, board):
        from chess.engine.pieces.piece import NullPiece

        attacked_piece = self.attacked_piece.__class__(self.attacked_piece.position, self.attacked_piece.alliance)
        attacking_piece = self.moving_piece.__class__(self.origin, self.moving_piece.alliance)

        board.set_piece(self.attacked_piece.position, attacked_piece)
        board.set_piece(self.origin, attacking_piece)
        board.set_piece(self.target, NullPiece())

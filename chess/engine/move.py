from __future__ import annotations

from typing import TYPE_CHECKING

from chess.engine.alliance import Alliance

if TYPE_CHECKING:
    from chess.engine.board import Board
    from chess.engine.pieces import Piece


class Move:
    def __init__(self, moving_piece: Piece, target: int):
        self.moving_piece = moving_piece

        self.origin = moving_piece.position
        self.target = target

    def __str__(self):
        return f"M: {self.moving_piece.abbreviation} -> {self.target}"

    def __repr__(self):
        return f"M: {self.moving_piece.abbreviation} -> {self.target}"

    def execute(self, board: Board):
        board.set_piece_at(self.target, self.moving_piece)
        board.set_piece_at(self.origin, None)

        self.moving_piece.move_count += 1

    def undo(self, board: Board):
        board.set_piece_at(self.origin, self.moving_piece)
        board.set_piece_at(self.target, None)

        self.moving_piece.move_count -= 1

    def __eq__(self, other: Move) -> bool:
        return self.moving_piece is other.moving_piece and self.target == other.target

    def __hash__(self):
        return hash((self.origin, self.target))


class AttackMove(Move):
    def __init__(self, moving_piece: Piece, target: int, attacked_piece: Piece):
        super().__init__(moving_piece, target)

        self.attacked_piece = attacked_piece

    def __str__(self):
        return f"A: {self.moving_piece.abbreviation} -> {self.target}"

    def __repr__(self):
        return f"A: {self.moving_piece.abbreviation} -> {self.target}"

    def execute(self, board: Board):
        board.set_piece_at(self.target, self.moving_piece)
        board.set_piece_at(self.origin, None)

        self.moving_piece.move_count += 1

    def undo(self, board: Board):
        board.set_piece_at(self.origin, self.moving_piece)
        board.set_piece_at(self.target, self.attacked_piece)

        self.moving_piece.move_count -= 1


class CastleMove(Move):
    def __init__(self, moving_piece: Piece, target: int, is_king_side = True):
        super().__init__(moving_piece, target)

        self.is_king_side = is_king_side

    def execute(self, board: Board):
        if self.is_king_side:
            rook = board.get_piece_at(self.origin + 3)
            board.set_piece_at(self.target - 1, rook)
            board.set_piece_at(self.target + 1, None)
            abbreviation = self.moving_piece.abbreviation
        else:
            rook = board.get_piece_at(self.origin - 4)
            board.set_piece_at(self.target + 1, rook)
            board.set_piece_at(self.target - 2, None)
            abbreviation = "Q" if self.moving_piece.alliance == Alliance.WHITE else "q"

        board.set_piece_at(self.target, self.moving_piece)
        board.set_piece_at(self.origin, None)

        self.moving_piece.move_count += 1
        rook.move_count += 1

        board.castling_availability = board.castling_availability.replace(abbreviation, '')

    def undo(self, board: Board):
        king = board.get_piece_at(self.target)
        board.set_piece_at(self.origin, king)
        board.set_piece_at(self.target, None)

        if self.is_king_side:
            rook = board.get_piece_at(self.target - 1)
            board.set_piece_at(self.target + 1, rook)
            board.set_piece_at(self.target - 1, None)
            abbreviation = self.moving_piece.abbreviation
        else:
            rook = board.get_piece_at(self.target + 1)
            board.set_piece_at(self.target - 2, rook)
            board.set_piece_at(self.target + 1, None)
            abbreviation = "Q" if self.moving_piece.alliance == Alliance.WHITE else "q"

        king.move_count -= 1
        rook.move_count -= 1

        board.castling_availability += abbreviation
        board.castling_availability = ''.join(sorted(board.castling_availability))


class PromotionMove(Move):
    def __init__(self, moving_piece: Piece, target: int, attacked_piece: Piece | None = None):
        super().__init__(moving_piece, target)

        self.attacked_piece = attacked_piece
        self.piece_to_promote = None

    def __repr__(self):
        return f"{self.moving_piece.show()}, {self.piece_to_promote.show()}"

    def __str__(self):
        return f"{self.moving_piece.show()}, {self.piece_to_promote.show()}"

    def execute(self, board):
        from chess.engine.pieces import Queen

        if self.piece_to_promote is None:
            self.piece_to_promote = Queen(self.target, self.moving_piece.alliance)

        self.piece_to_promote.move_count = 1
        self.moving_piece.move_count += 1

        board.set_piece_at(self.target, self.piece_to_promote)
        board.set_piece_at(self.origin, None)

        if self.moving_piece.alliance == Alliance.WHITE:
            board.white_pieces.add(self.piece_to_promote)
        else:
            board.black_pieces.add(self.piece_to_promote)

    def undo(self, board):
        if self.attacked_piece is not None:
            board.set_piece_at(self.target, self.attacked_piece)
        else:
            board.set_piece_at(self.target, None)

        self.moving_piece.move_count -= 1

        board.set_piece_at(self.origin, self.moving_piece)

        if self.moving_piece.alliance == Alliance.WHITE:
            board.white_pieces.discard(self.piece_to_promote)
        else:
            board.black_pieces.discard(self.piece_to_promote)


class PawnJumpMove(Move):
    def __init__(self, moving_piece: Piece, target: int, jumped_position: int):
        super().__init__(moving_piece, target)

        self.jumped_position = jumped_position

    def execute(self, board: Board) -> None:
        board.set_piece_at(self.target, self.moving_piece)
        board.set_piece_at(self.origin, None)

        self.moving_piece.move_count += 1

    def undo(self, board: Board) -> None:
        board.set_piece_at(self.origin, self.moving_piece)
        board.set_piece_at(self.target, None)

        self.moving_piece.move_count -= 1


class EnPassantAttackMove(Move):
    def __init__(self, moving_piece: Piece, target: int, en_passant_move: PawnJumpMove):
        super().__init__(moving_piece, target)

        self.attacked_piece = en_passant_move.moving_piece
        self.attacking_piece_at = int(self.attacked_piece.position)

    def __repr__(self):
        return f"{self.moving_piece.show()}, {self.attacked_piece.show()}"

    def __str__(self):
        return f"{self.moving_piece.show()}, {self.attacked_piece.show()}"

    def execute(self, board):
        board.set_piece_at(self.target, self.moving_piece)
        board.set_piece_at(self.origin, None)
        board.set_piece_at(self.attacked_piece.position, None)

        self.moving_piece.move_count += 1

    def undo(self, board):
        board.set_piece_at(self.attacking_piece_at, self.attacked_piece)
        board.set_piece_at(self.origin, self.moving_piece)
        board.set_piece_at(self.target, None)

        self.moving_piece.move_count -= 1

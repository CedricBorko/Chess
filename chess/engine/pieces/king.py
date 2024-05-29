from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from chess.engine.board import Board

from chess.engine.move import AttackMove, Move, CastleMove
from chess.engine.alliance import Alliance
from chess.engine.pieces.piece import Piece
from chess.engine.pieces.rook import Rook

KING_SIDE_CASTLE = 1
QUEEN_SIDE_CASTLE = -1


class King(Piece):
    OFFSETS: set[int] = {-9, -8, -7, -1, 1, 7, 8, 9}

    def __init__(self, position: int, alliance: Alliance):
        super().__init__(position, alliance)

    def calculate_legal_moves(self, board: Board) -> set[Move]:
        from chess.engine.board import is_valid_position

        self.legal_moves.clear()

        for offset in self.OFFSETS:
            possible_target = self.position + offset

            if is_valid_position(possible_target):
                self.check_standard_moves(board, possible_target, offset)

                if not any((castle_availability := self.can_castle(board))):
                    continue

                if (
                    offset == KING_SIDE_CASTLE
                    and castle_availability[0]
                    and self.tiles_for_castling_are_save_and_clear(
                        board, is_king_side=True
                    )
                ):

                    possible_rook = board.get_piece_at(possible_target + 2)
                    if (
                        isinstance(possible_rook, Rook)
                        and not possible_rook.has_moved
                        and possible_rook.alliance == self.alliance
                    ):
                        self.legal_moves.add(
                            CastleMove(
                                self, possible_rook.position - 1, is_king_side=True
                            )
                        )

                elif (
                    offset == QUEEN_SIDE_CASTLE
                    and castle_availability[1]
                    and self.tiles_for_castling_are_save_and_clear(
                        board, is_king_side=False
                    )
                ):
                    possible_rook = board.get_piece_at(possible_target - 3)
                    if (
                        isinstance(possible_rook, Rook)
                        and not possible_rook.has_moved
                        and possible_rook.alliance == self.alliance
                    ):
                        self.legal_moves.add(
                            CastleMove(
                                self, possible_rook.position + 2, is_king_side=False
                            )
                        )

        return self.legal_moves

    def check_standard_moves(self, board: Board, target: int, offset: int) -> None:
        if self.is_first_column_exclusion(offset) or self.is_eighth_column_exclusion(
            offset
        ):
            return

        piece_on_tile = board.state[target]
        if piece_on_tile is None:
            self.legal_moves.add(Move(self, target))
            return

        if piece_on_tile.alliance != self.alliance:
            self.legal_moves.add(AttackMove(self, target, piece_on_tile))

    def is_first_column_exclusion(self, offset: int) -> bool:
        return self.position % 8 == 0 and offset in (-9, -1, 7)

    def is_eighth_column_exclusion(self, offset: int) -> bool:
        return self.position % 8 == 7 and offset in (-7, 1, 9)

    def tiles_for_castling_are_save_and_clear(self, board: Board, is_king_side: bool):
        from chess.engine.board import is_valid_position

        offsets = {1, 2} if is_king_side else {-1, -2, -3}

        path_is_clear = all(
            (
                is_valid_position(self.position + offset)
                and board.get_piece_at(self.position + offset) is None
                for offset in offsets
            )
        )

        if not path_is_clear:
            return False

        for piece in board.get_available_pieces(board.active_player.opponent()):
            for move in piece.legal_moves:
                if move.target in [self.position + offset for offset in offsets]:
                    return False

        return True

    def can_castle(self, board: Board) -> tuple[bool, bool]:
        if self.alliance == Alliance.WHITE:
            return (
                "K" in board.castling_availability and not self.has_moved,
                "Q" in board.castling_availability and not self.has_moved,
            )

        return (
            "k" in board.castling_availability and not self.has_moved,
            "q" in board.castling_availability and not self.has_moved,
        )

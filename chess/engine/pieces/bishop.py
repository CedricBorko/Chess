from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from chess.engine.board import Board
    from chess.engine.alliance import Alliance

from chess.engine.move import Move, AttackMove
from chess.engine.pieces.piece import Piece


class Bishop(Piece):
    OFFSETS: set[int] = {-9, -7, 7, 9}

    def __init__(self, position: int, alliance: Alliance):
        super().__init__(position, alliance)

    def calculate_legal_moves(self, board: Board) -> set[Move]:
        from chess.engine.board import is_valid_position

        self.legal_moves.clear()

        for offset in self.OFFSETS:
            possible_target = self.position

            while is_valid_position(possible_target):
                if is_restricted_move(possible_target, offset):
                    break

                possible_target += offset

                if is_valid_position(possible_target):
                    piece_on_tile = board.get_piece_at(possible_target)

                    if piece_on_tile is None:
                        self.legal_moves.add(Move(self, possible_target))
                    else:
                        if piece_on_tile.alliance != self.alliance:
                            self.legal_moves.add(
                                AttackMove(self, possible_target, piece_on_tile)
                            )
                        break

        return self.legal_moves


def is_first_column_exclusion(position: int, offset: int) -> bool:
    return position % 8 == 0 and offset in (-9, 7)


def is_eighth_column_exclusion(position: int, offset: int) -> bool:
    return position % 8 == 7 and offset in (-7, 9)


def is_restricted_move(position: int, offset: int) -> bool:
    return is_first_column_exclusion(position, offset) or is_eighth_column_exclusion(
        position, offset
    )

from __future__ import annotations
from typing import TYPE_CHECKING

from chess.engine.alliance import Alliance

if TYPE_CHECKING:
    from chess.engine.board import Board

from chess.engine.move import AttackMove, Move
from chess.engine.pieces.piece import Piece


class Rook(Piece):
    OFFSETS: set[int] = {-8, -1, 1, 8}

    def __init__(self, position: int, alliance: Alliance):
        super().__init__(position, alliance)

    def calculate_legal_moves(self, board: Board) -> set[Move]:
        from chess.engine.board import is_valid_position

        self.legal_moves.clear()

        for offset in self.OFFSETS:
            possible_target = self.position

            while is_valid_position(possible_target):
                if (
                    is_first_column_exclusion(possible_target, offset) or
                    is_eighth_column_exclusion(possible_target, offset)
                ):
                    break

                possible_target += offset

                if not is_valid_position(possible_target):
                    break

                piece_on_tile = board.state[possible_target]
                if piece_on_tile is None:
                    self.legal_moves.add(Move(self, possible_target))
                else:
                    if piece_on_tile.alliance != self.alliance:
                        self.legal_moves.add(AttackMove(self, possible_target, piece_on_tile))
                    break

        return self.legal_moves


def is_first_column_exclusion(position: int, offset: int) -> bool:
    return position % 8 == 0 and offset == -1


def is_eighth_column_exclusion(position: int, offset: int) -> bool:
    return position % 8 == 7 and offset == 1

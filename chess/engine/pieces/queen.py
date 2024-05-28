from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from chess.engine.board import Board

from chess.engine.move import AttackMove, Move
from chess.engine.alliance import Alliance
from chess.engine.pieces.piece import Piece


class Queen(Piece):

    OFFSETS: set[int] = {-9, -8, -7, -1, 1, 7, 8, 9}

    def __init__(self, position: int, alliance: Alliance) -> None:
        super().__init__(position, alliance)

    def calculate_legal_moves(self, board: Board):
        from chess.engine.board import is_valid_position

        self.legal_moves.clear()

        for offset in self.OFFSETS:
            possible_target = self.position
            while is_valid_position(possible_target):
                if is_restricted_move(possible_target, offset):
                    break

                possible_target += offset

                if not is_valid_position(possible_target):
                    break

                piece_on_tile = board.state[possible_target]
                if piece_on_tile is None:
                    self.legal_moves.add(Move(self, possible_target))
                    continue

                else:
                    if piece_on_tile.alliance != self.alliance:
                        self.legal_moves.add(
                            AttackMove(self, possible_target, piece_on_tile)
                        )
                        break


def is_first_column_exclusion(position: int, offset: int) -> bool:
    return position % 8 == 0 and offset in (-9, -1, 7)


def is_eighth_column_exclusion(position: int, offset: int) -> bool:
    return position % 8 == 7 and offset in (-7, 1, 9)


def is_restricted_move(positon: int, offset: int) -> bool:
    return is_first_column_exclusion(positon, offset) or is_eighth_column_exclusion(
        positon, offset
    )

from __future__ import annotations
from typing import TYPE_CHECKING

from chess.engine.alliance import Alliance

if TYPE_CHECKING:
    from chess.engine.board import Board
from chess.engine.move import Move, AttackMove, PromotionMove, PawnJumpMove, EnPassantAttackMove
from chess.engine.pieces.piece import Piece

SINGLE_MOVE = 8
DOUBLE_MOVE = 16


class Pawn(Piece):
    OFFSETS: set[int] = {7, 8, 9, 16}

    def __init__(self, position, alliance):
        super().__init__(position, alliance)

        self.first_move = True

    def calculate_legal_moves(self, board: Board) -> set[Move]:
        from chess.engine.board import is_valid_position

        self.legal_moves.clear()

        for offset in self.OFFSETS:
            possible_target = self.position + (offset * self.alliance.get_direction())

            if is_valid_position(possible_target):
                piece_on_tile = board.get_piece_at(possible_target)

                if offset == SINGLE_MOVE and piece_on_tile is None:
                    if self.position // 8 == 1 and self.alliance == Alliance.WHITE:
                        self.legal_moves.add(PromotionMove(self, possible_target))

                    elif self.position // 8 == 6 and self.alliance == Alliance.BLACK:  # Promotion Black Pawn
                        self.legal_moves.add(PromotionMove(self, possible_target))

                    else:
                        self.legal_moves.add(Move(self, possible_target))

                # Pawn jump move
                elif (
                    offset == DOUBLE_MOVE and
                    self.is_eligible_for_jump_move()
                ):
                    position_in_between = self.position + (8 * self.alliance.get_direction())
                    if (
                        board.get_piece_at(position_in_between) is None
                        and piece_on_tile is None
                    ):
                        self.legal_moves.add(PawnJumpMove(self, possible_target, position_in_between))

                # Attack and en passant moves
                elif offset in (7, 9):
                    if offset == 7 and (self.position % 8 == 7 and self.is_white() or
                                        self.position % 8 == 0 and self.is_black()):
                        continue

                    if offset == 9 and (self.position % 8 == 0 and self.is_white() or
                                        self.position % 8 == 7 and self.is_black()):
                        continue

                    piece = board.state[possible_target]
                    last_move = board.get_last_move()

                    if (
                        isinstance(last_move, PawnJumpMove) and
                        last_move.jumped_position == possible_target and
                        last_move.moving_piece.alliance != self.alliance
                    ):
                        self.legal_moves.add(EnPassantAttackMove(self, possible_target, last_move))

                    else:
                        if piece is not None and self.alliance != piece.alliance:
                            if self.position // 8 == 1 and self.is_white():
                                self.legal_moves.add(PromotionMove(self, possible_target, piece))
                            elif self.position // 8 == 6 and self.is_black():
                                self.legal_moves.add(PromotionMove(self, possible_target, piece))
                            else:
                                self.legal_moves.add(AttackMove(self, possible_target, piece))

        return self.legal_moves

    def is_eligible_for_jump_move(self) -> bool:
        return (
            not self.has_moved and
            (
                self.is_black() and self.position // 8 == 1 or
                self.is_white() and self.position // 8 == 6
            )
        )

from chess.engine.move import AttackMove, Move
from chess.engine.alliance import Alliance
from chess.engine.pieces.piece import Piece


class Knight(Piece):
    OFFSETS: set[int] = {-17, -15, -10, -6, 6, 10, 15, 17}

    def __init__(self, position: int, alliance: Alliance):
        super().__init__(position, alliance)

        self.abbreviation = "n" if self.alliance == Alliance.BLACK else "N"

    def calculate_legal_moves(self, board):
        from chess.engine.board import is_valid_position

        self.legal_moves.clear()

        for offset in self.OFFSETS:
            possible_target = self.position + offset

            if not is_valid_position(possible_target) or self.is_restricted_move(offset):
                continue

            piece_on_tile = board.state[possible_target]
            if piece_on_tile is None:
                self.legal_moves.add(Move(self, possible_target))
                continue

            if piece_on_tile.alliance != self.alliance:
                self.legal_moves.add(AttackMove(self, possible_target, piece_on_tile))

    def is_first_column_exclusion(self, offset: int) -> bool:
        return self.position % 8 == 0 and offset in (-17, -10, 6, 15)

    def is_second_column_exclusion(self, offset: int) -> bool:
        return self.position % 8 == 1 and offset in (-10, 6)

    def is_seventh_column_exclusion(self, offset: int) -> bool:
        return self.position % 8 == 6 and offset in (-6, 10)

    def is_eighth_column_exclusion(self, offset: int) -> bool:
        return self.position % 8 == 7 and offset in (-15, -6, 10, 17)

    def is_restricted_move(self, offset: int) -> bool:
        return any(
            (
                self.is_first_column_exclusion(offset),
                self.is_second_column_exclusion(offset),
                self.is_seventh_column_exclusion(offset),
                self.is_eighth_column_exclusion(offset)
            )
        )

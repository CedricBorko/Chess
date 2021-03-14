from board_.utils import valid_target, on_col
from board_.move import AttackMove, Move
from pieces.piece import Piece, EmptyPiece


class Queen(Piece):
    ABBREVIATION = "Q"

    def __init__(self, position, alliance):
        super().__init__(position, alliance)

    def calculate_legal_moves(self, board):
        self.legal_moves = []
        offsets = {-9, -8, -7, -1, 1, 7, 8, 9}

        for offset in offsets:

            possible_target = self.position
            while valid_target(possible_target):
                if self.first_column_exclusion(possible_target, offset) \
                    or self.eighth_column_exclusion(possible_target, offset):
                    break

                possible_target += offset

                if valid_target(possible_target):

                    piece_on_tile = board.get_piece(possible_target)
                    if isinstance(piece_on_tile, EmptyPiece):
                        self.legal_moves.append(Move(self, possible_target))

                    else:
                        if piece_on_tile.alliance != self.alliance:
                            self.legal_moves.append(AttackMove(self, possible_target, piece_on_tile))
                        break

    @staticmethod
    def first_column_exclusion(current_pos, offset):
        return on_col(0, current_pos) and offset in (-9, -1, 7)

    @staticmethod
    def eighth_column_exclusion(current_pos, offset):
        return on_col(7, current_pos) and offset in (-7, 1, 9)

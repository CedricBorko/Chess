from board_.utils import valid_target, on_col
from board_.move import AttackMove, Move
from pieces.piece import Piece, EmptyPiece


class Knight(Piece):
    ABBREVIATION = "N"

    def __init__(self, position, alliance):
        super().__init__(position, alliance)

    def calculate_legal_moves(self, board):
        self.legal_moves = []
        offsets = {-17, -15, -10, -6, 6, 10, 15, 17}

        for offset in offsets:

            possible_target = self.position + offset

            if valid_target(possible_target):
                if not self.first_column_exclusion(offset) and not self.second_column_exclusion(offset) \
                    and not self.seventh_column_exclusion(offset) and not self.eighth_column_exclusion(offset):

                    piece_on_tile = board.get_piece(possible_target)
                    if isinstance(piece_on_tile, EmptyPiece):
                        self.legal_moves.append(Move(self, possible_target, ))

                    else:
                        if piece_on_tile.alliance != self.alliance:
                            self.legal_moves.append(AttackMove(self, possible_target, piece_on_tile))

    def first_column_exclusion(self, offset):
        """Returns if the Knight is on column 1 and going left"""
        return on_col(0, self.position) and offset in (-17, -10, 6, 15)

    def second_column_exclusion(self, offset):
        """Returns if the Knight is on column 2 and going left"""
        return on_col(1, self.position) and offset in (-10, 6)

    def seventh_column_exclusion(self, offset):
        """Returns if the Knight is on column 7 and going right"""
        return on_col(6, self.position) and offset in (-6, 10)

    def eighth_column_exclusion(self, offset):
        """Returns if the Knight is on column 8 and going right"""
        return on_col(7, self.position) and offset in (-15, -6, 10, 17)

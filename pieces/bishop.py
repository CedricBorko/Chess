from board_.move import Move, AttackMove
from board_.utils import valid_target, on_col
from pieces.piece import Piece, EmptyPiece


class Bishop(Piece):
    ABBREVIATION = "B"

    def __init__(self, position, alliance):
        super().__init__(position, alliance)

    def calculate_legal_moves(self, board):
        self.legal_moves = []
        offsets = {-9, -7, 7, 9}  # A Bishop has 4 possible directions to move in

        for offset in offsets:

            possible_target = self.position
            while valid_target(possible_target):

                if self.first_column_exclusion(possible_target, offset) \
                    or self.eighth_column_exclusion(possible_target, offset):
                    # The bishop can neither go left if on column 1 nor go right on column 8
                    break

                possible_target += offset

                if valid_target(possible_target):

                    piece_on_tile = board.get_piece(possible_target)
                    if isinstance(piece_on_tile, EmptyPiece):
                        # Create a standard move
                        self.legal_moves.append(Move(self, possible_target))

                    else:
                        # Create an attack move with the piece on target tile as attacked piece
                        if piece_on_tile.alliance != self.alliance:
                            self.legal_moves.append(AttackMove(self, possible_target, piece_on_tile))
                        break

    @staticmethod
    def first_column_exclusion(current_pos, offset):
        """Returns if the Bishop is on column 1 and going left"""
        return on_col(0, current_pos) and offset in (-9, 7)

    @staticmethod
    def eighth_column_exclusion(current_pos, offset):
        """Returns if the Bishop is on column 8 and going right"""
        return on_col(7, current_pos) and offset in (-7, 9)

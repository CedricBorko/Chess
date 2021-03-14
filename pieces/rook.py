from board_.utils import valid_target, on_col
from board_.move import AttackMove, Move
from pieces.piece import Piece, EmptyPiece


class Rook(Piece):
    ABBREVIATION = "R"

    def __init__(self, position, alliance, original_rook=False):
        super().__init__(position, alliance)

        self.first_move = True
        self.original_rook = original_rook

    def calculate_legal_moves(self, board):
        self.legal_moves = []
        offsets = {-8, -1, 1, 8}

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
        return on_col(0, current_pos) and offset == -1

    @staticmethod
    def eighth_column_exclusion(current_pos, offset):
        return on_col(7, current_pos) and offset == 1

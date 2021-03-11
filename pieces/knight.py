from board_.utils import valid_target
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
                if not self.first_column(offset) and not self.second_column(offset) \
                    and not self.seventh_column(offset) and not self.eighth_column(offset):

                    piece_on_tile = board.get_piece(possible_target)
                    if isinstance(piece_on_tile, EmptyPiece):
                        self.legal_moves.append(Move(board, self, possible_target, ))

                    else:
                        if piece_on_tile.alliance != self.alliance:
                            self.legal_moves.append(AttackMove(board, self, possible_target, piece_on_tile))

    def first_column(self, offset):
        return self.position % 8 == 0 and offset in (-17, -10, 6, 15)

    def second_column(self, offset):
        return self.position % 8 == 1 and offset in (-10, 6)

    def seventh_column(self, offset):
        return self.position % 8 == 6 and offset in (-6, 10)

    def eighth_column(self, offset):
        return self.position % 8 == 7 and offset in (-15, -6, 10, 17)

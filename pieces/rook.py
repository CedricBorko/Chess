from chess_board.board_utils import valid_target
from chess_board.move import AttackMove, Move
from pieces.piece import Piece


class Rook(Piece):
    Name = "Rook"

    def __init__(self, position, alliance):
        super().__init__(position, alliance)

    def calculate_legal_moves(self, board):
        offsets = {-8, -1, 1, 8}

        for offset in offsets:

            possible_target = self.position
            while valid_target(possible_target):

                possible_target += offset

                if valid_target(possible_target):
                    if not self.first_column(offset) and not self.eighth_column(offset):

                        piece_on_tile = board.get_piece(possible_target)
                        if piece_on_tile is None:
                            self.legal_moves.add(Move(board, self, possible_target))

                        else:
                            if piece_on_tile.alliance != self.alliance:
                                self.legal_moves.add(AttackMove(board, self, possible_target, piece_on_tile))
                            else:
                                break

    def first_column(self, offset):
        return self.position % 8 == 0 and offset == -1

    def eighth_column(self, offset):
        return self.position % 8 == 7 and offset == 1

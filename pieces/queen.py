from chess_board.utils import valid_target
from chess_board.move import AttackMove, Move
from pieces.piece import Piece


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
                if self.first_column(possible_target, offset) or self.eighth_column(possible_target, offset):
                    break

                possible_target += offset

                if valid_target(possible_target):

                    piece_on_tile = board.get_piece(possible_target)
                    if piece_on_tile is None:
                        self.legal_moves.append(Move(board, self, possible_target))

                    else:
                        if piece_on_tile.alliance != self.alliance:
                            self.legal_moves.append(AttackMove(board, self, possible_target, piece_on_tile))
                        else:
                            break

    @staticmethod
    def make_move(move):
        return Queen(move.destination, move.moving_piece.alliance)

    @staticmethod
    def first_column(current_pos, offset):
        return current_pos % 8 == 0 and offset in (-9, -1, 7)

    @staticmethod
    def eighth_column(current_pos, offset):
        return current_pos % 8 == 7 and offset in (-7, 1, 9)

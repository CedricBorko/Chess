from chess_board.utils import valid_target, on_row
from chess_board.move import Move, AttackMove
from pieces.alliance import get_direction
from pieces.piece import Piece, EmptyPiece


class Pawn(Piece):
    ABBREVIATION = "P"

    def __init__(self, position, alliance):
        super().__init__(position, alliance)

        self.first_move = True

    def calculate_legal_moves(self, board):
        self.legal_moves = []
        offsets = {7, 8, 9, 16}

        for offset in offsets:

            possible_target = self.position + (offset * get_direction(self.alliance))
            if valid_target(possible_target):

                piece_on_tile = board.get_piece(possible_target)

                if offset == 8 and isinstance(piece_on_tile, EmptyPiece):
                    self.legal_moves.append(Move(board, self, possible_target))
                    # TODO promotion
                elif offset == 16 and self.first_move and (self.is_black() and on_row(1, self.position) or
                                                           self.is_white() and on_row(6, self.position)):

                    position_in_between = self.position + (8 * get_direction(self.alliance))
                    if isinstance(board.get_piece(position_in_between), EmptyPiece) \
                        and isinstance(piece_on_tile, EmptyPiece):

                        self.legal_moves.append(Move(board, self, possible_target))

                elif offset == 7 and not (self.position % 8 == 7 and self.is_white() or
                                          self.position % 8 == 0 and self.is_black()):

                    piece = board.get_piece(possible_target)
                    if not isinstance(piece, EmptyPiece):
                        if self.alliance != piece.alliance:
                            self.legal_moves.append(AttackMove(board, self, possible_target, piece))

                elif offset == 9 and not (self.position % 8 == 0 and self.is_white() or
                                          self.position % 8 == 7 and self.is_black()):

                    piece = board.get_piece(possible_target)
                    if not isinstance(piece, EmptyPiece):
                        if self.alliance != piece.alliance:
                            self.legal_moves.append(AttackMove(board, self, possible_target, piece))

    @staticmethod
    def make_move(move):
        return Pawn(move.destination, move.moving_piece.alliance)
from chess_board.utils import valid_target
from chess_board.move import AttackMove, Move, CastleMove
from pieces.piece import Piece, EmptyPiece
from pieces.rook import Rook


class King(Piece):
    ABBREVIATION = "K"

    def __init__(self, position, alliance):
        super().__init__(position, alliance)

        self.first_move = True

    def calculate_legal_moves(self, board):
        self.legal_moves = []
        offsets = {-9, -8, -7, -1, 1, 7, 8, 9}

        for offset in offsets:

            possible_target = self.position + offset

            if self.first_move:
                if offset == 1:
                    free_way = True
                    for i in range(1, 2):
                        if not isinstance(board.get_piece(possible_target + i), EmptyPiece):
                            free_way = False
                            break

                    if free_way:
                        possible_rook = board.get_piece(possible_target + 2)
                        if isinstance(possible_rook, Rook):
                            if possible_rook.first_move and possible_rook.alliance == self.alliance:
                                self.legal_moves.append(CastleMove(board, self, possible_rook.position, True))

                elif offset == -1:
                    free_way = True
                    for i in range(1, 3):
                        if not isinstance(board.get_piece(possible_target - i), EmptyPiece):
                            free_way = False
                            break

                    if free_way:
                        possible_rook = board.get_piece(possible_target - 3)
                        if isinstance(possible_rook, Rook):
                            if possible_rook.first_move and possible_rook.alliance == self.alliance:
                                self.legal_moves.append(CastleMove(board, self, possible_rook.position + 1, False))




            if valid_target(possible_target):
                if not self.first_column(offset) and not self.eighth_column(offset):

                    piece_on_tile = board.get_piece(possible_target)
                    if isinstance(piece_on_tile, EmptyPiece):
                        self.legal_moves.append(Move(board, self, possible_target))

                    else:
                        if piece_on_tile.alliance != self.alliance:
                            self.legal_moves.append(AttackMove(board, self, possible_target, piece_on_tile))

    def first_column(self, offset):
        return self.position % 8 == 0 and offset in (-9, -1, 7)

    def eighth_column(self, offset):
        return self.position % 8 == 7 and offset in (-7, 1, 9)

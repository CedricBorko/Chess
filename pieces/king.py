from board_.utils import valid_target, on_col
from board_.move import AttackMove, Move, CastleMove
from pieces.alliance import Alliance
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

            if valid_target(possible_target):
                if not self.first_column_exclusion(offset) and not self.eighth_column_exclusion(offset):

                    piece_on_tile = board.get_piece(possible_target)
                    if isinstance(piece_on_tile, EmptyPiece):
                        self.legal_moves.append(Move(self, possible_target))

                    else:

                        if piece_on_tile.alliance != self.alliance:
                            self.legal_moves.append(AttackMove(self, possible_target, piece_on_tile))

                # Check for castling
                if self.alliance == Alliance.White and board.white_player.king_first_move or \
                    self.alliance == Alliance.Black and board.black_player.king_first_move:

                    if offset == 1:  # King side
                        has_path = self.has_path(board, 2)
                        if not has_path:
                            continue

                        has_save_path = self.save_path(board, (1, 2))
                        if not has_save_path:
                            continue

                        if valid_target(possible_target + 2):
                            possible_rook = board.get_piece(possible_target + 2)
                            if isinstance(possible_rook, Rook) and possible_rook.original_rook:
                                if possible_rook.first_move and possible_rook.alliance == self.alliance:
                                    self.legal_moves.append(CastleMove(self,
                                                                       possible_rook.position - 1,
                                                                       king_side=True))

                    elif offset == -1:  # Queen side
                        has_path = self.has_path(board, -3)
                        if not has_path:
                            continue

                        has_save_path = self.save_path(board, (-1, -2, -3))
                        if not has_save_path:
                            continue

                        if valid_target(possible_target - 3):
                            possible_rook = board.get_piece(possible_target - 3)
                            if isinstance(possible_rook, Rook) and possible_rook.original_rook:
                                if possible_rook.first_move and possible_rook.alliance == self.alliance:
                                    self.legal_moves.append(CastleMove(self,
                                                                       possible_rook.position + 2,
                                                                       king_side=False))

    def first_column_exclusion(self, offset):
        """Returns if the King is on column 1 and going left"""
        return on_col(0, self.position) and offset in (-9, -1, 7)

    def eighth_column_exclusion(self, offset):
        """Returns if the King is on column 8 and going right"""
        return on_col(7, self.position) and offset in (-7, 1, 9)

    def has_path(self, board, r):
        if r > 0:
            for i in range(1, r + 1):
                if not valid_target(self.position + i):
                    continue
                else:
                    piece = board.get_piece(self.position + i)
                    if not isinstance(piece, EmptyPiece):
                        return False
        else:
            for i in range(-1, -3, -1):
                if not valid_target(self.position + i):
                    continue
                else:
                    piece = board.get_piece(self.position + i)
                    if not isinstance(piece, EmptyPiece):
                        return False
        return True

    def save_path(self, board, offsets):
        for piece in board.current_player.opponent().active_pieces(board):
            for move in piece.legal_moves:
                if move.target in [self.position + offset for offset in offsets]:
                    return False
        return True

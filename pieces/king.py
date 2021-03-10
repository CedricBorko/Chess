from chess_board.utils import valid_target
from chess_board.move import AttackMove, Move, CastleMove
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

            if self.alliance == Alliance.White and board.white_player.king_first_move or \
                self.alliance == Alliance.Black and board.black_player.king_first_move:
                try:
                    if offset == 1:

                        piece_a = board.get_piece(possible_target)
                        piece_b = board.get_piece(possible_target + 1)
                        path_under_attack = False
                        for piece in board.current_player.opponent().active_pieces(board):
                            for move in piece.legal_moves:
                                if move.target == possible_target or move.target == possible_target + 1:
                                    path_under_attack = True
                                    break

                        if not path_under_attack:
                            if isinstance(piece_a, EmptyPiece) and isinstance(piece_b, EmptyPiece):
                                possible_rook = board.get_piece(possible_target + 2)
                                if isinstance(possible_rook, Rook) and possible_rook.original_rook:
                                    if possible_rook.first_move and possible_rook.alliance == self.alliance:
                                        self.legal_moves.append(CastleMove(board, self, possible_rook.position - 1, True))

                    elif offset == -1:
                        piece_a = board.get_piece(possible_target)
                        piece_b = board.get_piece(possible_target - 1)
                        piece_c = board.get_piece(possible_target - 2)

                        path_under_attack = False
                        for piece in board.current_player.opponent().active_pieces(board):
                            for move in piece.legal_moves:
                                if move.target == possible_target or move.target == possible_target - 1 or move.target == possible_target - 2:
                                    path_under_attack = True
                                    break

                        if not path_under_attack:
                            if isinstance(piece_a, EmptyPiece) and \
                                isinstance(piece_b, EmptyPiece) and \
                                isinstance(piece_c, EmptyPiece):
                                possible_rook = board.get_piece(possible_target - 3)
                                if isinstance(possible_rook, Rook) and possible_rook.original_rook:
                                    if possible_rook.first_move and possible_rook.alliance == self.alliance:
                                        self.legal_moves.append(CastleMove(board, self, possible_rook.position + 2, False))
                except IndexError:
                    pass

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

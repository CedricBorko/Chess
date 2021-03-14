from board_.utils import valid_target, on_row, on_col
from board_.move import Move, AttackMove, PromotionMove, EnPassantMove, EnPassantAttackMove
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

                    if on_row(1, self.position) and self.alliance == "White":  # Promotion White Pawn
                        self.legal_moves.append(PromotionMove(self, possible_target))

                    elif on_row(6, self.position) and self.alliance == "Black":  # Promotion Black Pawn
                        self.legal_moves.append(PromotionMove(self, possible_target))

                    else:
                        self.legal_moves.append(Move(self, possible_target))

                # Pawn jump move
                elif offset == 16 and self.first_move and (self.is_black() and on_row(1, self.position) or
                                                           self.is_white() and on_row(6, self.position)):

                    position_in_between = self.position + (8 * get_direction(self.alliance))  # 1 if white else -1
                    if isinstance(board.get_piece(position_in_between), EmptyPiece) \
                        and isinstance(piece_on_tile, EmptyPiece):
                        self.legal_moves.append(EnPassantMove(self, possible_target, position_in_between))

                # Attack and En passant move right
                elif offset in (7, 9):
                    if offset == 7 and (on_col(7, self.position) and self.is_white() or
                                        on_col(0, self.position) and self.is_black()):
                        continue

                    if offset == 9 and (on_col(0, self.position) and self.is_white() or
                                        on_col(7, self.position) and self.is_black()):
                        continue

                    piece = board.get_piece(possible_target)

                    try:
                        en_passant_move = board.current_player.opponent().moves_done[-1]
                    except IndexError:
                        en_passant_move = None

                    if isinstance(piece, EmptyPiece):
                        if isinstance(en_passant_move, EnPassantMove):
                            if en_passant_move.jumped_position == possible_target \
                                and en_passant_move.piece.alliance != self.alliance:
                                self.legal_moves.append(EnPassantAttackMove(self, possible_target, en_passant_move))

                    else:
                        if self.alliance != piece.alliance:
                            if on_row(1, self.position) and self.alliance == "White":
                                self.legal_moves.append(PromotionMove(self, possible_target, piece))
                            elif on_row(6, self.position) and self.alliance == "Black":
                                self.legal_moves.append(PromotionMove(self, possible_target, piece))
                            else:
                                self.legal_moves.append(AttackMove(self, possible_target, piece))

from chess_board.utils import pos_to_letter_code


class Move:
    def __init__(self, board, piece, target):
        self.board = board
        self.piece = piece
        self.target = target

    def __str__(self):
        return f"(M: {self.piece.show()} -> {pos_to_letter_code(self.target)})"

    def __repr__(self):
        return f"(M: {self.piece.show()} -> {pos_to_letter_code(self.target)})"


class AttackMove:
    def __init__(self, board, piece, target, attacked_piece):
        self.board = board
        self.piece = piece
        self.target = target
        self.attacked_piece = attacked_piece

    def __repr__(self):
        return f"(AM: {self.piece.show()} -> {self.attacked_piece.show()})"

    def __str__(self):
        return f"(AM: {self.piece.show()} -> {self.attacked_piece.show()})"


class CastleMove:
    def __init__(self, board, king, target, king_side=True):
        self.board = board
        self.king = king
        self.target = target
        self.king_side = king_side

    def __repr__(self):
        return f"(CM: {self.king.show()} -> {self.board.get_piece(self.target).show()})"

    def __str__(self):
        return f"(CM: {self.king.show()} -> {self.board.get_piece(self.target).show()})"


class PromotionMove:
    def __init__(self, board, pawn, target, other_piece=None):
        self.board = board
        self.pawn = pawn
        self.target = target
        self.other_piece = other_piece
        self.promotion_to = None

    def __repr__(self):
        return f"(PM: {self.pawn.show()} -> {self.promotion_to.show()})"

    def __str__(self):
        return f"(PM: {self.pawn.show()} -> {self.promotion_to.show()})"


class EnPassantMove:
    def __init__(self, board, piece, target, jumped_position):
        self.board = board
        self.piece = piece
        self.target = target
        self.jumped_position = jumped_position

    def __str__(self):
        return f"(DM: {self.piece.show()} -> {pos_to_letter_code(self.target)})"

    def __repr__(self):
        return f"(DM: {self.piece.show()} -> {pos_to_letter_code(self.target)})"

    def __eq__(self, other):
        return self.target == other.target and self.piece == other.piece


class EnPassantAttackMove:
    def __init__(self, board, piece, target, en_passant_move):
        self.board = board
        self.piece = piece
        self.target = target
        self.attacked_piece = en_passant_move.piece
        self.attacked_piece.position = en_passant_move.target
        self.en_passant_move = en_passant_move

    def __repr__(self):
        return f"(EM: {self.piece.show()} -> {self.attacked_piece.show()})"

    def __str__(self):
        return f"(EM: {self.piece.show()} -> {self.attacked_piece.show()})"

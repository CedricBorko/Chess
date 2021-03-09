from chess_board.utils import letter_code

class Move:
    def __init__(self, board, piece, target):
        self.board = board
        self.piece = piece
        self.target = target

    def __str__(self):
        return f"(M: {self.piece.show()} -> {letter_code(self.target)})"

    def __repr__(self):
        return f"(M: {self.piece.show()} -> {letter_code(self.target)})"


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
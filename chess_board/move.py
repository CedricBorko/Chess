class Move:
    def __init__(self, board, piece, destination):
        self.board = board
        self.piece = piece
        self.destination = destination


class AttackMove(Move):
    def __init__(self, board, piece, destination, attacked_piece):
        super().__init__(board, piece, destination)

        self.attacked_piece = attacked_piece


class PawnMove(Move):
    def __init__(self, board, piece, destination):
        super().__init__(board, piece, destination)
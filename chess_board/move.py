class Move:
    def __init__(self, board, piece, destination):
        self.board = board
        self.piece = piece
        self.destination = destination

    def __repr__(self):
        return "{} is attacking an empty tile at {}".format(self.piece, self.destination)


class AttackMove(Move):
    def __init__(self, board, piece, destination, attacked_piece):
        super().__init__(board, piece, destination)

        self.attacked_piece = attacked_piece

    def __repr__(self):
        return "{} is attacking {} at {}".format(self.piece, self.attacked_piece, self.destination)


class PawnMove(Move):
    def __init__(self, board, piece, destination):
        super().__init__(board, piece, destination)
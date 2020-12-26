import copy


class Move:
    def __init__(self, board, piece, destination):
        self.board = board
        self.piece = piece
        self.destination = destination

    def __repr__(self):
        return "Destination {}".format(self.destination)

    @property
    def x(self):
        return self.destination % 8

    @property
    def y(self):
        return self.destination // 8

    def move(self):
        copied_board = copy.deepcopy(self.board)
        copied_board.set_piece(self.piece.position, self.destination, self.piece)
        copied_board.update()
        if copied_board.is_valid():
            old = self.piece.position
            self.piece.position = self.destination
            self.board.set_piece(old, self.destination, self.piece)
            self.board.update()
            self.board.next_player()
            return True
        else:
            return False


class AttackMove(Move):
    def __init__(self, board, piece, destination, attacked_piece):
        super().__init__(board, piece, destination)

        self.attacked_piece = attacked_piece

    def __repr__(self):
        return "{} on {} is attacking {} at {}".format(self.piece, self.piece.position,
                                                       self.attacked_piece, self.destination)

    def move(self):
        pass


class PawnMove(Move):
    def __init__(self, board, piece, destination):
        super().__init__(board, piece, destination)

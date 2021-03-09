class Player:
    def __init__(self, board, moves=None):
        self.board = board
        self.moves = moves or []

    def next_player(self):
        self.board.current_player = self.opponent()

    def opponent(self):
        pass

    def active_pieces(self):
        pass


class WhitePlayer(Player):
    def __init__(self, board, moves=None):
        super().__init__(board, moves)

    def opponent(self):
        return self.board.black_player

    def active_pieces(self):
        return self.board.white_pieces()


class BlackPlayer(Player):
    def __init__(self, board, moves=None):
        super().__init__(board, moves)

    def opponent(self):
        return self.board.white_player

    def active_pieces(self):
        return self.board.black_pieces()

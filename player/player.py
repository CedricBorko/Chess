from pieces.alliance import Alliance
from pieces.king import King


class Player:
    def __init__(self, board, my_moves, enemy_moves):
        self.board = board
        self.my_moves = my_moves
        self.my_king = self.has_king()

    def get_active_pieces(self):
        pass

    def has_king(self):
        pass

    def is_move_legal(self, move):
        return move in self.my_moves

    def is_check(self):
        return False

    def is_stalemate(self):
        return False

    def is_checkmate(self):
        return False

    def is_castle(self):
        return False


class WhitePlayer(Player):
    def __init__(self, board, my_moves, enemy_moves):
        super().__init__(board, my_moves, enemy_moves)

    def get_active_pieces(self):
        return self.board.active_pieces(Alliance.White)

    def has_king(self):
        for piece in self.get_active_pieces():
            if isinstance(piece, King):
                return piece
        raise Exception("No king! Invalid board")


class BlackPlayer(Player):
    def __init__(self, board, my_moves, enemy_moves):
        super().__init__(board, my_moves, enemy_moves)

    def get_active_pieces(self):
        return self.board.active_pieces(Alliance.Black)

    def has_king(self):
        for piece in self.get_active_pieces():
            if isinstance(piece, King):
                return piece
        raise Exception("No king! Invalid board")
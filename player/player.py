from chess_board.move import AttackMove
from pieces.alliance import Alliance
from pieces.king import King


def is_stalemate():
    return False


class Player:
    def __init__(self, board, my_moves):
        self.board = board
        self.my_moves = my_moves
        self.my_king = self.has_king()

    def get_active_pieces(self):
        pass

    def has_king(self):
        pass

    def enemy(self):
        pass

    def is_move_legal(self, move):
        return move in self.my_moves

    def is_check(self, board):
        for piece in self.enemy().get_active_pieces():
            piece.calculate_legal_moves(board)
            for move in piece.legal_moves:
                if isinstance(move, AttackMove) and isinstance(move.attacked_piece, King):
                    return True
        return False

    def is_checkmate(self):
        return self.is_check(self.board)

    def is_castle(self):
        return False


class WhitePlayer(Player):
    def __init__(self, board, my_moves):
        super().__init__(board, my_moves)

    def get_active_pieces(self):
        return self.board.active_pieces(Alliance.White)

    def has_king(self):
        for piece in self.get_active_pieces():
            if isinstance(piece, King):
                return piece
        raise Exception("No king! Invalid board")

    def enemy(self):
        return self.board.black_player


class BlackPlayer(Player):
    def __init__(self, board, my_moves):
        super().__init__(board, my_moves)

    def get_active_pieces(self):
        return self.board.active_pieces(Alliance.Black)

    def has_king(self):
        for piece in self.get_active_pieces():
            if isinstance(piece, King):
                return piece
        raise Exception("No king! Invalid board")

    def enemy(self):
        return self.board.white_player

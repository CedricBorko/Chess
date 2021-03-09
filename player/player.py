from chess_board.move import AttackMove
from pieces.king import King


class Player:
    def __init__(self, board, alliance, moves=None):
        self.board = board
        self.alliance = alliance
        self.moves = moves or []

    def next_player(self):
        self.board.current_player = self.opponent()

    def opponent(self):
        pass

    def active_pieces(self):
        pass

    def is_check(self):
        opponent = self.opponent()
        pieces = opponent.active_pieces()

        for piece in pieces:
            piece.calculate_legal_moves(self.board)
        self.moves = [piece.legal_moves for piece in pieces]

        moves_with_king_as_target = []
        for move_list in self.moves:
            for move in move_list:
                if isinstance(move, AttackMove):
                    if isinstance(move.attacked_piece, King):
                        moves_with_king_as_target.append(move)
        print(moves_with_king_as_target)
        return len(moves_with_king_as_target) > 0


class WhitePlayer(Player):
    def __init__(self, board, alliance, moves=None):
        super().__init__(board, alliance, moves)

    def opponent(self):
        return self.board.black_player

    def active_pieces(self):
        return self.board.get_alliance_pieces("White")


class BlackPlayer(Player):
    def __init__(self, board, alliance, moves=None):
        super().__init__(board, alliance, moves)

    def opponent(self):
        return self.board.white_player

    def active_pieces(self):
        return self.board.get_alliance_pieces("Black")

import copy

from chess.engine.move import AttackMove, PromotionMove
from chess.engine.pieces import King


class Player:
    def __init__(self, board, alliance, moves=None):
        self.board = board
        self.alliance = alliance
        self.moves = moves or []
        self.king_first_move = True
        self.lost_pieces = []
        self.moves_done = []

    def next_player(self):
        self.board.current_player = self.opponent()
        self.board.calculate_legal_moves()

    def opponent(self):
        pass

    def active_pieces(self, board):
        return board.current_player.active_pieces(board)

    def is_check(self, board):
        opponent = self.opponent()
        pieces = opponent.active_pieces(board)

        for piece in pieces:
            piece.calculate_legal_moves(board)
        self.moves = [piece.legal_moves for piece in pieces]

        for move_list in self.moves:
            for move in move_list:
                if isinstance(move, AttackMove) or isinstance(move, PromotionMove):
                    if isinstance(move.attacked_piece, King):
                        return True
        return False

    def get_possible_moves(self):
        pieces = self.active_pieces(self.board)
        for piece in pieces:
            piece.calculate_legal_moves(self.board)
            updated_legal_moves = []
            copied_board = copy.deepcopy(self.board)
            for move in piece.legal_moves:
                move.execute(copied_board)
                if not copied_board.current_player.is_check(copied_board):
                    updated_legal_moves.append(move)
                move.undo(copied_board)
            piece.legal_moves = updated_legal_moves

        return [move for piece in pieces for move in piece.legal_moves]

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return self.__class__.__name__


class WhitePlayer(Player):
    def __init__(self, board, alliance, moves=None):
        super().__init__(board, alliance, moves)

    def opponent(self):
        return self.board.black_player

    def active_pieces(self, board):
        return board.get_alliance_pieces("White")


class BlackPlayer(Player):
    def __init__(self, board, alliance, moves=None):
        super().__init__(board, alliance, moves)

    def opponent(self):
        return self.board.white_player

    def active_pieces(self, board):
        return board.get_alliance_pieces("Black")

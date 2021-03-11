import copy

from chess_board.move import AttackMove
from pieces.king import King


class Player:
    def __init__(self, board, alliance, king=None, moves=None):
        self.board = board
        self.alliance = alliance
        self.moves = moves or []
        self.king_first_move = True
        self.rook_q_first_move = True
        self.rook_k_first_move = True

    def next_player(self):
        self.board.current_player = self.opponent()

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

        moves_with_king_as_target = []
        for move_list in self.moves:
            for move in move_list:
                if isinstance(move, AttackMove):
                    if isinstance(move.attacked_piece, King):
                        moves_with_king_as_target.append(move)
        return len(moves_with_king_as_target) > 0

    def is_checkmate(self):
        pieces = self.active_pieces(self.board)
        for piece in pieces:
            piece.calculate_legal_moves(self.board)
            updated_legal_moves = []
            copied_board = copy.deepcopy(self.board)
            for move in piece.legal_moves:
                piece.make_move(copied_board, move)
                if not copied_board.current_player.is_check(copied_board):
                    updated_legal_moves.append(move)
                copied_board = copy.deepcopy(self.board)
            piece.legal_moves = updated_legal_moves

        moves = [move for piece in pieces for move in piece.legal_moves]

        return len(moves) == 0

    def is_stalemate(self):
        pieces = self.active_pieces(self.board)
        for piece in pieces:
            piece.calculate_legal_moves(self.board)
            updated_legal_moves = []
            copied_board = copy.deepcopy(self.board)
            for move in piece.legal_moves:
                piece.make_move(copied_board, move)
                if not copied_board.current_player.is_check(copied_board):
                    updated_legal_moves.append(move)
                copied_board = copy.deepcopy(self.board)
            piece.legal_moves = updated_legal_moves

        moves = [move for piece in pieces for move in piece.legal_moves]

        return len(moves) == 0

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

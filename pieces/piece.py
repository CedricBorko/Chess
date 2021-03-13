from board_.utils import pos_to_letter_code
from pieces.alliance import Alliance


class Piece:
    ABBREVIATION = ""

    def __init__(self, position, alliance):
        self.NAME = self.__class__.__name__
        self.position = position
        self.alliance = alliance

        self.legal_moves = []

    def __repr__(self):
        return "{} {}".format(self.alliance, self.NAME)

    def __str__(self):
        return self.ABBREVIATION if self.alliance == Alliance.White else self.ABBREVIATION.lower()

    def show(self):
        return f"{self.NAME} {self.alliance} {pos_to_letter_code(self.position)}"

    def is_black(self):
        return self.alliance == Alliance.Black

    def is_white(self):
        return self.alliance == Alliance.White

    @property
    def col(self):
        return self.position % 8

    @property
    def row(self):
        return self.position // 8

    def __eq__(self, other):
        return self.position == other.position and self.alliance == other.alliance

    def get_move(self, target):
        for move in self.legal_moves:
            if move.target == target:
                return move


class EmptyPiece(Piece):
    ABBREVIATION = "·"

    def __init__(self, position=None, alliance=None):
        super().__init__(position, alliance)

    @staticmethod
    def calculate_legal_moves(board):
        return []

from enum import Enum

from pieces.alliance import Alliance


class Piece:

    Name = ""

    def __init__(self, position, alliance):
        self.position = position
        self.alliance = alliance

        self.legal_moves = []

    def __repr__(self):
        return "{} {}".format(self.alliance, self.Name)

    def __str__(self):
        return self.Name

    def move(self, target_position):
        if self.valid_target(target_position):
            self.position = target_position

    def valid_target(self, target_position):
        pass

    def calculate_legal_moves(self, board):
        pass

    def is_black(self):
        return self.alliance == Alliance.Black

    def is_white(self):
        return self.alliance == Alliance.White

    @property
    def x(self):
        return self.position % 8

    @property
    def y(self):
        return self.position // 8

    def get_move(self, destination):
        for move in self.legal_moves:
            if move.destination == destination:
                return move
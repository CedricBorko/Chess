from enum import Enum

from pieces.alliance import Alliance


class Piece:

    Name = ""

    def __init__(self, position, alliance):
        self.position = position
        self.alliance = alliance

        self.legal_moves = set()

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


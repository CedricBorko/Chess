class Piece:

    def __init__(self, position, alliance):
        self.position = position
        self.__alliance = alliance

    def __repr__(self):
        return "This is a {} of alliance {} on position {}".format(self, self.__alliance, self.position)

    def get_alliance(self):
        return self.__alliance

    def move(self, target_position):
        if self.valid_target(target_position):
            self.position = target_position

    def valid_target(self, target_position):
        pass




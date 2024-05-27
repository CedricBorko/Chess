from __future__ import annotations

from chess.engine.alliance import Alliance
from chess.engine.move import Move
from chess.engine.pieces import King, Piece

DEFAULT_BOARD_STATE = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
PIECE_ABBREVIATIONS = "kqrbnpKQRBNP"

LETTERS = "abcdefgh"

COORDINATES = [
    f"{letter}{index}"
    for index in range(8, 0, -1)
    for letter in LETTERS
]


class Board:
    def __init__(self, fen_string: str = DEFAULT_BOARD_STATE) -> None:
        self.active_player = Alliance.WHITE
        self.castling_availability = "KQkq"
        self.en_passant_target_square = None
        self.halfmove_clock = 0
        self.fullmove_number = 1

        self.state: list[Piece | None] = []
        self.moves: list[Move] = []

        self.white_pieces = set()
        self.black_pieces = set()

        self.parse_fen(fen_string)

    def __repr__(self) -> str:
        return '\n'.join(
            row for row in [
                ''.join(str(piece) for piece in self.get_pieces_in_row(i))
                for i in range(8)
            ]
        )

    def get_pieces_in_row(self, row_index: int) -> list[Piece]:
        return self.state[row_index * 8:8 + row_index * 8]

    def get_pieces_in_column(self, column_index: int) -> list[Piece]:
        return self.state[column_index:64:8]

    def parse_fen(self, fen_string: str) -> None:
        fen_parts = fen_string.split()

        self.state: list[Piece | None] = [None for _ in range(64)]

        piece_positions = fen_parts[0]
        for row_index, row in enumerate(piece_positions.split("/")):
            column = 0
            for character in row:
                if character.isdigit():
                    column += int(character)
                else:
                    piece = Piece.from_abbreviation(row_index * 8 + column, character)

                    if piece.alliance == Alliance.WHITE:
                        self.white_pieces.add(piece)
                    else:
                        self.black_pieces.add(piece)

                    self.state[piece.position] = piece
                    column += 1

        self.active_player = Alliance.WHITE if fen_parts[1] == "w" else Alliance.BLACK
        self.castling_availability = fen_parts[2]
        self.en_passant_target_square = fen_parts[3]
        self.halfmove_clock = int(fen_parts[4])
        self.fullmove_number = int(fen_parts[5])

    def to_fen(self) -> str:
        """
        Convert the current state of the board into its FEN (Forsyth-Edwards-Notation) representation.
        https://de.wikipedia.org/wiki/Forsyth-Edwards-Notation

        """
        fen_string = ""

        for row in (self.get_pieces_in_row(i) for i in range(8)):
            empty_count = 0

            for piece in row:
                if piece is None:
                    empty_count += 1
                    continue

                if empty_count > 0:
                    fen_string += str(empty_count)
                    empty_count = 0

                fen_string += piece.abbreviation

            if empty_count > 0:
                fen_string += str(empty_count)

            fen_string += "/"

        if fen_string[-1] == "/":
            fen_string = fen_string[:-1] + " "

        fen_string += f"{self.active_player.to_fen()} "
        fen_string += f"{self.castling_availability} "
        fen_string += f"{self.en_passant_target_square} "
        fen_string += f"{self.halfmove_clock} {self.fullmove_number}"

        return fen_string

    def set_piece_at(self, position: int, piece: Piece | None) -> None:
        if piece is not None:
            self.state[position], self.state[piece.position] = piece, None
            piece.position = position
        else:
            self.state[position] = piece

    def get_piece_at(self, position: int) -> Piece | None:
        return self.state[position]

    def get_available_pieces(self, alliance: Alliance) -> set[Piece]:
        if alliance == Alliance.WHITE: return self.white_pieces
        return self.black_pieces

    def all_active_pieces(self) -> set[Piece]:
        return self.get_available_pieces(Alliance.WHITE).union(self.get_available_pieces(Alliance.BLACK))

    def next_turn(self) -> None:
        self.active_player = Alliance.WHITE if self.active_player == Alliance.BLACK else Alliance.WHITE
        self.halfmove_clock += 1
        self.fullmove_number += 0.5

        for piece in self.get_available_pieces(self.active_player):
            piece.calculate_legal_moves(self)


def is_valid_position(position: int) -> bool:
    return 0 <= position < 64


def position_to_coordinate(position: int) -> str:
    return COORDINATES[position]


def coordinate_to_position(coordinate: str) -> int:
    letter, index, *_ = coordinate

    if int(index) < 1 or letter not in LETTERS: raise IndexError("Out of bounds.")
    y = 8 - int(index)
    return y * 8 + (ord(letter) - ord("a"))


def main() -> None:
    FEN = DEFAULT_BOARD_STATE
    board = Board(FEN)
    print(board)


if __name__ == '__main__':
    main()

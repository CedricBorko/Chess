import string

from engine.pieces import Piece, PieceType

DEFAULT = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
PIECE_ABBREVIATIONS = "kqrbnpKQRBNP"

Board = list[Piece]


def is_tile_empty(board: Board, position: int) -> bool:
    return board[position].piece_type == PieceType.Null


def parse_fen_string(fen_string: str) -> Board:
    position = 0

    positions, *options = fen_string.split(" ")
    pieces = []

    for character in positions:
        if character == "/": continue
        if character in PIECE_ABBREVIATIONS:
            pieces.append(Piece.from_fen(position, character))
            position += 1
        else:
            number_of_empty_tiles = int(character)
            for i in range(number_of_empty_tiles): pieces.append(Piece.from_fen(position, "")); position += 1

    print("\n".join(map(str, pieces)))


if __name__ == '__main__':
    parse_fen_string(DEFAULT)

from __future__ import annotations
from typing import TYPE_CHECKING
from abc import ABC, abstractmethod

from chess.engine.alliance import Alliance
from chess.engine.move import Move

if TYPE_CHECKING:
    from chess.engine.board import Board


class Piece(ABC):
    OFFSETS: set[int] = set()

    def __init__(self, position: int, alliance: Alliance):
        self.position = position
        self.alliance = alliance

        self.abbreviation = self.__class__.__name__[0]
        if self.alliance == Alliance.BLACK:
            self.abbreviation = self.abbreviation.lower()

        self.move_count = 0
        self.is_active = True
        self.legal_moves: set[Move] = set()

    @property
    def has_moved(self) -> bool:
        return self.move_count > 0

    def __repr__(self):
        return self.abbreviation

    def __str__(self):
        return self.abbreviation

    def show(self):
        from chess.engine.board import position_to_coordinate

        return f"{self.abbreviation} {position_to_coordinate(self.position)}"

    def is_black(self):
        return self.alliance == Alliance.BLACK

    def is_white(self):
        return self.alliance == Alliance.WHITE

    @property
    def col(self):
        return self.position % 8

    @property
    def row(self):
        return self.position // 8

    def __eq__(self, other: Piece):
        return (self.position, self.alliance) == (other.position, other.alliance)

    def __hash__(self) -> int:
        return hash((self.position, self.alliance.value))

    def get_move(self, target: int):
        for move in self.legal_moves:
            if move.target == target:
                return move

    @abstractmethod
    def calculate_legal_moves(self, board: Board) -> set[Move]:
        ...

    @classmethod
    def from_abbreviation(cls: Piece, position: int, abbreviation: str) -> Piece | None:
        from chess.engine.pieces import Bishop, King, Knight, Pawn, Queen, Rook

        alliance = Alliance.WHITE if abbreviation.isupper() else Alliance.BLACK

        match abbreviation.lower():
            case "k": return King(position, alliance)
            case "n": return Knight(position, alliance)
            case "q": return Queen(position, alliance)
            case "p": return Pawn(position, alliance)
            case "r": return Rook(position, alliance)
            case "b": return Bishop(position, alliance)
            case _: return None

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class Alliance(Enum):
    Null = 0
    White = 1
    Black = 2

    @classmethod
    def from_abbreviation(cls: Alliance, abbreviation: str) -> Alliance:
        return Alliance.Black if abbreviation.islower() else Alliance.White


class PieceType(Enum):
    Null = 0
    King = auto()
    Queen = auto()
    Rook = auto()
    Bishop = auto()
    Knight = auto()
    Pawn = auto()

    def abbreviation(self) -> str:
        if self == PieceType.Null: return ""
        if self == PieceType.King: return "K"
        if self == PieceType.Queen: return "Q"
        if self == PieceType.Rook: return "R"
        if self == PieceType.Bishop: return "B"
        if self == PieceType.Knight: return "N"
        if self == PieceType.Pawn: return "P"

    @classmethod
    def from_abbreviation(cls: PieceType, abbreviation: str) -> PieceType:
        match abbreviation.lower():
            case "": return PieceType.Null
            case "k": return PieceType.King
            case "q": return PieceType.Queen
            case "r": return PieceType.Rook
            case "b": return PieceType.Bishop
            case "n": return PieceType.Knight
            case "p": return PieceType.Pawn


@dataclass
class Piece:
    position: int
    piece_type: PieceType
    alliance: Alliance

    def column(self) -> int:
        return self.position % 8

    def row(self) -> int:
        return self.position // 8

    @classmethod
    def from_fen(cls: type[Piece], position: int, abbreviation: str) -> Piece:
        return Piece(position, PieceType.from_abbreviation(abbreviation), Alliance.from_abbreviation(abbreviation))


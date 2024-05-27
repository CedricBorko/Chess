from __future__ import annotations

from enum import Enum


class Alliance(Enum):
    WHITE = 0
    BLACK = 1

    def opponent(self) -> Alliance:
        return Alliance.BLACK if self == Alliance.WHITE else Alliance.BLACK

    def to_fen(self) -> str:
        return self.value[0].lower()

    def get_direction(self) -> int:
        return -1 if self == Alliance.WHITE else 1

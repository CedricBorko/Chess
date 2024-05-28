from unittest import TestCase

from chess.engine.pieces import Knight
from chess.engine.board import Board

board = Board()


class TestKnight(TestCase):

    def test_legal_moves(self) -> None:
        knight = board.get_piece_at(6)
        knight.calculate_legal_moves(board)
        self.assertEqual(len(knight.legal_moves), 2)

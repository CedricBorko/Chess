from unittest import TestCase

from chess.engine.alliance import Alliance
from chess.engine.board import (
    Board,
    is_valid_position,
    coordinate_to_position,
    position_to_coordinate,
)

FEN_EXAMPLES = [
    {"depth": 1, "nodes": 8, "fen": "r6r/1b2k1bq/8/8/7B/8/8/R3K2R b KQ - 3 2"},
    {"depth": 1, "nodes": 8, "fen": "8/8/8/2k5/2pP4/8/B7/4K3 b - d3 0 3"},
    {
        "depth": 1,
        "nodes": 19,
        "fen": "r1bqkbnr/pppppppp/n7/8/8/P7/1PPPPPPP/RNBQKBNR w KQkq - 2 2",
    },
    {
        "depth": 1,
        "nodes": 5,
        "fen": "r3k2r/p1pp1pb1/bn2Qnp1/2qPN3/1p2P3/2N5/PPPBBPPP/R3K2R b KQkq - 3 2",
    },
    {
        "depth": 1,
        "nodes": 44,
        "fen": "2kr3r/p1ppqpb1/bn2Qnp1/3PN3/1p2P3/2N5/PPPBBPPP/R3K2R b KQ - 3 2",
    },
    {
        "depth": 1,
        "nodes": 39,
        "fen": "rnb2k1r/pp1Pbppp/2p5/q7/2B5/8/PPPQNnPP/RNB1K2R w KQ - 3 9",
    },
    {"depth": 1, "nodes": 9, "fen": "2r5/3pk3/8/2P5/8/2K5/8/8 w - - 5 4"},
    {
        "depth": 3,
        "nodes": 62379,
        "fen": "rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8",
    },
    {
        "depth": 3,
        "nodes": 89890,
        "fen": "r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10",
    },
    {"depth": 6, "nodes": 1134888, "fen": "3k4/3p4/8/K1P4r/8/8/8/8 b - - 0 1"},
    {"depth": 6, "nodes": 1015133, "fen": "8/8/4k3/8/2p5/8/B2P2K1/8 w - - 0 1"},
    {"depth": 6, "nodes": 1440467, "fen": "8/8/1k6/2b5/2pP4/8/5K2/8 b - d3 0 1"},
    {"depth": 6, "nodes": 661072, "fen": "5k2/8/8/8/8/8/8/4K2R w K - 0 1"},
    {"depth": 6, "nodes": 803711, "fen": "3k4/8/8/8/8/8/8/R3K3 w Q - 0 1"},
    {"depth": 4, "nodes": 1274206, "fen": "r3k2r/1b4bq/8/8/8/8/7B/R3K2R w KQkq - 0 1"},
    {"depth": 4, "nodes": 1720476, "fen": "r3k2r/8/3Q4/8/8/5q2/8/R3K2R b KQkq - 0 1"},
    {"depth": 6, "nodes": 3821001, "fen": "2K2r2/4P3/8/8/8/8/8/3k4 w - - 0 1"},
    {"depth": 5, "nodes": 1004658, "fen": "8/8/1P2K3/8/2n5/1q6/8/5k2 b - - 0 1"},
    {"depth": 6, "nodes": 217342, "fen": "4k3/1P6/8/8/8/8/K7/8 w - - 0 1"},
    {"depth": 6, "nodes": 92683, "fen": "8/P1k5/K7/8/8/8/8/8 w - - 0 1"},
    {"depth": 6, "nodes": 2217, "fen": "K1k5/8/P7/8/8/8/8/8 w - - 0 1"},
    {"depth": 7, "nodes": 567584, "fen": "8/k1P5/8/1K6/8/8/8/8 w - - 0 1"},
    {"depth": 4, "nodes": 23527, "fen": "8/8/2k5/5q2/5n2/8/5K2/8 b - - 0 1"},
]


class TestBoard(TestCase):
    def test_parse_fen_string(self):
        for example in FEN_EXAMPLES:
            fen_string = example["fen"]
            board = Board(fen_string)
            self.assertEqual(fen_string, board.to_fen())

    def test_is_valid_position(self) -> None:
        count = 0
        for i in range(-10, 100):
            count += 1 if is_valid_position(i) else 0

        self.assertEqual(count, 64)

    def test_position_to_coordinate(self) -> None:
        self.assertEqual(position_to_coordinate(0), "a8")
        self.assertEqual(position_to_coordinate(63), "h1")
        self.assertEqual(position_to_coordinate(37), "f4")

    def test_coordinate_to_position(self) -> None:
        self.assertEqual(coordinate_to_position("a8"), 0)
        self.assertEqual(coordinate_to_position("h1"), 63)
        self.assertEqual(coordinate_to_position("f4"), 37)

    def test_is_in_check(self) -> None:
        # board = Board("4k3/8/8/8/8/8/8/3KQ3 w KQkq - 0 1")
        # self.assertEqual(True, board.is_checked(Alliance.BLACK))
        board = Board("4k3/8/8/8/b7/8/8/3KQ3 b KQkq - 0 1")
        print(board)
        self.assertEqual(True, board.is_checked(Alliance.WHITE))


def main() -> None:
    test = TestBoard()
    test.test_is_in_check()


if __name__ == "__main__":
    main()

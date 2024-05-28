from unittest import TestCase

from chess.engine.alliance import Alliance


class TestAlliance(TestCase):
    def test_white_opponent(self) -> None:
        self.assertEqual(Alliance.BLACK, Alliance.WHITE.opponent())

    def test_black_opponent(self) -> None:
        self.assertEqual(Alliance.WHITE, Alliance.BLACK.opponent())


def main() -> None:
    test = TestAlliance()
    test.test_get_opponent()


if __name__ == "__main__":
    main()

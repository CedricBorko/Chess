from PySide6.QtGui import QImage

from chess.io.paths import RESOURCES


def load_piece_graphics() -> dict[str, QImage]:
    with open(RESOURCES / "pieces" / "pieces.png", "rb") as f:
        content = f.read()
        sprite = QImage.fromData(content)

        images = [
            sprite.copy(
                i * sprite.width() // 6,
                j * sprite.height() // 2,
                sprite.width() // 6,
                sprite.height() // 2
            )
            for j in range(2)
            for i in range(6)
        ]

        images = {
            key: image for key, image in zip("KQBNRPkqbnrp", images)
        }

    return images

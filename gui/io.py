from PySide6.QtGui import QImage

from chess.io.paths import RESOURCES


def load_piece_graphics() -> dict[str, QImage]:
    images = {}

    for file in (RESOURCES / "pieces" / "Set 1").iterdir():
        key = file.stem[0].lower() if file.stem[1] == "B" else file.stem[0]
        images[key] = QImage.fromData(file.read_bytes())
    return images

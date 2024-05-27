import sys

from PySide6.QtWidgets import QApplication, QMainWindow


def main():
    app = QApplication(sys.argv)
    main_window = QMainWindow()
    main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
import sys

from PySide6.QtWidgets import QApplication, QMainWindow

from gui.mainwindow import Window


def main():
    app = QApplication(sys.argv)
    main_window = Window()
    main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

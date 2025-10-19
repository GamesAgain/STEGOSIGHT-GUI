import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from Stegosight.ui.stegosight_app import StegoSightApp


def main() -> None:
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)

    window = StegoSightApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

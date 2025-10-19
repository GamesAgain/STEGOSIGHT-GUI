import sys
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from Stegosight.ui.stegosight_app import StegoSightApp
else:
    from .ui.stegosight_app import StegoSightApp


def main() -> None:
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)

    window = StegoSightApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

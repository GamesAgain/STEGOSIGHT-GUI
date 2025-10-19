import sys
from pathlib import Path

from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtWidgets import QApplication

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from Stegosight.ui.stegosight_app import StegoSightApp
else:
    from .ui.stegosight_app import StegoSightApp


def main() -> None:
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)

    window = StegoSightApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

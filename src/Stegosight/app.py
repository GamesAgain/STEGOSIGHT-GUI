import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from myapp.views.main_window import MainWindow
try:
    from myapp.core.theme import load_qss
except Exception:
    def load_qss(_): return ""

def main():
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    # Optional theme (will work after resources compiled)
    app.setStyleSheet(load_qss(":/qss/dark.qss"))
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

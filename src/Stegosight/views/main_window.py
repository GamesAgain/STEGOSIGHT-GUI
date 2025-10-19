from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow

UI_PATH = ":/ui/main_window.ui"  # from Qt Resource

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(UI_PATH, self)

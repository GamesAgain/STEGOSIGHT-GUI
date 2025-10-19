from PyQt5.QtCore import QFile, QTextStream

def load_qss(resource_path: str) -> str:
    f = QFile(resource_path)
    if not f.exists():
        return ""
    if not f.open(QFile.ReadOnly | QFile.Text):
        return ""
    ts = QTextStream(f)
    ts.setCodec("UTF-8")
    return ts.readAll()

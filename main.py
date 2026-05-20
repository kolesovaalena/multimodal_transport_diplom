import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

from PySide6.QtWidgets import QApplication
from ui_main import TransportApp

app = QApplication([])

window = TransportApp()

window.show()

app.exec()

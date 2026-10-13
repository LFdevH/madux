import signal
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QApplication, QWidget


class Mascote(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(160, 160)
        self.arrastando = None

    def paintEvent(self, evento):
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing)
        pintor.setPen(Qt.NoPen)

        pintor.setBrush(QColor("#7c3aed"))
        pintor.drawEllipse(10, 10, 140, 140)

        pintor.setBrush(QColor("white"))
        pintor.drawEllipse(45, 55, 22, 30)
        pintor.drawEllipse(93, 55, 22, 30)

    def mousePressEvent(self, evento):
        self.arrastando = evento.globalPosition().toPoint() - self.pos()

    def mouseMoveEvent(self, evento):
        if self.arrastando is not None:
            self.move(evento.globalPosition().toPoint() - self.arrastando)

    def mouseReleaseEvent(self, evento):
        self.arrastando = None

    def mouseDoubleClickEvent(self, evento):
        self.close()


signal.signal(signal.SIGINT, signal.SIG_DFL)

app = QApplication(sys.argv)
mascote = Mascote()
mascote.show()
app.exec()

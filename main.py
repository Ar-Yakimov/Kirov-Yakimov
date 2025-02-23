import random
import sys

from PyQt6 import uic
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtWidgets import QApplication, QMainWindow


class CircleWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('UI.ui', self)
        self.circles = []
        self.drawButton.clicked.connect(self.draw_circle)

    def draw_circle(self):
        diameter = random.randint(10, 100)
        x = random.randint(0, self.width() - diameter)
        y = random.randint(0, self.height() - diameter)
        self.circles.append((x, y, diameter))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QColor(255, 255, 0))  # Желтый цвет
        for (x, y, diameter) in self.circles:
            painter.drawEllipse(x, y, diameter, diameter)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = CircleWidget()
    ex.show()
    sys.exit(app.exec())

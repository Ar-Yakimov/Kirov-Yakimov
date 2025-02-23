import random
import sys

from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget


class CircleWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.circles = []
        self.drawButton = QPushButton('Нарисовать окружность', self)
        self.drawButton.clicked.connect(self.draw_circle)

        layout = QVBoxLayout()
        layout.addWidget(self.drawButton)
        self.setLayout(layout)

    def draw_circle(self):
        diameter = random.randint(10, 100)
        x = random.randint(0, self.width() - diameter)
        y = random.randint(0, self.height() - diameter)

        color = QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        self.circles.append((x, y, diameter, color))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        for (x, y, diameter, color) in self.circles:
            painter.setBrush(color)
            painter.drawEllipse(x, y, diameter, diameter)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Рисование окружностей 2")

        self.circleWidget = CircleWidget()
        self.setCentralWidget(self.circleWidget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.resize(800, 800)
    mainWin.show()
    sys.exit(app.exec())

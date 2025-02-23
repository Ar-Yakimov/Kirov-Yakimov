import sqlite3
import sys

from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox


class CoffeeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('UI.ui', self)

        self.load_data_button.clicked.connect(self.load_coffee_data)

    def load_coffee_data(self):
        try:
            connection = sqlite3.connect('coffee.sqlite')
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM coffee")
            rows = cursor.fetchall()

            # Очищаем предыдущие данные
            self.coffee_list.clear()

            for row in rows:
                coffee_info = f"ID: {row[0]}, Название: {row[1]}, Обжарка: {row[2]}, " \
                              f"Тип: {row[3]}, Вкус: {row[4]}, Цена: {row[5]}, Объем: {row[6]}"
                self.coffee_list.addItem(coffee_info)

            connection.close()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CoffeeApp()
    window.setWindowTitle("Информация о кофе")
    window.resize(600, 400)
    window.show()
    sys.exit(app.exec())

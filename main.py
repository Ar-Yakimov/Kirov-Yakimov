import sqlite3
import sys

from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QListWidgetItem, QDialog


class CoffeeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('UI.ui', self)
        self.load_data_button.clicked.connect(self.load_coffee_data)
        self.add_button.clicked.connect(self.open_add_edit_form)
        self.edit_button.clicked.connect(self.edit_selected_coffee)
        self.load_coffee_data()

    def load_coffee_data(self):
        try:
            connection = sqlite3.connect('coffee.sqlite')
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM coffee")
            rows = cursor.fetchall()
            self.coffee_list.clear()
            for row in rows:
                coffee_info = f"ID: {row[0]}, Название: {row[1]}, Обжарка: {row[2]}, " \
                              f"Тип: {row[3]}, Вкус: {row[4]}, Цена: {row[5]}, Объем: {row[6]}"
                item = QListWidgetItem(coffee_info)
                item.setData(1, row[0])
                self.coffee_list.addItem(item)
            connection.close()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {e}")

    def open_add_edit_form(self, coffee_id=None):
        form = AddEditCoffeeForm(coffee_id)
        if form.exec() == QDialog.accepted:
            self.load_coffee_data()

    def edit_selected_coffee(self):
        selected_item = self.coffee_list.currentItem()
        if selected_item:
            coffee_id = selected_item.data(1)
            self.open_add_edit_form(coffee_id)
        else:
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, выберите кофе для редактирования.")


class AddEditCoffeeForm(QDialog):
    def __init__(self, coffee_id=None):
        super().__init__()
        uic.loadUi('addEditCoffeeForm.ui', self)
        self.coffee_id = coffee_id
        if coffee_id:
            self.load_coffee_data(coffee_id)
        self.saveButton.clicked.connect(self.save_coffee)

    def load_coffee_data(self, coffee_id):
        try:
            connection = sqlite3.connect('coffee.sqlite')
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM coffee WHERE id=?", (coffee_id,))
            row = cursor.fetchone()
            if row:
                self.nameLineEdit.setText(row[1])
                self.roastLevelLineEdit.setText(row[2])
                self.typeComboBox.setCurrentText(row[3])
                self.flavorDescriptionLineEdit.setText(row[4])
                self.priceLineEdit.setText(str(row[5]))
                self.packageVolumeLineEdit.setText(row[6])
            connection.close()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {e}")

    def save_coffee(self):
        name = self.nameLineEdit.text().strip()
        roast_level = self.roastLevelLineEdit.text().strip()
        coffee_type = self.typeComboBox.currentText()
        flavor_description = self.flavorDescriptionLineEdit.text().strip()

        try:
            price = float(self.priceLineEdit.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите корректное значение для цены.")
            return

        package_volume = self.packageVolumeLineEdit.text().strip()

        if not name or not roast_level or not flavor_description or not package_volume:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля.")
            return

        try:
            connection = sqlite3.connect('coffee.sqlite')
            cursor = connection.cursor()
            if self.coffee_id:
                cursor.execute("""
                    UPDATE coffee SET name=?, roast_level=?, type=?, flavor_description=?, price=?, package_volume=?
                    WHERE id=?
                """, (name, roast_level, coffee_type, flavor_description, price, package_volume, self.coffee_id))
            else:
                cursor.execute("""
                    INSERT INTO coffee (name, roast_level, type, flavor_description, price, package_volume)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (name, roast_level, coffee_type, flavor_description, price, package_volume))

            connection.commit()
            connection.close()
            QMessageBox.information(self, "Успех", "Запись успешно сохранена.")
            self.accept()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить данные: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CoffeeApp()
    window.setWindowTitle("Информация о кофе")
    window.resize(600, 400)
    window.show()
    sys.exit(app.exec())

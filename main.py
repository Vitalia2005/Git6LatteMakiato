import sys
import sqlite3
import os

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt


db = 'data/coffee.sqlite3'
TABLE_CREATE_REQUEST = '''CREATE TABLE coffee (
    id                  INTEGER        PRIMARY KEY AUTOINCREMENT
                                       UNIQUE
                                       NOT NULL,
    sort_title          TEXT           NOT NULL,
    degree_of_roasting  TEXT           NOT NULL,
    ground_or_grains    TEXT           NOT NULL,
    flavor_description  TEXT,
    price               REAL,
    volume_of_packaging REAL
);'''


def create_empty_file(full_path: str):
    full_path = full_path.replace('\\', '/')
    path = '/'.join(full_path.split('/')[:-1])
    if not os.path.isdir(path):
        os.makedirs(path)
    open(full_path, mode='w').close()


def create_database_if_need():
    if not os.path.isfile(db):
        create_empty_file(db)
        con = sqlite3.connect(db)
        cur = con.cursor()
        cur.execute(TABLE_CREATE_REQUEST)
        con.commit()
        con.close()


class CoffeeAddForm(QWidget):
    def __init__(self, main_window):
        super().__init__()
        uic.loadUi('UI/addEditCoffeeForm.ui', self)
        self.main_window = main_window
        self.submit_btn.clicked.connect(self.submit)
        self.id_box.valueChanged.connect(self.change_data)

    def change_data(self, coffee_id):
        create_database_if_need()
        con = sqlite3.connect(db)
        cur = con.cursor()
        element = cur.execute('SELECT * FROM coffee WHERE id = ?',
                              (coffee_id, )).fetchone()
        if element is not None:
            element = element[1:]
            self.sort_edit.setText(element[0])
            self.degree_edit.setText(element[1])
            self.ground_or_grains_box.setValue(element[2])
            self.flavor_edit.setText(element[3])
            self.price_box.setValue(element[4])
            self.volume_box.setValue(element[5])
        con.close()

    def submit(self):
        coffee_id = self.id_box.value()
        sort = self.sort_edit.text()
        degree = self.degree_edit.text()
        ground_or_grains = self.ground_or_grains_box.value()
        flavor = self.flavor_edit.text()
        price = self.price_box.value()
        volume = self.volume_box.value()
        create_database_if_need()
        con = sqlite3.connect(db)
        cur = con.cursor()
        if (cur.execute('SELECT id FROM coffee WHERE id = ?',
                        (coffee_id, )).fetchone() is not None):
            cur.execute('DELETE FROM coffee WHERE id = ?', (coffee_id, ))
        if coffee_id != 0:
            cur.execute('INSERT INTO coffee VALUES (?, ?, ?, ?, ?, ?, ?)',
                        (coffee_id, sort, degree, ground_or_grains,
                         flavor, price, volume))
        else:
            cur.execute('INSERT INTO coffee(sort_title,'
                        ' degree_of_roasting,'
                        ' groud_or_grains,'
                        ' flavor_description,'
                        ' price,'
                        ' volume_of_packaging) VALUES (?, ?, ?, ?, ?, ?)',
                        (sort, degree, ground_or_grains,
                         flavor, price, volume))
        con.commit()
        con.close()
        self.main_window.load_table()
        self.deleteLater()


class CoffeeMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('UI/main.ui', self)
        self.coffee_table: QTableWidget = self.coffee_table
        self.add_form = None
        self.coffee_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        self.add_edit_btn.clicked.connect(self.add_item)
        self.load_table()

    def load_table(self):
        self.coffee_table.setRowCount(0)
        create_database_if_need()
        con = sqlite3.connect(db)
        cur = con.cursor()
        data = cur.execute('SELECT * FROM coffee').fetchall()
        self.coffee_table.setRowCount(len(data))
        for i, row in enumerate(data):
            for j in range(len(row)):
                value = str(row[j])
                item = QTableWidgetItem(value)
                item.setFlags(Qt.ItemIsEnabled)
                self.coffee_table.setItem(i, j, item)
        con.close()

    def add_item(self):
        self.add_form = CoffeeAddForm(self)
        self.add_form.show()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CoffeeMainWindow()
    window.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())

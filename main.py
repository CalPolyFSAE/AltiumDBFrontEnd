import sys
import mysql.connector
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtSql import *


class Describe:
    # All of the information from describe
    def __init__(self, db):
        self.db = db
        self.field = []
        self.type = []
        self.null = []
        self.key = []
        self.default = []
        self.extra = []

    def describeTable(self, tableName):
        if self.field:
            print("Describe object already in use")
            return
        cursor = self.db.cursor()
        cursor.execute("""DESCRIBE `{}`""".format(tableName))
        results = cursor.fetchall()
        self.processResults(results)
        cursor.close()

    def processResults(self, results):
        for i in range(len(results)):
            self.field.append(results[i][0])
            self.type.append(results[i][1])
            self.null.append(results[i][2])
            self.key.append(results[i][3])
            self.default.append(results[i][4])
            self.extra.append(results[i][5])

    def __str__(self):
        result = ''
        for i in range(len(self.field)):
            result += "{field:30}{type:20}{null:10}{key:10}{default}\t{extra}\n".format(
                field=self.field[i], type=self.type[i], null=self.null[i], key=self.key[i],
                default=self.default[i], extra=self.extra[i])
        return result

class Example(QWidget):

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.initUI(db)

    def initUI(self, db):
        self.grid = QGridLayout()
        self.verticalLayout = QVBoxLayout(self)
        cursor = db.cursor()
        cursor.execute("""SHOW TABLES""")
        results = cursor.fetchall()
        self.combo = QComboBox(self)
        for result in results:
            self.combo.addItem(result[0])
        self.combo.activated[str].connect(self.addCombo)
        self.grid.addWidget(self.combo, 0, 0)
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('QComboBox')
        self.verticalLayout.addLayout(self.grid)
        self.show()
        cursor.close()

    def addCombo(self, text):
        table = Describe(self.db)
        table.describeTable(text)
        self.combo = QComboBox(self)
        self.combo.addItems(table.field)
        self.grid.addWidget(self.combo, 0,1)
    def center(self):

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def keyPressEvent(self, e):

        if e.key() == Qt.Key_Escape:
            self.close()
    def closeEvent(self, event):
        print("closing PyQTTest")
        self.db.close()

def main():
    # Creating main connection
    mydb = mysql.connector.connect(
        host="altium.cyyn3lqbjhax.us-east-2.rds.amazonaws.com",
        user="cpracing",
        passwd="formulasae",
        database="Altium"
    )

    # print(mydb)
    # a = Describe(mydb)
    # a.describeTable("Capacitor")
    # print(a)
    # b = Describe(mydb)
    # b.describeTable("Resistor")
    # print(b)
    app = QApplication(sys.argv)
    ex = Example(mydb)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

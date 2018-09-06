import sys
import mysql.connector
from PyQt5.QtWidgets import QLineEdit, QComboBox, QLabel, QWidget, QApplication, QGridLayout, QVBoxLayout,QDesktopWidget
from PyQt5.QtCore import Qt

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
        self.colCombo = []
        self.colLabel = []
        self.colLineEdit = []
        self.grid = QGridLayout()
        self.verticalLayout = QVBoxLayout(self)
        cursor = db.cursor()
        cursor.execute("""SHOW TABLES""")
        results = cursor.fetchall()
        self.tableCombo = QComboBox(self)
        self.tableLabel = QLabel(self)
        self.tableLabel.setText('Table')
        for result in results:
            self.tableCombo.addItem(result[0])
        self.tableCombo.activated[str].connect(self.showTable)
        self.grid.addWidget(self.tableCombo, 0, 1)
        self.grid.addWidget(self.tableLabel, 0, 0)
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('Altium DB')
        self.verticalLayout.addLayout(self.grid)
        self.show()
        cursor.close()

    def showTable(self, text):
        # updates all of the columns for a given table
        table = Describe(self.db)
        table.describeTable(text)
        cursor = self.db.cursor()
        cursor.execute("""SELECT * FROM `{}`""".format(text))
        results = cursor.fetchall()
        if(results):
            tResults = self.transposeResults(results)
            fResults = self.filterResults(tResults)
        for i in range(len(table.field)):
            self.addLabel(table.field[i], i+1, 0)
            self.addLineEdit(i+1, 2)
            if(results):
                # Error switching between drawer and anything else
                self.addCombo(fResults[i], i+1, 1)
            else:
                self.addCombo(['Null'], i+1, 1)
        self.removeRowsBelow(len(table.field))

    def filterResults(self, results):
        # removes duplicates
        filtered = []
        for result in results:
            filtered.append(list(dict.fromkeys(result)))
        return filtered

    def transposeResults(self, results):
        # transposes the 2d list that results holds
        transpose = []
        for i in range(len(results[0])):
            transpose.append([])
            for j in range(len(results)):
                transpose[i].append(results[j][i])
        return transpose

    def removeRowsBelow(self, yPos):
        # removes all rows below a given position from the columns
        if(len(self.colCombo)-1 > yPos):
            for i in range(yPos, len(self.colCombo)):
                self.removeRows(i)
            self.clearNones()

    def clearNones(self):
        # removes all of the nones
        self.colCombo = [x for x in self.colCombo if x]
        self.colLabel = [x for x in self.colLabel if x]
        self.colLinedEdit = [x for x in self.colLineEdit if x]

    def removeRows(self, yPos):
        # finds removes items from colLabel and colCombo at an index
        if(self.colCombo[yPos]):
            self.colCombo[yPos].deleteLater()
            self.colCombo[yPos] = None
        if(self.colLabel[yPos]):
            self.colLabel[yPos].deleteLater()
            self.colLabel[yPos] = None
        if(self.colLineEdit[yPos]):
            self.colLineEdit[yPos].deleteLater()
            self.colLineEdit[yPos] = None

    def addLineEdit(self, yPos, xPos):
        if(yPos > len(self.colLineEdit) or not self.colLineEdit[yPos - 1]):
            self.colLineEdit.append(QLineEdit(self))
            self.grid.addWidget(self.colLineEdit[-1], yPos, xPos)

    def addLabel(self, text, yPos, xPos):
        if(yPos > len(self.colLabel) or not self.colLabel[yPos-1]):
            self.colLabel.append(QLabel(self))
            self.colLabel[-1].setText(text)
            self.grid.addWidget(self.colLabel[-1], yPos, xPos)
        else:
            self.colLabel[yPos - 1].setText(text)

    def addCombo(self, text, yPos, xPos):
        if(yPos > len(self.colCombo) or not self.colCombo[yPos-1]):
            self.colCombo.append(QComboBox(self))
            for value in text:
                self.colCombo[-1].addItem(str(value))
            self.grid.addWidget(self.colCombo[-1], yPos, xPos)
        else:
            for i in range(self.colCombo[yPos - 1].count()):
                self.colCombo[yPos - 1].removeItem(0)
            text = list(map(str, text))
            self.colCombo[yPos - 1].addItems(text)

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

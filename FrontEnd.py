from PyQt5.QtWidgets import (QLineEdit, QComboBox, QLabel, QWidget, QApplication,
                             QGridLayout, QVBoxLayout, QHBoxLayout,  QDesktopWidget, QPushButton,
                             QMessageBox)
from PyQt5.QtCore import Qt
from sql import Table


class FrontEnd(QWidget):

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.initUI(db)

    def initUI(self, db):
        self.colCombo = []
        self.colLabel = []
        self.colLineEdit = []
        self.tableName = None
        self.grid = QGridLayout()
        self.verticalLayout = QVBoxLayout(self)
        cursor = db.cursor()
        cursor.execute("""SHOW TABLES""")
        results = cursor.fetchall()

        self.tableCombo = QComboBox(self)
        self.tableLabel = QLabel(self)
        self.tableLabel.setText('Table')
        self.find = QPushButton('Find', self)
        self.edit = QPushButton('Edit', self)
        self.add = QPushButton('Add', self)
        for result in results:
            self.tableCombo.addItem(result[0])
        self.tableCombo.activated[str].connect(self.showTable)
        self.showTable(results[0][0])
        self.find.clicked.connect(self.findParts)
        self.edit.clicked.connect(self.editPart)
        self.add.clicked.connect(self.addParts)
        self.grid.addWidget(self.tableCombo, 0, 1)
        self.grid.addWidget(self.tableLabel, 0, 0)
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('Altium DB')
        self.verticalLayout.addLayout(self.grid)
        self.verticalLayout.addWidget(self.find, 0, Qt.AlignBaseline)
        self.verticalLayout.addWidget(self.edit, 0, Qt.AlignBaseline)
        self.verticalLayout.addWidget(self.add, 0, Qt.AlignBaseline)
        self.show()
        cursor.close()

    def findParts(self):
        filt = ''
        if(self.colLineEdit[0].text()):
            # if someone puts in an pKey, just use that
            filt = "`{}` = '{}'".format(
                self.colLabel[0].text(), self.colLineEdit[0].text())
        else:
            for i in range(len(self.colLabel)):
                if self.colLineEdit[i].text():
                    filt += "`{}` ".format(self.colLabel[i].text())
                    if(self.colLineEdit[i].text() == 'Null'):
                        filt += "is Null"
                    else:
                        filt += "= '{}'".format(self.colLineEdit[i].text())
                    filt += " and "
                if i == len(self.colLabel)-1:
                    filt = filt[:-len(' and ')]
        self.showTable(self.tableName, filt)

    def editPart(self):
        if self.colLineEdit[0].text:
            # checking to see if there is text in the primary key
            print('edit')
        else:
            print("don't edit")

    def addParts(self):
        print('Add')

    def showTable(self, text, filt=None):
        # updates all of the columns for a given table
        self.tableName = text
        table = Table(self.db, self.tableName)
        table.describeTable()
        results = table.selectTable(filt=filt)
        if(results):
            tResults = self.transposeResults(results)
            fResults = self.filterResults(tResults)
        else:
            msg = QMessageBox()
            msg.setText(
                'Table {} has no rows that match filter {}'.format(self.tableName, filt))
            msg.exec_()
        for i in range(table.numColumns()):
            self.addLabel(table.colList[i].field, i+1, 0)
            self.addLineEdit(i+1, 2)
            if(results):
                # Error switching between drawer and anything else
                if(table.colList[i].isForeign()):
                    self.addCombo(table.colList[i].fTable.selectTable('Name'), i+1, 1)
                else:
                    self.addCombo(fResults[i], i+1, 1)
            else:
                self.addCombo(['Null'], i+1, 1)
        self.removeRowsBelow(table.numColumns())

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
            if(text[0] is not None):
                for value in text:
                    if isinstance(value, tuple) or isinstance(value, list):
                        #fixing any issues with lists
                        value = value[0]
                    self.colCombo[-1].addItem(str(value))
            else:
                self.colCombo[-1].addItem("Null")
            self.grid.addWidget(self.colCombo[-1], yPos, xPos)
            self.colCombo[-1].activated[str].connect(self.updateLine)
        else:
            for i in range(self.colCombo[yPos - 1].count()):
                self.colCombo[yPos - 1].removeItem(0)
            if(text[0] is not None):
                for value in text:
                    if isinstance(value, tuple) or isinstance(value, list):
                        #fixing any issues with lists
                        value = value[0]
                    self.colCombo[yPos - 1].addItem(str(value))
            else:
                self.colCombo[yPos - 1].addItem("Null")

    def updateLine(self, text):
        self.colLineEdit[self.colCombo.index(self.sender())].setText(text)

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

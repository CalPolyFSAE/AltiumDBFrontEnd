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
        self.table = Table(db, results[0][0])
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
            for column in self.getUserInputs():
                if column[1]:
                    # check if something was typed in for that column
                    if filt:
                        filt += ' and '  # concatenating strings
                    filt += "`{}`".format(column[0])
                    if(column[1] == 'Null'):
                        filt += "is Null"
                    else:
                        filt += "= '{}'".format(column[1])
        self.showTable(self.table.name, filt)

    def editPart(self):
        if self.colLineEdit[0].text():
            # checking to see if there is text in the primary key
            columns = self.getUserInputs()
            params = ''
            for i in range(len(columns)):
                column = columns[i]
                if column[1]:  # only edit types in parameters
                    if params:
                        params += ', '
                    params += "`{}` = '{}'".format(column[0], column[1])
            self.showTable(self.table.name)
        else:
            self.displayMsg('Cannot edit without Primary Key')

    def addParts(self):
        if not self.colLineEdit[0].text():
            # checking to see if there is text in the primary key
            columns = self.getUserInputs()
            cols = ''
            values = ''
            for i in range(len(columns)):
                column = columns[i]
                if not i:
                    primaryKey = column[0]
                    pk_id = column[1]
                else:
                    if column[1]:  # only edit types in parameters
                        if cols:
                            cols += ', '
                            values += ', '
                        cols += "`{}`".format(column[0])
                        values += "'{}'".format(column[1])
            cursor = self.db.cursor()
            stmt = """INSERT INTO `{name}` ({columns})
            VALUES ({values}); """.format(name=self.table.name, columns=cols, values=values)
            print(stmt)
            cursor.execute(stmt)
            self.db.commit()
            cursor.close()
            self.showTable(self.table.name)
        else:
            self.displayMsg(
                'Primary Key has value, remove in order to insert part')

    def getUserInputs(self):
        # returns a 2d array of all inputs
        result = []
        for i in range(self.table.numColumns()):
            columnName = self.table.colList[i].getName()
            inputText = self.colLineEdit[i].text()
            if inputText and self.table.colList[i].isForeign():
                fKeyID = self.table.colList[i].getFKeyName()
                filt = "Name = '{}'".format(inputText)
                columnValue = self.table.colList[i].fTable.selectTable(
                    col=fKeyID, filt=filt)[0][0]
            else:
                columnValue = inputText
            tmp = [columnName, columnValue]
            result.append(tmp)
        return result

    def displayMsg(self, text):
        msg = QMessageBox()
        msg.setText(text)
        msg.exec_()

    def showTable(self, text, filt=None):
        # updates all of the columns for a given table
        if(self.table.name != text):
            self.table = Table(self.db, text)
            # Regen table if it's the wrong one
        results = self.table.selectTable(filt=filt)
        # add a getTable or something that returns all of this stuff and takes advantage of the column class
        if(results):
            # TODO: Replace is select distinct
            tResults = self.transposeResults(results)
            fResults = self.filterResults(tResults)

        else:
            if(filt):
                self.displayMsg('Table {} has no rows that match filter {}'.format(
                    self.table.name, filt))
            else:
                self.displayMsg('Table {} has no rows'.format(self.table.name))
        if(not filt and not results) or results:
            for i in range(self.table.numColumns()):
                self.addLabel(self.table.colList[i].getName(), i+1, 0)
                self.addLineEdit(i+1, 2)
                if(results):
                    if(self.table.colList[i].isForeign()):
                        self.addCombo(  # Left off here, trying to select results that match fResults
                            self.table.colList[i].getFKeyVals('Name', fResults[i]), i+1, 1)
                    else:
                        self.addCombo(fResults[i], i+1, 1)
                else:
                    self.addCombo(['Null'], i+1, 1)
            self.removeRowsBelow(self.table.numColumns())

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
        else:
            self.colLineEdit[yPos - 1].setText(None)

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
                        # fixing any issues with lists
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
                        # fixing any issues with lists
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

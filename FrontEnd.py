from PyQt5.QtWidgets import (QLineEdit, QComboBox, QLabel, QWidget,
                             QGridLayout, QVBoxLayout, QPushButton,
                             QMessageBox)
from PyQt5.QtCore import Qt
from sql import Table


class FrontEnd(QWidget):
    """The main GUI class

    Arguments:
        QWidget {QWidget} -- [GUI Class]

    Returns:
        [None] -- [Nothing]
    """

    def __init__(self, db):
        """Constructor for Front End class. Creation of FrondEnd class will initialize UI

        Arguments:
            db {MySQLConnection} -- Provide a connected MySQL connection here. 
            This is used to run all of the SQL scripts
        """

        super().__init__()
        self.db = db
        self.col_combo = []  # list of input comboBoxes
        self.col_label = []  # list of column names
        self.col_line_edit = []  # list of lineedit objects
        self.table_combo = None
        self.table_label = None
        self.table = None
        self.grid = QGridLayout()
        self.vertical_layout = QVBoxLayout(self)
        self.init_ui()

    def init_ui(self):
        """Initializes UI and creates the GUI
        """
        # creating inital comboBox for table selection and buttons
        self.table_combo = QComboBox(self)
        self.table_label = QLabel(self)
        self.table_label.setText('Table')
        self.find = QPushButton('Find', self)
        self.edit = QPushButton('Edit', self)
        self.add = QPushButton('Add', self)
        self.find.clicked.connect(self.find_parts)
        self.edit.clicked.connect(self.edit_part)
        self.add.clicked.connect(self.add_parts)
        # Getting all available tables from database
        cursor = self.db.cursor()
        cursor.execute("""SHOW TABLES""")
        results = cursor.fetchall()
        cursor.close()
        # adding all tables to comboBox
        for result in results:
            self.table_combo.addItem(result[0])

        # selecting a table will call show_table with argument of tableName selected
        self.table_combo.activated[str].connect(self.show_table)
        # table object holds all of the displayed table information
        self.table = Table(self.db, results[0][0])
        self.show_table(results[0][0])
        # adding widgets to GUI
        self.grid.addWidget(self.table_combo, 0, 1)
        self.grid.addWidget(self.table_label, 0, 0)
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('Altium DB')
        self.vertical_layout.addLayout(self.grid)
        self.vertical_layout.addWidget(self.find, 0, Qt.AlignBaseline)
        self.vertical_layout.addWidget(self.edit, 0, Qt.AlignBaseline)
        self.vertical_layout.addWidget(self.add, 0, Qt.AlignBaseline)
        self.show()  # displays table

    def find_parts(self):
        """find_parts reads through the user inputs and finds all parts
        that match the search criteria, unfilled lineEdits are ignored
        null values are actively searched iff null is entered
        """

        filt = ''
        if self.col_line_edit[0].text():
            # if someone puts in an primary_keyey, just use that
            filt = "`{}` = '{}'".format(
                self.col_label[0].text(), self.col_line_edit[0].text())
        else:
            for column in self.get_user_inputs():
                if column[1]:
                    # check if something was typed in for that column
                    if filt:
                        filt += ' and '  # concatenating strings
                    filt += "`{}`".format(column[0])
                    if(column[1] == 'Null' or column[1] == 'null'):
                        filt += "is Null"
                    else:
                        filt += "= '{}'".format(column[1])
        self.show_table(self.table.name, filt)

    def edit_part(self):
        """See above documentation foor edit part. 
        This function is almost the same except that the strings are formatted differently
        We are editing a part based off of it's primary key. Because of that, it is not possible
        to edit multiple parts at once. SQL scripts are recommended to be written instead.
        Alternatively, this program can be modified
        """

        if self.col_line_edit[0].text():
            # checking to see if there is text in the primary key
            primary_key = self.col_line_edit[0].text()
            if primary_key.isdigit() and int(primary_key) > 0:
                columns = self.get_user_inputs()
                params = ''
                for i in range(len(columns)):
                    column = columns[i]
                    if column[1]:  # only edit types in parameters
                        if params:
                            params += ', '
                        params += "`{}` = '{}'".format(column[0], column[1])
                self.table.editTable(params, self.col_line_edit[0].text())
                self.show_table(self.table.name)
            else:
                self.display_msg('Primary Key must be integer > 0')
        else:
            self.display_msg('Cannot edit without Primary Key')

    def add_parts(self):
        """See above documentation. Unlike edit_parts, add_parts requires that the primary key
        be blank. This is because we assume that autoincrement is turned on. In which case, 
        providing a primary key will break the program.
        """

        if not self.col_line_edit[0].text():
            # checking to see if there is text in the primary key
            columns = self.get_user_inputs()
            cols = ''
            values = ''
            for i in range(len(columns)):
                column = columns[i]
                if column[1]:  # only edit types in parameters
                    if cols:
                        cols += ', '
                        values += ', '
                    cols += "`{}`".format(column[0])
                    values += "'{}'".format(column[1])
            cursor = self.db.cursor()
            stmt = """INSERT INTO `{name}` ({columns})
            VALUES ({values}); """.format(name=self.table.name, columns=cols, values=values)
            try:
                cursor.execute(stmt)
                self.db.commit()
            except:
                self.display_msg(
                    'An Error has occured, ensure that all NN rows are filled in')
            cursor.close()
            self.show_table(self.table.name)
        else:
            self.display_msg(
                'Primary Key has value, remove in order to insert part')

    def get_user_inputs(self):
        """get_user_inputs takes and formats all of the column inputs into a list
        It is a helper function for find, edit and add_parts. The function also takes in 
        the input text and coverts it to the primary key if given

        Returns:
            List -- result is a 2d list, the first element is name of the column, the second is the value. 
            In the future, this should be replaced with a Column object or something in the SQL file
        """

        # returns a 2d array of all inputs
        result = []
        # iterate through all columns
        for i in range(self.table.numColumns()):
            # grab column name and input_text
            column_name = self.table.colList[i].getName()
            input_text = self.col_line_edit[i].text()
            # if there is input text and the column represents a foreign key
            if input_text and self.table.colList[i].isForeign():
                # instead of returning the input_text, replace it with  the primary key of the foreign table
                # corresponding to the input_text for column Name
                f_key_id = self.table.colList[i].getFKeyName()
                filt = "Name = '{}'".format(input_text)
                column_value = self.table.colList[i].fTable.selectTable(
                    col=f_key_id, filt=filt)[0][0]
            else:
                column_value = input_text
            tmp = [column_name, column_value]
            result.append(tmp)
        return result

    def display_msg(self, text):
        """Helper function to display a message popup

        Arguments:
            text {str} -- The text that should be displayed in the message popup
        """

        msg = QMessageBox()
        msg.setText(text)
        msg.exec_()

    def show_table(self, text, filt=None):
        """show_table will update the GUI with a new or updated table. This function will first change the table,
        then run a select operation on the table with a given filter. Then the table will be regenerated. The drop down
        menus will only contain unique values to select from. Finally, the function will delete any rows that aren't needed.
        In general, the function tries to modify existing widgets instead of remaking the whole thing. If the table is empty,
        then options in the dropdown will be filled with Null. However, if the filter provides nothing, show_tables will quit

        Arguments:
            text {str} -- text is the name of the table that is to be searched. This is automatically
            filled in by the Table comboBox on selection. Otherwise, itshould be the same

        Keyword Arguments:
            filt {str} -- filt is a string in SQL syntax(TODO:Change this to take only a list) that
            describes that all SQL rows must match to be returned (default: {None})
        """

        # updates all of the columns for a given table
        if self.table.name != text:
            self.table = Table(self.db, text)
            # Regen table if it's the wrong one
        results = self.table.selectTable(filt=filt)
        # add a getTable or something that returns all of this stuff and takes advantage of the column class
        if results:
            # TODO: Replace is select distinct
            # transposes results, then selects only unique values
            t_results = self.transpose_results(results)
            f_results = self.filter_results(t_results)

        else:
            # print an error message stating that nothing could be found
            if filt:
                self.display_msg('Table {} has no rows that match filter {}'.format(
                    self.table.name, filt))
                return  # quit here to not Null out the results
            else:
                self.display_msg(
                    'Table {} has no rows'.format(self.table.name))
        # show the new table as long as there wasn't a filter that returned nothing
        for i in range(self.table.numColumns()):
            # iterate through all of the columns
            self.add_label(self.table.colList[i].getName(), i+1, 0)
            self.add_line_edit(i+1, 2)
            if results:
                # if column is foreign key, show selectable options as names of the foreign table values
                # instead of indexes
                if self.table.colList[i].isForeign():
                    self.add_combo(
                        self.table.colList[i].getFKeyVals('Name', f_results[i]), i+1, 1)
                else:
                    self.add_combo(f_results[i], i+1, 1)
            else:
                # if there aren't any options available here, then just add a Null comboBox
                self.add_combo(['Null'], i+1, 1)
        self.s(self.table.numColumns())

    def filter_results(self, results):
        """Takes in a list and filters out all non-unique results

        Arguments:
            results {list(list(str))} -- A 2dlist of strings

        Returns:
            list -- results where the str lists are only unique values
        """

        filtered = []
        for result in results:
            filtered.append(list(dict.fromkeys(result)))
        return filtered

    def transpose_results(self, results):
        """Changes a list of rows with column data to a list of columns with row data.
        This aids with finding unqieu row results

        Arguments:
            results {list(list(str))} -- A list of rows with column information

        Returns:
            list(list(str)) -- A list of columns with row information
        """

        transpose = []
        for i in range(len(results[0])):
            transpose.append([])
            for j in range(len(results)):
                transpose[i].append(results[j][i])
        return transpose

    def remove_rows_below(self, yPos):
        """removes all rows from the GUI and the column lists that are below a given position

        Arguments:
            yPos {int} -- The position to start removing rows from
        """

        if len(self.col_combo)-1 > yPos:
            for i in range(yPos, len(self.col_combo)):
                self.remove_row(i)
            # clear all of Nones created by remove_row
            self.col_combo = [x for x in self.col_combo if x]
            self.col_label = [x for x in self.col_label if x]
            self.col_line_edit = [x for x in self.col_line_edit if x]

    def remove_row(self, yPos):
        """A helper function for remove_rows_below. Takes in a y position and 
        removes the entire row from the GUI through deleteLater as well as deleting the object

        Arguments:
            yPos {int} -- The position of the row to be deleted
        """

        if self.col_combo[yPos]:
            self.col_combo[yPos].deleteLater()
            self.col_combo[yPos] = None
        if self.col_label[yPos]:
            self.col_label[yPos].deleteLater()
            self.col_label[yPos] = None
        if self.col_line_edit[yPos]:
            self.col_line_edit[yPos].deleteLater()
            self.col_line_edit[yPos] = None

    def add_line_edit(self, yPos, xPos):
        if(yPos > len(self.col_line_edit) or not self.col_line_edit[yPos - 1]):
            self.col_line_edit.append(QLineEdit(self))
            self.grid.addWidget(self.col_line_edit[-1], yPos, xPos)
        else:
            self.col_line_edit[yPos - 1].setText(None)

    def add_label(self, text, yPos, xPos):
        if(yPos > len(self.col_label) or not self.col_label[yPos-1]):
            self.col_label.append(QLabel(self))
            self.col_label[-1].setText(text)
            self.grid.addWidget(self.col_label[-1], yPos, xPos)
        else:
            self.col_label[yPos - 1].setText(text)

    def add_combo(self, text, yPos, xPos):
        if(yPos > len(self.col_combo) or not self.col_combo[yPos-1]):
            self.col_combo.append(QComboBox(self))
            if text[0] is not None:
                for value in text:
                    if isinstance(value, (list, tuple)):
                        # fixing any issues with lists
                        value = value[0]
                    self.col_combo[-1].addItem(str(value))
            else:
                self.col_combo[-1].addItem("Null")
            self.grid.addWidget(self.col_combo[-1], yPos, xPos)
            self.col_combo[-1].activated[str].connect(self.update_line)
        else:
            for i in range(self.col_combo[yPos - 1].count()):
                self.col_combo[yPos - 1].removeItem(0)
            if text[0] is not None:
                for value in text:
                    if isinstance(value, tuple) or isinstance(value, list):
                        # fixing any issues with lists
                        value = value[0]
                    self.col_combo[yPos - 1].addItem(str(value))
            else:
                self.col_combo[yPos - 1].addItem("Null")

    def update_line(self, text):
        self.col_line_edit[self.col_combo.index(self.sender())].setText(text)

    def keyPressEvent(self, e):
        """Handles keyPresses. Currently, typing escape will close the program

        Arguments:
            e {Event?} -- not sure what this is
        """

        if e.key() == Qt.Key_Escape:
            self.close()

    def closeEvent(self, event):
        print("closing PyQTTest")
        self.db.close()

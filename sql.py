import mysql.connector


class Table:
    def __init__(self, db, name):
        self.db = db
        self.name = name
        self.colList = []
        self.describeTable()

    def setName(self, name):
        self.name = name

    def selectTable(self, col=None, filt=None):
        cursor = self.db.cursor()
        text = "SELECT "
        if col:
            text += "{}".format(col)
        else:
            text += "*"
        text += " FROM `{}` ".format(self.name)
        if filt:
            text += "WHERE {};".format(filt)
        cursor.execute(text)
        results = cursor.fetchall()
        cursor.close()
        # convert all to strings
        return results

    def describeTable(self):
        cursor = self.db.cursor()
        cursor.execute("""DESCRIBE `{}`""".format(self.name))
        results = cursor.fetchall()
        cursor.close()
        for result in results:
            self.colList.append(Column(result, self.name, self.db))

    def numColumns(self):
        return len(self.colList)

    def getPrimaryKey(self):
        for column in self.colList:
            if column.isPrimary():
                return column.field

    def editTable(self, params, pk_id):
        cursor = self.db.cursor()
        stmt = """UPDATE `{tableName}`
                    SET {params}
                    WHERE {primaryKey} = {pk_id}; """.format(tableName=self.name, params=params, primaryKey=self.getPrimaryKey(), pk_id=pk_id)
        cursor.execute(stmt)
        self.db.commit()
        cursor.close()


class Column:
    def __init__(self, result, tableName, db):
        # intended to take information from Describe Table
        self.db = db
        self.field = result[0]
        self.type = result[1]
        self.null = result[2]
        self.key = result[3]
        self.default = result[4]
        self.extra = result[5]
        self.tableName = tableName
        if self.isForeign():
            # changing class to foreign key if it is one
            self.__class__ = Foreign_Key
            self.getForeignTable()

    def isForeign(self):
        # checks if column is a foreign key
        return self.key == "MUL"

    def isPrimary(self):
        # checks if column is the primary key
        return self.key == "PRI"

    def isNullable(self):
        return self.null == "YES"

    def getName(self):
        return self.field


class Foreign_Key(Column):
    def __init__(self, result, tableName, db):
        super().__init__(result, tableName, db)
        self.fTable = None

    def getForeignTable(self):
        # returns a table object of the table the foreign key points to
        if not self.isForeign():
            # print("Column {} is not a foreign key".format(self.field))
            return None
        prev = self.db.database
        self.db.database = "information_schema"  # search the information schema
        cursor = self.db.cursor()
        cursor.execute("""SELECT REFERENCED_TABLE_NAME FROM key_column_usage WHERE TABLE_NAME = "{}" and COLUMN_NAME = "{}"; """.format(
            self.tableName, self.field))
        result = cursor.fetchall()[0][0]
        self.db.database = prev  # set database back to what it was
        self.fTable = Table(self.db, result)  # only expecting one result
        cursor.close()

    def getFKeyName(self):
        # returns the name of the foreign key that is being pointed to
        return self.fTable.getPrimaryKey()

    def getFKeyVals(self, columnName, ids):
        # returns an array of all values from column matching id and name
        tmp = ""  # rename this
        for num in ids:
            # create string of ids
            if tmp:
                tmp += ', '
            tmp += "'{}'".format(num)
        stmt = "{fkName} in ({tmp})".format(fkName=self.getFKeyName(), tmp=tmp)
        results = self.fTable.selectTable(col=columnName, filt=stmt)
        return results

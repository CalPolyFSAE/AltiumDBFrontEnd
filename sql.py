import mysql.connector


class Table:
    def __init__(self, db, tableName):
        self.db = db
        self.tableName = tableName
        self.colList = []

    def setTableName(self, tableName):
        self.tableName = tableName

    def selectTable(self, col=None, filt=None):
        cursor = self.db.cursor()
        text = "SELECT "
        if col:
            text += "{}".format(col)
        else:
            text += "*"
        text += " FROM `{}` ".format(self.tableName)
        if(filt):
            text += "WHERE {};".format(filt)
        cursor.execute(text)
        results = cursor.fetchall()
        cursor.close()
        return results

    def describeTable(self):
        cursor = self.db.cursor()
        cursor.execute("""DESCRIBE `{}`""".format(self.tableName))
        results = cursor.fetchall()
        cursor.close()
        for result in results:
            self.colList.append(Column(result, self.tableName, self.db))
            if(self.colList[-1].isForeign()):
                self.colList[-1].getForeignTable()

    def numColumns(self):
        return len(self.colList)


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
        self.fTable = None
    def isForeign(self):
        # checks if column is a foreign key
        return self.key == "MUL"

    def isPrimary(self):
        # checks if column is the primary key
        return self.key == "PRI"

    def isNullable(self):
        return self.null == "YES"

    def getForeignTable(self):
        # returns a table object of the table the foreign key points to
        if not self.isForeign():
            # print("Column {} is not a foreign key".format(self.field))
            return None
        # mydb = mysql.connector.connect(
        #     host="altium.cyyn3lqbjhax.us-east-2.rds.amazonaws.com",
        #     user="cpracing",
        #     passwd="formulasae",
        #     database="information_schema"
        # )
        prev = self.db.database
        self.db.database = "information_schema"  # search the information schema
        cursor = self.db.cursor()
        cursor.execute("""SELECT REFERENCED_TABLE_NAME FROM key_column_usage WHERE TABLE_NAME = "{}" and COLUMN_NAME = "{}"; """.format(
            self.tableName, self.field))
        self.fTable = Table(self.db,cursor.fetchall()[0][0])  # only expecting one result
        self.db.database = prev  # set database back to what it was
        self.fTable.describeTable()
        cursor.close()

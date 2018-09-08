class Table:
    def __init__(self, db, tableName):
        self.db = db
        self.tableName = tableName

    def setTableName(self, tableName):
        self.tableName = tableName


class Describe(Table):
    # All of the information from describe
    def __init__(self, db, tableName):
        super().__init__(db, tableName)
        self.field = []
        self.type = []
        self.null = []
        self.key = []
        self.default = []
        self.extra = []
        self.describeTable()

    def describeTable(self):
        if self.field:
            print("Describe object already in use")
            return
        cursor = self.db.cursor()
        cursor.execute("""DESCRIBE `{}`""".format(self.tableName))
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


class Select(Table):
    def __init__(self, db, tableName):
        super().__init__(db, tableName)

    def selectTable(self, col=None, filt=None):
        cursor = self.db.cursor()
        text = "SELECT "
        if(col):
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

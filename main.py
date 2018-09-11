import sys
import mysql.connector
from PyQt5.QtWidgets import QApplication
from FrontEnd import FrontEnd
import datetime

def main():
    # Creating main connection
    mydb = mysql.connector.connect(
        host="altium.cyyn3lqbjhax.us-east-2.rds.amazonaws.com",
        user="cpracing",
        passwd="formulasae",
        database="Altium"
    )
    app = QApplication(sys.argv)
    ex = FrontEnd(mydb)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

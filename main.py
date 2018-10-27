import sys
import mysql.connector
from PyQt5.QtWidgets import QApplication
from FrontEnd import FrontEnd
import Converter

def main():
    """The main function. Establishes a database connection, then initiates the GUI
    """

    # Creating main connection
    mydb = mysql.connector.connect(
        converter_class=Converter.MyConverter,
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

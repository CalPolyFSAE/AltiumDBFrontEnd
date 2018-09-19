# AltiumDBFrontEnd
How to install:
    First, assuming you have Python 3.6 or 3.7 installed (NOTE: must add python to PATH, otherwise you won't be able to use python commands in command prompt), you must install all of the required packages. The first package to install is PyQt5
    by calling **pip3 install PyQt5**.(might have to run pip3.exe under python installation folder for access to pip3 commands)
    Next, you will need the mySQL connector for Python, call **pip install mysql-connector-python** from a python terminal
How to use:
    To run the program, call python main.py while in this folder from the command terminal. You should also be able to double click on the main.py file. After some time, you will see the main GUI. At the very top is the table selector selecting any table from the drop-down menu will change the table. This may take some time to occur. Currently, there are three columns. The first column describes which table column you are looking at. The next column will display a drop down menu of the unique values that the table currently holds. Selecting a value from the drop down menu will insert it into the final column, the user input column. The final column is for user input to manipulate a column.

    A special note, there are foreign keys in the database, basically, they are numbers that correspond to information from another table. I have implemented the feature to show and accept the name of a row from the foreign table instead of an id to make editing and adding information to a table easier. The row that is being edited will actually hold the id and not the name.

    At the bottom, there are three buttons: find, edit, add. These buttons operate off of the user input column. 
        Find can be used at any time. Clicking the find button after typing anything in the user input columns will change the drop down menus to only show unique values of parts that having matching parameters to the input columns

        Edit can only be used when the primary key is filled in on the user input column. This was chosen intentionally to prevent people from accidentally modifying the entire table. Once a value is filled into the primary key, clicking the edit button will cause that particular part to have all other filled in columns to take on the user input column's value. Any blank columns will be ignored. If you want to clear a column, type in Null into the user input column. This was done to make it easier for users to modify singular parts of tables.

        Add will only work if the primary key is blank. Primary keys are designed to increment on their own. This prevents the database from having out of order primary keys being added and messing it up. Add will generate a new part in the shown table with parameters equal to all of the values in the user input columns. In the event that a row has no value, then the default value for the table will be used, which is typically Null. If you want the value to specifically be Null for sure, type in Null to the column.

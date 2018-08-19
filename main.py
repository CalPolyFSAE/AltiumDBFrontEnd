import mysql.connector


def main():
    # Creating main connection
    mydb = mysql.connector.connect(
        host="altium.cyyn3lqbjhax.us-east-2.rds.amazonaws.com",
        user="cpracing",
        passwd="formulasae",
        database="Altium"
    )
    print(mydb)
    mydb.close()
    a=mydb.num_rows
    print(1)
    
if __name__ == "__main__":
    main()

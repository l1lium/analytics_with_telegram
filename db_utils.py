import pandas as pd
from sqlalchemy import create_engine
import mysql.connector


# Replace these values with your actual MySQL database credentials
hostname= '127.0.0.1'
port='3306'
database= "new_db"
username= "admin"
password= "admin"
table= "info"

# Establish a connection to the MySQL server
connection = mysql.connector.connect(
    host=hostname,
    user=username,
    password=password,
    database=database
)


def read_db():
    # Define your SQL query to fetch data from the database
    sql_query = 'SELECT * FROM new_db.info'

    # Read data from the database into a Pandas DataFrame
    df = pd.read_sql(sql_query, connection)

    # Close the connection
    connection.close()

    # Display the DataFrame
    # print(df)

    return df


def create_db():
    df = pd.read_csv('data.csv')
    df1 = df[["patientid", "age", "gender", "chestpain", "restingBP"]]

    try:
        mydb = mysql.connector.connect(
            host='127.0.0.1',
            port='3306',
            user="admin",
            password="admin",
            database="new_db"
        )
        print("Connection established")
        cursor = mydb.cursor()
        cursor.execute("create database if not exists new_db")
        mydb.commit()
        print("Database created successfully")
        cursor.execute("use new_db")

    except mysql.connector.Error as err:
        print("An error occurred:", err)

    engine = create_engine("mysql+pymysql://{user}:{pw}@{host}:{port}/{db}".format(user=username, pw=password, host=hostname, port=port, db=database))

    # creating table
    df1.to_sql('info', engine, if_exists='replace', index=False)
    print(65, cursor.execute("use new_db"))

if __name__ == "__main__":
   create_db()
    
   # df_sql = pd.read_sql('SELECT * from patients', con=engine)
   # print(68, df_sql)



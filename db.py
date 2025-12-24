import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Adetom1wa.",
        database="bincomphptest"
    )

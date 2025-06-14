import mysql.connector

def conectar_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="CFOP.D3l1a#",
        database="mercaduca"
    )

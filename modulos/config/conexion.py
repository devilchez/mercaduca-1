import mysql.connector
from mysql.connector import Error

def obtener_conexion():
    try:
        conexion = mysql.connector.connect(
            host='budyatsrezya80loqpsv-mysql.services.clever-cloud.com',          
            user='ugu7boqyhnkemf1dtu',
            password='3A57rTKfGrjUsSzuLQWd',
            database='budyatsrezya80loqpsv',
            port=3306               
        )
        if conexion.is_connected():
            print("Conexión exitosa a la base de datos")
            return conexion
    except Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

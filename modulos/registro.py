import mysql.connector

def registrar_emprendedor(nombre, apellido, correo, telefono, emprendimiento):
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",           # cambia si tienes otro usuario
            password="",           # cambia si tienes contraseña
            database="nombre_de_tu_base"  # cambia por tu base real
        )

        cursor = conexion.cursor()
        sql = """
            INSERT INTO registro (nombre, apellido, correo, telefono, emprendimiento)
            VALUES (%s, %s, %s, %s, %s)
        """
        valores = (nombre, apellido, correo, telefono, emprendimiento)
        cursor.execute(sql, valores)
        conexion.commit()

        print("✅ Emprendedor registrado correctamente")
    except Exception as e:
        print("❌ Error al registrar:", e)
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()

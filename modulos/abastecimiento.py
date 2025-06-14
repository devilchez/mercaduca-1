import streamlit as st
from config.conexion import conectar_db

def mostrar_abastecimiento(usuario):
    st.header("Registrar abastecimiento")
    con = conectar_db()
    cursor = con.cursor()

    cursor.execute("SELECT ID_Emprendimiento FROM EMPRENDIMIENTO WHERE Nombre_emprendedor = %s", (usuario,))
    emp = cursor.fetchone()

    if not emp:
        st.error("No se encontró emprendimiento para este usuario")
        return

    id_emprendimiento = emp[0]
    nombre = st.text_input("Nombre del producto")
    descripcion = st.text_area("Descripción")
    precio = st.number_input("Precio", min_value=0.01)
    cantidad = st.number_input("Cantidad a ingresar", min_value=1)
    tipo = st.text_input("Tipo de producto")

    if st.button("Registrar"):
        cursor.execute("INSERT INTO PRODUCTO (Nombre_producto, Descripcion, Precio, Tipo_producto, ID_Emprendimiento) VALUES (%s, %s, %s, %s, %s)",
                       (nombre, descripcion, precio, tipo, id_emprendimiento))
        id_producto = cursor.lastrowid
        cursor.execute("INSERT INTO ABASTECIMIENTO (ID_Emprendimiento, ID_Producto, Cantidad, Fecha_ingreso) VALUES (%s, %s, %s, NOW())",
                       (id_emprendimiento, id_producto, cantidad))
        cursor.execute("INSERT INTO INVENTARIO (ID_Producto, Cantidad_ingresada, Stock, Fecha_ingreso) VALUES (%s, %s, %s, NOW())",
                       (id_producto, cantidad, cantidad))
        con.commit()
        st.success("Producto ingresado al inventario")

    con.close()

import streamlit as st 
from modulos.config.conexion import obtener_conexion

def mostrar_abastecimiento(usuario):
    st.header("Registrar abastecimiento")

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Obtener lista de emprendedores desde la base de datos
        cursor.execute("SELECT ID_Emprendimiento, Nombre_emprendedor FROM EMPRENDIMIENTO")
        emprendedores = cursor.fetchall()

        if not emprendedores:
            st.warning("No hay emprendedores registrados en la base de datos.")
            return

        opciones = {nombre: emp_id for emp_id, nombre in emprendedores}

        # Mostrar lista desplegable para seleccionar al emprendedor
        seleccionado = st.selectbox("Selecciona un emprendedor", list(opciones.keys()))

        # Obtener ID del emprendedor seleccionado
        id_emprendimiento = opciones[seleccionado]

        # Formulario de ingreso
        nombre = st.text_input("Nombre del producto", key="nombre_producto")
        descripcion = st.text_area("Descripción", key="descripcion_producto")0
        precio = st.number_input("Precio", min_value=0.01, key="precio_producto")
        cantidad = st.number_input("Cantidad a ingresar", min_value=1, key="cantidad_producto")
        tipo = st.text_input("Tipo de producto", key="tipo_producto")


        if st.button("Registrar"):
            # Insertar en PRODUCTO
            cursor.execute(
                "INSERT INTO PRODUCTO (Nombre_producto, Descripcion, Precio, Tipo_producto, ID_Emprendimiento) VALUES (%s, %s, %s, %s, %s)",
                (nombre, descripcion, precio, tipo, id_emprendimiento)
            )
            id_producto = cursor.lastrowid

            # Insertar en ABASTECIMIENTO
            cursor.execute(
                "INSERT INTO ABASTECIMIENTO (ID_Emprendimiento, ID_Producto, Cantidad, Fecha_ingreso) VALUES (%s, %s, %s, NOW())",
                (id_emprendimiento, id_producto, cantidad)
            )

            # Insertar en INVENTARIO
            cursor.execute(
                "INSERT INTO INVENTARIO (ID_Producto, Cantidad_ingresada, Stock, Fecha_ingreso) VALUES (%s, %s, %s, NOW())",
                (id_producto, cantidad, cantidad)
            )

            con.commit()
            st.success("Producto ingresado al inventario correctamente")

    except Exception as e:
        st.error(f"Error al acceder a la base de datos: {e}")

    finally:
        cursor.close()
        con.close()


        # Formulario de ingreso
        nombre = st.text_input("Nombre del producto")
        descripcion = st.text


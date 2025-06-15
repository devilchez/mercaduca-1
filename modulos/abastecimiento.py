import streamlit as st 
from modulos.config.conexion import obtener_conexion

def mostrar_abastecimiento(usuario):
    st.header("Registrar abastecimiento")

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Obtener lista de emprendedores
        cursor.execute("SELECT ID_Emprendimiento, Nombre_emprendedor FROM EMPRENDIMIENTO")
        emprendedores = cursor.fetchall()

        if not emprendedores:
            st.warning("No hay emprendedores registrados.")
            return

        # Diccionario {nombre: id}
        opciones = {nombre: emp_id for emp_id, nombre in emprendedores}
        seleccionado = st.selectbox("Selecciona un emprendedor", list(opciones.keys()), key="emprendedor_select")
        id_emprendimiento = opciones[seleccionado]

        # Obtener productos con su precio
        cursor.execute("SELECT Nombre_producto, Precio FROM PRODUCTO WHERE ID_Emprendimiento = %s", (id_emprendimiento,))
        productos_data = cursor.fetchall()

        if not productos_data:
            st.warning("Este emprendedor aún no tiene productos registrados.")
            return

        productos = [row[0] for row in productos_data]
        producto_seleccionado = st.selectbox("Selecciona el producto", productos, key="nombre_producto")

        # Buscar precio del producto seleccionado
        precio_unitario = next((precio for nombre, precio in productos_data if nombre == producto_seleccionado), 0)

        # Mostrar precio unitario (solo lectura)
        st.markdown(f"**Precio unitario:** ${precio_unitario:.2f}")

        cantidad = st.selectbox("Cantidad a ingresar", list(range(1, 101)), key="cantidad_producto")

        # Calcular y mostrar el precio total
        precio_total = precio_unitario * cantidad
        st.markdown(f"**Precio total:** ${precio_total:.2f}")

        tipo = st.text_input("Tipo de producto", key="tipo_producto")
        descripcion = st.text_area("Descripción del producto", key="descripcion_producto")

        if st.button("Registrar"):
            # Insertar producto (puedes omitir si ya existen y solo registrar abastecimiento)
            cursor.execute(
                "INSERT INTO PRODUCTO (Nombre_producto, Descripcion, Precio, Tipo_producto, ID_Emprendimiento) VALUES (%s, %s, %s, %s, %s)",
                (producto_seleccionado, descripcion, precio_unitario, tipo, id_emprendimiento)
            )
            id_producto = cursor.lastrowid

            cursor.execute(
                "INSERT INTO ABASTECIMIENTO (ID_Emprendimiento, ID_Producto, Cantidad, Fecha_ingreso) VALUES (%s, %s, %s, NOW())",
                (id_emprendimiento, id_producto, cantidad)
            )

            cursor.execute(
                "INSERT INTO INVENTARIO (ID_Producto, Cantidad_ingresada, Stock, Fecha_ingreso) VALUES (%s, %s, %s, NOW())",
                (id_producto, cantidad, cantidad)
            )

            con.commit()
            st.success("Producto registrado exitosamente en inventario.")

    except Exception as e:
        st.error(f"Error al registrar: {e}")

    finally:
        cursor.close()
        con.close()


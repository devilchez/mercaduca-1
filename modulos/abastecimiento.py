import streamlit as st
from modulos.config.conexion import obtener_conexion

def mostrar_abastecimiento(usuario):
    st.header("Registrar abastecimiento")

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Obtener lista de emprendimientos
        cursor.execute("SELECT ID_Emprendimiento, Nombre_emprendimiento FROM EMPRENDIMIENTO")
        emprendedores = cursor.fetchall()

        if not emprendedores:
            st.warning("No hay emprendimientos registrados.")
            return

        opciones = {nombre: emp_id for emp_id, nombre in emprendedores}
        lista_emprendedores = list(opciones.keys())

        # Estado persistente del emprendedor seleccionado
        if "select_emprendedor" not in st.session_state or st.session_state["select_emprendedor"] not in lista_emprendedores:
            st.session_state["select_emprendedor"] = lista_emprendedores[0]

        index_emprendedor = lista_emprendedores.index(st.session_state["select_emprendedor"])
        emprendedor = st.selectbox("Selecciona un emprendedor", lista_emprendedores, index=index_emprendedor, key="select_emprendedor")

        # Reset si cambia el emprendedor
        if emprendedor != st.session_state.get("select_emprendedor_previo", None):
            st.session_state["producto_actual"] = None
            st.session_state["select_emprendedor_previo"] = emprendedor

        id_emprendimiento = opciones[emprendedor]

        # Obtener productos del emprendedor
        cursor.execute("SELECT Nombre_producto, Precio FROM PRODUCTO WHERE ID_Emprendimiento = %s", (id_emprendimiento,))
        productos_data = cursor.fetchall()

        productos = [row[0] for row in productos_data]
        if not productos:
            st.warning("Este emprendedor aún no tiene productos registrados.")
            return

        if st.session_state.get("producto_actual") not in productos:
            st.session_state["producto_actual"] = productos[0]

        index_producto = productos.index(st.session_state["producto_actual"])
        producto_seleccionado = st.selectbox("Selecciona el producto", productos, index=index_producto, key="producto_actual")

        # Precio unitario
        precio_unitario = next((precio for nombre, precio in productos_data if nombre == producto_seleccionado), 0)
        st.markdown(f"**Precio unitario:** ${precio_unitario:.2f}")

        # Cantidad a ingresar (number_input)
        cantidad = st.number_input("Cantidad a ingresar", min_value=1, max_value=1000, step=1, key="cantidad_producto")
        st.markdown(f"**Precio total:** ${precio_unitario * cantidad:.2f}")

        # Obtener ID_Producto existentes del producto seleccionado y emprendimiento
        cursor.execute("""
            SELECT ID_Producto
            FROM PRODUCTO
            WHERE Nombre_producto = %s AND ID_Emprendimiento = %s
        """, (producto_seleccionado, id_emprendimiento))
        id_productos_disponibles = [row[0] for row in cursor.fetchall()]

        if not id_productos_disponibles:
            st.warning("No hay IDs registrados aún para este producto.")
            id_producto = st.text_input("Ingresa un nuevo ID de producto (ej. P005)")
        else:
            id_producto = st.selectbox("Selecciona el ID del producto", id_productos_disponibles)

        # Botón para registrar
        if st.button("Registrar"):
            # Validación mínima
            if not id_producto or not tipo:
                st.error("Por favor, completa todos los campos requeridos.")
                return

            # Insertar en PRODUCTO
            cursor.execute("""
                INSERT INTO PRODUCTO (ID_Producto, Nombre_producto, Descripcion, Precio, Tipo_producto, ID_Emprendimiento)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (id_producto, producto_seleccionado, descripcion, precio_unitario, tipo, id_emprendimiento))

            # Insertar en ABASTECIMIENTO
            cursor.execute("""
                INSERT INTO ABASTECIMIENTO (ID_Emprendimiento, ID_Producto, Cantidad, Fecha_ingreso)
                VALUES (%s, %s, %s, NOW())
            """, (id_emprendimiento, id_producto, cantidad))

            # Insertar en INVENTARIO
            cursor.execute("""
                INSERT INTO INVENTARIO (ID_Producto, Cantidad_ingresada, Stock, Fecha_ingreso)
                VALUES (%s, %s, %s, NOW())
            """, (id_producto, cantidad, cantidad))

            con.commit()
            st.success("Producto registrado exitosamente en inventario.")

    except Exception as e:
        st.error(f"Error al registrar: {e}")

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'con' in locals(): con.close()

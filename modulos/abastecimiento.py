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

        if "select_emprendedor" not in st.session_state or st.session_state["select_emprendedor"] not in lista_emprendedores:
            st.session_state["select_emprendedor"] = lista_emprendedores[0]

        index_emprendedor = lista_emprendedores.index(st.session_state["select_emprendedor"])
        emprendedor = st.selectbox("Selecciona un emprendedor", lista_emprendedores, index=index_emprendedor, key="select_emprendedor")

        if emprendedor != st.session_state.get("select_emprendedor_previo", None):
            st.session_state["producto_actual"] = None
            st.session_state["select_emprendedor_previo"] = emprendedor

        id_emprendimiento = opciones[emprendedor]

        # Obtener productos con sus ID y precio
        cursor.execute("SELECT ID_Producto, Nombre_producto, Precio FROM PRODUCTO WHERE ID_Emprendimiento = %s", (id_emprendimiento,))
        productos_data = cursor.fetchall()

        if not productos_data:
            st.warning("Este emprendedor aún no tiene productos registrados.")
            return

        nombres_productos = [row[1] for row in productos_data]

        if st.session_state.get("producto_actual") not in nombres_productos:
            st.session_state["producto_actual"] = nombres_productos[0]

        index_producto = nombres_productos.index(st.session_state["producto_actual"])
        producto_seleccionado = st.selectbox("Selecciona el producto", nombres_productos, index=index_producto, key="producto_actual")

        # Obtener ID y precio del producto seleccionado
        producto_info = next((row for row in productos_data if row[1] == producto_seleccionado), None)
        if not producto_info:
            st.error("No se pudo encontrar el producto seleccionado.")
            return

        id_producto = producto_info[0]
        precio_unitario = producto_info[2]

        # Mostrar el código automáticamente
        st.markdown(f"**Código del producto:** `{id_producto}`")
        st.markdown(f"**Precio unitario:** ${precio_unitario:.2f}")

        # Cantidad con botones +/-
        cantidad = st.number_input("Cantidad a ingresar", min_value=1, max_value=1000, step=1, key="cantidad_producto")
        st.markdown(f"**Precio total:** ${precio_unitario * cantidad:.2f}")

        # Tipo y descripción (opcional)
        tipo = st.text_input("Tipo de producto (opcional)", key="tipo_producto")
        descripcion = st.text_area("Descripción del producto (opcional)", key="descripcion_producto")

        if st.button("Registrar"):
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
            st.success("Abastecimiento registrado exitosamente.")

    except Exception as e:
        st.error(f"Error al registrar: {e}")

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'con' in locals(): con.close()


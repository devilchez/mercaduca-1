import streamlit as st 
from modulos.config.conexion import obtener_conexion

def mostrar_abastecimiento(usuario):
    st.header("Registrar abastecimiento")

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Obtener lista de emprendedores
        cursor.execute("SELECT ID_Emprendimiento, Nombre_emprendimiento FROM EMPRENDIMIENTO")
        emprendedores = cursor.fetchall()

        if not emprendedores:
            st.warning("No hay emprendimientos registrados.")
            return

        opciones = {nombre: emp_id for emp_id, nombre in emprendedores}
        lista_emprendedores = list(opciones.keys())

        # Inicializar o mantener emprendedor seleccionado
        if "select_emprendedor" not in st.session_state or st.session_state["select_emprendedor"] not in lista_emprendedores:
            st.session_state["select_emprendedor"] = lista_emprendedores[0]

        # Mostrar selectbox emprendedores
        index_emprendedor = lista_emprendedores.index(st.session_state["select_emprendedor"])
        emprendedor = st.selectbox("Selecciona un emprendedor", lista_emprendedores, index=index_emprendedor, key="select_emprendedor")

        # Si cambió el emprendedor, limpiar producto_actual para que se recalcule la lista
        if emprendedor != st.session_state.get("select_emprendedor_previo", None):
            st.session_state["producto_actual"] = None  # forzar reset producto
            st.session_state["select_emprendedor_previo"] = emprendedor  # guardar el actual

        id_emprendimiento = opciones[emprendedor]

        # Cargar productos SOLO si emprendedor está seleccionado y producto_actual está None o inválido
        cursor.execute("SELECT Nombre_producto, Precio FROM PRODUCTO WHERE ID_Emprendimiento = %s", (id_emprendimiento,))
        productos_data = cursor.fetchall()

        if not productos_data:
            st.warning("Este emprendedor aún no tiene productos registrados.")
            return

        productos = [row[0] for row in productos_data]

        # Si producto_actual no está definido o no está en la lista, poner primero por defecto
        if st.session_state.get("producto_actual") not in productos:
            st.session_state["producto_actual"] = productos[0]

        # Mostrar selectbox productos con índice seguro
        index_producto = productos.index(st.session_state["producto_actual"])
        producto_seleccionado = st.selectbox("Selecciona el producto", productos, index=index_producto, key="producto_actual")

        # Buscar precio del producto seleccionado
        precio_unitario = next((precio for nombre, precio in productos_data if nombre == producto_seleccionado), 0)

        st.markdown(f"**Precio unitario:** ${precio_unitario:.2f}")

        # Cantidad con persistencia
        if "cantidad_producto" not in st.session_state:
            st.session_state["cantidad_producto"] = 1
            
        cantidad = st.number_input("Cantidad a ingresar", min_value=1, max_value=1000, value=st.session_state.get("cantidad_producto", 1), step=1, key="cantidad_producto")

        precio_total = precio_unitario * cantidad
        st.markdown(f"**Precio total:** ${precio_total:.2f}")

        # Inputs de texto con persistencia por key
        tipo = st.text_input("Tipo de producto", key="tipo_producto")
        descripcion = st.text_area("Descripción del producto", key="descripcion_producto")

        if st.button("Registrar"):
            # Insertar producto
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

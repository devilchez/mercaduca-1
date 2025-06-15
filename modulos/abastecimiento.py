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
        lista_emprendedores = list(opciones.keys())

        # Inicializar la clave en session_state solo si no existe o no es válida
        if "select_emprendedor" not in st.session_state or st.session_state["select_emprendedor"] not in lista_emprendedores:
            st.session_state["select_emprendedor"] = lista_emprendedores[0]

        # Mostrar selectbox para emprendedor con índice seguro
        index_emprendedor = lista_emprendedores.index(st.session_state["select_emprendedor"])
        emprendedor = st.selectbox("Selecciona un emprendedor", lista_emprendedores, index=index_emprendedor, key="select_emprendedor")

        id_emprendimiento = opciones[emprendedor]

        # Obtener productos con su precio para el emprendedor seleccionado
        cursor.execute("SELECT Nombre_producto, Precio FROM PRODUCTO WHERE ID_Emprendimiento = %s", (id_emprendimiento,))
        productos_data = cursor.fetchall()

        if not productos_data:
            st.warning("Este emprendedor aún no tiene productos registrados.")
            return

        productos = [row[0] for row in productos_data]

        # Inicializar producto_actual si no existe o no es válido
        if "producto_actual" not in st.session_state or st.session_state["producto_actual"] not in productos:
            st.session_state["producto_actual"] = productos[0]

        # Índice seguro para producto seleccionado
        index_producto = productos.index(st.session_state["producto_actual"])

        producto_seleccionado = st.selectbox("Selecciona el producto", productos, index=index_producto, key="producto_actual")

        # Buscar precio del producto seleccionado
        precio_unitario = next((precio for nombre, precio in productos_data if nombre == producto_seleccionado), 0)

        st.markdown(f"**Precio unitario:** ${precio_unitario:.2f}")

        # Inicializar cantidad_producto si no existe
        if "cantidad_producto" not in st.session_state:
            st.session_state["cantidad_producto"] = 1

        cantidad = st.selectbox("Cantidad a ingresar", list(range(1, 101)), index=st.session_state["cantidad_producto"]-1, key="cantidad_producto")

        precio_total = precio_unitario * cantidad
        st.markdown(f"**Precio total:** ${precio_total:.2f}")

        # Los inputs de texto ya guardan estado automáticamente por key
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

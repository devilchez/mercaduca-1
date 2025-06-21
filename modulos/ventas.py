import streamlit as st
from modulos.config.conexion import obtener_conexion

def mostrar_ventas():
    st.header("Registrar venta")

    # Inicializar el estado de la sesión
    if "productos" not in st.session_state:
        st.session_state.productos = []  # Lista de productos seleccionados
        st.session_state.emprendimientos = []  # Lista de emprendimientos seleccionados

    # Conexión a la base de datos
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Cargar emprendimientos
        cursor.execute("SELECT ID_Emprendimiento, Nombre_emprendimiento FROM EMPRENDIMIENTO")
        emprendimientos = cursor.fetchall()
        emprend_dict = {nombre: id_emp for id_emp, nombre in emprendimientos}

        # Cargar productos por emprendimiento
        cursor.execute("SELECT ID_Producto, Nombre_producto, Precio, ID_Emprendimiento FROM PRODUCTO")
        productos = cursor.fetchall()
        productos_por_emprendimiento = {}
        for idp, nombre, precio, id_emp in productos:
            productos_por_emprendimiento.setdefault(id_emp, []).append((idp, nombre, precio))

        # Mostrar tipo de pago
        tipo_pago = st.selectbox("Tipo de pago", ["Efectivo", "Woompi"], key="tipo_pago")

        # Mostrar los formularios de productos por cada emprendimiento
        for i, emp_sel in enumerate(st.session_state.emprendimientos):
            st.subheader(f"🧩 Emprendimiento #{i + 1}: {emp_sel}")

            # Selección del emprendimiento
            emp_id = emprend_dict[emp_sel]
            productos_disponibles = productos_por_emprendimiento.get(emp_id, [])

            # Si no hay productos para este emprendimiento, mostrar mensaje
            if not productos_disponibles:
                st.warning(f"No hay productos disponibles para {emp_sel}.")
                continue

            # Mostrar productos disponibles para este emprendimiento
            opciones_dict = {f"{nombre}": (idp, precio) for idp, nombre, precio in productos_disponibles}
            opciones_str = list(opciones_dict.keys())

            for j in range(len(st.session_state.productos[i])):
                col1, col2 = st.columns(2)
                with col1:
                    producto_sel = st.selectbox(
                        f"Producto {j + 1}",
                        ["-- Selecciona --"] + opciones_str,
                        key=f"producto_{i}_{j}"
                    )
                with col2:
                    cantidad = st.number_input(f"Cantidad {j + 1}", min_value=1, key=f"cantidad_{i}_{j}")

                if producto_sel != "-- Selecciona --":
                    id_producto, precio_unitario = opciones_dict[producto_sel]
                    subtotal = cantidad * precio_unitario
                    st.session_state.productos[i][j] = {
                        "id_producto": id_producto,
                        "precio_unitario": precio_unitario,
                        "cantidad": cantidad,
                        "subtotal": subtotal
                    }
                    st.caption(f"🆔 Código del producto: `{id_producto}`")
                    st.markdown(f"💵 Subtotal: **${subtotal:.2f}**")

        # Total general
        total_general = sum([producto['subtotal'] for emprendimiento in st.session_state.productos for producto in emprendimiento])

        st.markdown(f"### 💰 Total general: **${total_general:.2f}**")

        # Botones para agregar productos y emprendimientos
        col1, col2 = st.columns(2)
        if col1.button("➕ Agregar otro emprendimiento"):
            st.session_state.emprendimientos.append("-- Selecciona --")
            st.session_state.productos.append([])
        if col2.button("✅ Registrar venta"):
            # Registrar la venta y los productos
            try:
                cursor.execute("INSERT INTO VENTA (Fecha_venta, Tipo_pago) VALUES (NOW(), %s)", (tipo_pago,))
                id_venta = cursor.lastrowid

                # Insertar productos en PRODUCTOXVENTA
                for emprendimiento in st.session_state.productos:
                    for producto in emprendimiento:
                        cursor.execute(
                            "INSERT INTO PRODUCTOXVENTA (id_venta, ID_Producto, Cantidad, Precio_unitario) "
                            "VALUES (%s, %s, %s, %s)",
                            (
                                id_venta,
                                producto["id_producto"],
                                producto["cantidad"],
                                producto["precio_unitario"]
                            )
                        )

                con.commit()
                st.success("✅ Venta registrada correctamente.")
                st.session_state.clear()

            except Exception as e:
                con.rollback()
                st.error(f"❌ Error al registrar venta: {e}")

    except Exception as e:
        st.error(f"❌ Error general: {e}")

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'con' in locals(): con.close()

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

        # Mostrar lista de emprendimientos solo una vez
        if not st.session_state.emprendimientos:
            emprend_sel = st.selectbox("Selecciona un emprendimiento", list(emprend_dict.keys()))
            if emprend_sel != "-- Selecciona --":
                st.session_state.emprendimientos.append(emprend_sel)
        else:
            emprend_sel = st.session_state.emprendimientos[0]  # Solo un emprendimiento por ahora

        # Cargar productos por emprendimiento
        cursor.execute("""SELECT ID_Producto, Nombre_producto, Precio, ID_Emprendimiento 
                          FROM PRODUCTO WHERE ID_Emprendimiento = %s""", (emprend_dict[emprend_sel],))
        productos = cursor.fetchall()

        productos_dict = {f"{nombre} (ID: {idp}) - ${precio:.2f}": (idp, nombre, precio) for idp, nombre, precio in productos}
        opciones_str = list(productos_dict.keys())

        # Mostrar productos disponibles para este emprendimiento
        st.markdown("### Productos a vender")

        productos_vender = []

        # Formulario de productos
        with st.form("formulario_venta", clear_on_submit=False):
            for i in range(len(st.session_state.productos)):
                st.markdown(f"#### Producto #{i+1}")
                col1, col2 = st.columns(2)
                with col1:
                    producto_sel = st.selectbox(
                        f"Producto {i+1}",
                        ["-- Selecciona --"] + opciones_str,
                        key=f"producto_{i}"
                    )
                with col2:
                    cantidad = st.number_input(f"Cantidad {i+1}", min_value=1, key=f"cantidad_{i}")

                if producto_sel != "-- Selecciona --":
                    id_producto, nombre_producto, precio_unitario = productos_dict[producto_sel]
                    subtotal = cantidad * precio_unitario
                    productos_vender.append({
                        "id_producto": id_producto,
                        "nombre_producto": nombre_producto,
                        "precio_unitario": precio_unitario,
                        "cantidad": cantidad,
                        "subtotal": subtotal
                    })
                    st.caption(f"🆔 Código del producto: `{id_producto}`")
                    st.markdown(f"💵 Subtotal: **${subtotal:.2f}**")

            # Total general de la venta
            total_general = sum([producto['subtotal'] for producto in productos_vender])
            st.markdown(f"### 💰 Total general: **${total_general:.2f}**")

            tipo_pago = st.selectbox("Tipo de pago", ["Efectivo", "Woompi"], key="tipo_pago")

            # Botones para agregar productos o registrar la venta
            col1, col2 = st.columns(2)
            if col1.button("➕ Agregar producto"):
                st.session_state.productos.append({})
            if col2.button("✅ Registrar venta"):
                if not productos_vender:
                    st.error("Debes seleccionar al menos un producto.")
                    return

                # Registrar la venta
                try:
                    cursor.execute("INSERT INTO VENTA (Fecha_venta, Tipo_pago) VALUES (NOW(), %s)", (tipo_pago,))
                    id_venta = cursor.lastrowid

                    # Insertar productos en PRODUCTOXVENTA
                    for producto in productos_vender:
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
                    st.session_state.productos = []  # Reiniciar productos

                except Exception as e:
                    con.rollback()
                    st.error(f"❌ Error al registrar venta: {e}")

    except Exception as e:
        st.error(f"❌ Error general: {e}")

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'con' in locals(): con.close()

import streamlit as st
from modulos.config.conexion import obtener_conexion

def mostrar_ventas():
    st.header("Registrar venta")

    if "num_productos" not in st.session_state:
        st.session_state.num_productos = 1

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Obtener todos los emprendimientos
        cursor.execute("SELECT ID_Emprendimiento, Nombre_emprendimiento FROM EMPRENDIMIENTO")
        emprendimientos = cursor.fetchall()
        if not emprendimientos:
            st.error("No hay emprendimientos registrados.")
            return

        emprend_dict = {nombre: id_emp for id_emp, nombre in emprendimientos}

        # Obtener todos los productos una sola vez
        cursor.execute("""
            SELECT ID_Producto, Nombre_producto, Precio, ID_Emprendimiento 
            FROM PRODUCTO
        """)
        productos = cursor.fetchall()
        productos_por_emprend = {}
        for idp, nombre, precio, id_emp in productos:
            if id_emp not in productos_por_emprend:
                productos_por_emprend[id_emp] = []
            productos_por_emprend[id_emp].append((idp, nombre, precio))

        productos_vender = []
        total_general = 0

        st.markdown("### Selecciona productos por emprendimiento")

        with st.form("formulario_venta", clear_on_submit=False):
            for i in range(st.session_state.num_productos):
                st.markdown(f"#### Producto #{i+1}")
                col1, col2 = st.columns(2)

                with col1:
                    emp_sel = st.selectbox(
                        f"Emprendimiento {i+1}",
                        ["-- Selecciona --"] + list(emprend_dict.keys()),
                        key=f"emprend_{i}"
                    )

                with col2:
                    cantidad = st.number_input(f"Cantidad {i+1}", min_value=1, key=f"cantidad_{i}")

                if emp_sel != "-- Selecciona --":
                    id_emp = emprend_dict[emp_sel]
                    opciones_productos = productos_por_emprend.get(id_emp, [])

                    opciones_mostrar = [
                        f"{nombre} (${precio:.2f})" for _, nombre, precio in opciones_productos
                    ]

                    producto_sel = st.selectbox(
                        f"Producto {i+1}",
                        ["-- Selecciona --"] + opciones_mostrar,
                        key=f"producto_{i}"
                    )

                    if producto_sel != "-- Selecciona --":
                        index = opciones_mostrar.index(producto_sel)
                        id_producto, nombre_producto, precio_unitario = opciones_productos[index]
                        subtotal = cantidad * precio_unitario
                        total_general += subtotal
                        productos_vender.append({
                            "id_producto": id_producto,
                            "precio_unitario": precio_unitario,
                            "cantidad": cantidad,
                            "nombre": nombre_producto,
                            "subtotal": subtotal
                        })
                        st.markdown(f"**Subtotal:** ${subtotal:.2f}")

            if productos_vender:
                st.markdown(f"### 💰 Total a cobrar: **${total_general:.2f}**")

            tipo_pago = st.selectbox("Tipo de pago", ["Efectivo", "Woompi"])
            col1, col2 = st.columns(2)
            agregar = col1.form_submit_button("➕ Agregar otro producto")
            registrar = col2.form_submit_button("✅ Registrar venta")

        if agregar:
            st.session_state.num_productos += 1
            st.rerun()

        if registrar:
            if not productos_vender:
                st.error("Debes seleccionar al menos un producto.")
                return

            errores = []
            for item in productos_vender:
                cursor.execute(
                    "SELECT SUM(Stock) FROM INVENTARIO WHERE ID_Producto = %s",
                    (item["id_producto"],)
                )
                resultado = cursor.fetchone()
                stock_disponible = int(resultado[0]) if resultado and resultado[0] else 0
                if stock_disponible < item["cantidad"]:
                    errores.append(f"{item['nombre']}: Stock insuficiente (disponible: {stock_disponible})")

            if errores:
                for err in errores:
                    st.error(err)
                return

            try:
                cursor.execute(
                    "INSERT INTO VENTA (Fecha_venta, Tipo_pago) VALUES (NOW(), %s)",
                    (tipo_pago,)
                )
                id_venta = cursor.lastrowid

                for item in productos_vender:
                    cursor.execute(
                        "INSERT INTO PRODUCTOXVENTA (ID_Venta, ID_Producto, Cantidad, Precio_unitario) "
                        "VALUES (%s, %s, %s, %s)",
                        (id_venta, item["id_producto"], item["cantidad"], item["precio_unitario"])
                    )

                    cantidad_restante = item["cantidad"]
                    cursor.execute(
                        "SELECT ID_Inventario, Stock FROM INVENTARIO "
                        "WHERE ID_Producto = %s AND Stock > 0 ORDER BY Fecha_ingreso ASC",
                        (item["id_producto"],)
                    )
                    inventarios = cursor.fetchall()

                    for inv_id, stock in inventarios:
                        if cantidad_restante <= 0:
                            break
                        a_restar = min(cantidad_restante, stock)
                        cursor.execute(
                            "UPDATE INVENTARIO SET Stock = Stock - %s WHERE ID_Inventario = %s",
                            (a_restar, inv_id)
                        )
                        cantidad_restante -= a_restar

                    if cantidad_restante > 0:
                        raise Exception(f"{item['nombre']}: No se pudo descontar todo el stock.")

                con.commit()
                st.success("✅ Venta registrada exitosamente.")
                st.session_state.num_productos = 1

            except Exception as e:
                con.rollback()
                st.error(f"❌ Error al registrar venta: {e}")

    except Exception as e:
        st.error(f"❌ Error general: {e}")

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'con' in locals(): con.close()

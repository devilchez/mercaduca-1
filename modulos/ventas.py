import streamlit as st
from modulos.config.conexion import obtener_conexion

def mostrar_ventas():
    st.header("Registrar venta")

    if "num_productos" not in st.session_state:
        st.session_state.num_productos = 1

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Obtener emprendimientos
        cursor.execute("SELECT ID_Emprendimiento, Nombre_emprendimiento FROM EMPRENDIMIENTO")
        emprendimientos = cursor.fetchall()
        if not emprendimientos:
            st.error("No hay emprendimientos registrados.")
            return

        emprend_dict = {nombre: id_emp for id_emp, nombre in emprendimientos}
        emprend_sel = st.selectbox("Selecciona un emprendimiento", list(emprend_dict.keys()))
        id_emprendimiento = emprend_dict[emprend_sel]

        # Obtener productos del emprendimiento
        cursor.execute("""
            SELECT ID_Producto, Nombre_producto, Precio 
            FROM PRODUCTO 
            WHERE ID_Emprendimiento = %s
        """, (id_emprendimiento,))
        productos = cursor.fetchall()

        if not productos:
            st.warning("Este emprendimiento no tiene productos.")
            return

        producto_dict = {
            f"{nombre} (${precio:.2f})": (idp, precio)
            for idp, nombre, precio in productos
        }

        st.markdown("### Productos a vender")
        productos_vender = []

        with st.form("formulario_venta", clear_on_submit=False):
            total_general = 0
            for i in range(st.session_state.num_productos):
                st.markdown(f"#### Producto #{i+1}")
                col1, col2 = st.columns(2)
                with col1:
                    producto_sel = st.selectbox(
                        f"Producto {i+1}",
                        ["-- Selecciona --"] + list(producto_dict.keys()),
                        key=f"producto_{i}"
                    )
                with col2:
                    cantidad = st.number_input(f"Cantidad {i+1}", min_value=1, step=1, key=f"cantidad_{i}")

                if producto_sel != "-- Selecciona --":
                    id_producto, precio_unitario = producto_dict[producto_sel]
                    subtotal = cantidad * precio_unitario
                    total_general += subtotal
                    productos_vender.append({
                        "id_producto": id_producto,
                        "precio_unitario": precio_unitario,
                        "cantidad": cantidad,
                        "nombre": producto_sel.split(" ($")[0],
                        "subtotal": subtotal
                    })
                    st.markdown(f"**Subtotal:** ${subtotal:.2f}")

            if productos_vender:
                st.markdown(f"### 💵 Total a cobrar: **${total_general:.2f}**")

            tipo_pago = st.selectbox("Tipo de pago", ["Efectivo", "Woompi"], key="tipo_pago")
            col1, col2 = st.columns(2)
            agregar = col1.form_submit_button("➕ Agregar otro producto")
            registrar = col2.form_submit_button("✅ Registrar venta")

        if agregar:
            st.session_state.num_productos += 1
            st.rerun()  # Corrección aquí

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
                        raise Exception(f"Error: No se pudo descontar completamente el stock de {item['nombre']}.")

                con.commit()
                st.success("✅ Venta registrada correctamente.")
                st.session_state.num_productos = 1  # Reiniciar contador

            except Exception as e:
                con.rollback()
                st.error(f"❌ Error al registrar venta: {e}")

    except Exception as e:
        st.error(f"❌ Error general: {e}")

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'con' in locals(): con.close()

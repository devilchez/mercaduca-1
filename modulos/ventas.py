import streamlit as st
from modulos.config.conexion import obtener_conexion

def mostrar_ventas():
    st.header("Registrar venta")

    if "initialized" not in st.session_state:
        st.session_state.secciones = [{"id": 0, "productos": 1}]
        st.session_state.contador_secciones = 1
        st.session_state.emprendimientos_seleccionados = {}
        st.session_state.initialized = True

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Cargar emprendimientos
        cursor.execute("SELECT ID_Emprendimiento, Nombre_emprendimiento FROM EMPRENDIMIENTO")
        emprendimientos = cursor.fetchall()
        emprend_dict = {nombre: id_emp for id_emp, nombre in emprendimientos}

        # Cargar productos
        cursor.execute("SELECT ID_Producto, Nombre_producto, Precio, ID_Emprendimiento FROM PRODUCTO")
        productos = cursor.fetchall()
        productos_por_emprendimiento = {}
        for idp, nombre, precio, id_emp in productos:
            productos_por_emprendimiento.setdefault(id_emp, []).append((idp, nombre, precio))

        total_general = 0
        productos_vender = []

        for seccion in st.session_state.secciones:
            sec_id = seccion["id"]
            st.subheader(f"🧩 Emprendimiento #{sec_id + 1}")

            emp_sel = st.selectbox(
                f"Selecciona un emprendimiento (sección {sec_id + 1})",
                ["-- Selecciona --"] + list(emprend_dict.keys()),
                key=f"emprend_{sec_id}"
            )

            if emp_sel == "-- Selecciona --":
                continue

            id_emp = emprend_dict[emp_sel]
            st.session_state.emprendimientos_seleccionados[sec_id] = id_emp

            productos_disponibles = productos_por_emprendimiento.get(id_emp, [])
            if not productos_disponibles:
                st.warning("Este emprendimiento no tiene productos.")
                continue

            opciones_dict = {
                f"{nombre} (ID: {idp}) - ${precio:.2f}": (idp, nombre, precio)
                for idp, nombre, precio in productos_disponibles
            }
            opciones_str = list(opciones_dict.keys())

            for i in range(seccion["productos"]):
                st.markdown(f"**Producto #{i + 1} de {emp_sel}**")
                col1, col2 = st.columns(2)

                with col1:
                    prod_sel = st.selectbox(
                        f"Producto {i + 1} (sección {sec_id + 1})",
                        ["-- Selecciona --"] + opciones_str,
                        key=f"producto_{sec_id}_{i}"
                    )
                with col2:
                    cantidad = st.number_input(
                        f"Cantidad {i + 1} (sección {sec_id + 1})",
                        min_value=1,
                        step=1,
                        key=f"cantidad_{sec_id}_{i}"
                    )

                if prod_sel in opciones_dict:
                    id_producto, nombre_producto, precio_unitario = opciones_dict[prod_sel]

                    if id_producto:  # Validación fuerte
                        subtotal = cantidad * precio_unitario
                        total_general += subtotal
                        productos_vender.append({
                            "id_producto": id_producto,
                            "precio_unitario": precio_unitario,
                            "cantidad": cantidad,
                            "nombre": nombre_producto
                        })
                        st.caption(f"🆔 Código del producto: `{id_producto}`")
                        st.markdown(f"💵 Subtotal: **${subtotal:.2f}**")

            if st.button(f"➕ Agregar otro producto a {emp_sel}", key=f"agrega_{sec_id}"):
                seccion["productos"] += 1
                st.rerun()

        if productos_vender:
            st.markdown("---")
            st.markdown(f"### 💰 Total general: **${total_general:.2f}**")

        col1, col2 = st.columns(2)
        if col1.button("➕ Agregar otro emprendimiento"):
            st.session_state.secciones.append({"id": st.session_state.contador_secciones, "productos": 1})
            st.session_state.contador_secciones += 1
            st.rerun()

        if col2.button("✅ Registrar venta"):
            if not productos_vender:
                st.error("Debes seleccionar al menos un producto.")
                return

            # Verificar que los productos tienen el ID_Producto correctamente
            st.markdown("### 🔍 Depuración antes del insert:")
            for item in productos_vender:
                if not item["id_producto"]:
                    st.error(f"⛔ Error: Producto sin ID. Detalle: {item}")
                    return

            errores = []
            for item in productos_vender:
                cursor.execute("SELECT SUM(Stock) FROM INVENTARIO WHERE ID_Producto = %s", (item["id_producto"],))
                resultado = cursor.fetchone()
                stock_disponible = int(resultado[0]) if resultado and resultado[0] else 0
                if stock_disponible < item["cantidad"]:
                    errores.append(f"{item['nombre']}: Stock insuficiente (disponible: {stock_disponible})")

            if errores:
                for err in errores:
                    st.error(err)
                return

            try:
                # 1. Insertar la venta
                cursor.execute("INSERT INTO VENTA (Fecha_venta, Tipo_pago) VALUES (NOW(), %s)", ("Efectivo",))
                id_venta = cursor.lastrowid  # Obtener el ID de la venta recién insertada

                # 2. Insertar productos en PRODUCTOXVENTA con id_venta
                for item in productos_vender:
                    if not item["id_producto"]:
                        raise Exception("⛔ Intento de insertar producto con ID vacío.")

                    cursor.execute(
                        "INSERT INTO PRODUCTOXVENTA (id_venta, ID_Producto, Cantidad, Precio_unitario) "
                        "VALUES (%s, %s, %s, %s)",
                        (
                            id_venta,  # Ahora usamos el id_venta de la venta recién insertada
                            str(item["id_producto"]),  # Aseguramos que ID_Producto sea un string
                            int(item["cantidad"]),  # Cantidad como entero
                            float(item["precio_unitario"])  # Precio unitario como float
                        )
                    )

                    # Descontar inventario con FIFO
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

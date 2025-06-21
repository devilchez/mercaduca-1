import streamlit as st
from modulos.config.conexion import obtener_conexion

def mostrar_ventas():
    st.header("🧾 Registrar venta")

    # Inicialización de estado
    if "secciones" not in st.session_state:
        st.session_state.secciones = [{
            "id": 0,
            "emprendimiento": None,
            "productos": [{}]  # Solo un producto por defecto
        }]
        st.session_state.contador_secciones = 1
        st.session_state.productos_vender = []
        st.session_state.flag_agregado = False
        st.session_state.flag_producto = {}

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Obtener emprendimientos
        cursor.execute("SELECT ID_Emprendimiento, Nombre_emprendimiento FROM EMPRENDIMIENTO")
        emprendimientos = cursor.fetchall()
        emprend_dict = {nombre: id_emp for id_emp, nombre in emprendimientos}

        # Obtener productos por emprendimiento
        cursor.execute("SELECT ID_Producto, Nombre_producto, Precio, ID_Emprendimiento FROM PRODUCTO")
        productos = cursor.fetchall()
        productos_por_emprendimiento = {}
        for idp, nombre, precio, id_emp in productos:
            productos_por_emprendimiento.setdefault(id_emp, []).append((idp, nombre, precio))

        # Botón: marcar intención de agregar emprendimiento
        if st.button("➕ Agregar emprendimiento"):
            st.session_state.flag_agregado = True
            st.rerun()

        # Acción: agregar nueva sección
        if st.session_state.flag_agregado:
            nuevo_id = st.session_state.contador_secciones
            st.session_state.secciones.append({
                "id": nuevo_id,
                "emprendimiento": None,
                "productos": [{}]
            })
            st.session_state.contador_secciones += 1
            st.session_state.flag_agregado = False
            st.rerun()

        total_general = 0
        st.session_state.productos_vender = []

        # Mostrar secciones
        for seccion in st.session_state.secciones:
            sec_id = seccion["id"]
            st.subheader(f"🧩 Emprendimiento #{sec_id + 1}")

            id_emp = seccion.get("emprendimiento")

            if id_emp is None:
                emp_sel = st.selectbox(
                    f"Selecciona un emprendimiento (sección {sec_id + 1})",
                    ["-- Selecciona --"] + list(emprend_dict.keys()),
                    key=f"emprend_{sec_id}"
                )
                if emp_sel != "-- Selecciona --":
                    seccion["emprendimiento"] = emprend_dict[emp_sel]
                    st.rerun()
                continue

            productos_disponibles = productos_por_emprendimiento.get(id_emp, [])
            if not productos_disponibles:
                st.warning("Este emprendimiento no tiene productos.")
                continue

            opciones_dict = {
                nombre: (idp, nombre, precio) for idp, nombre, precio in productos_disponibles
            }
            opciones_str = list(opciones_dict.keys())

            subtotal_emprendimiento = 0

            for i, _ in enumerate(seccion["productos"]):
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
                    subtotal = cantidad * precio_unitario
                    subtotal_emprendimiento += subtotal

                    st.caption(f"🆔 Código: `{id_producto}`")
                    st.markdown(f"💵 Subtotal: **${subtotal:.2f}**")

                    st.session_state.productos_vender.append({
                        "id_producto": id_producto,
                        "precio_unitario": precio_unitario,
                        "cantidad": cantidad,
                        "nombre": nombre_producto
                    })

            st.markdown(f"🧮 Subtotal por emprendimiento #{sec_id + 1}: **${subtotal_emprendimiento:.2f}**")
            total_general += subtotal_emprendimiento

            # Control para agregar producto
            if sec_id not in st.session_state.flag_producto:
                st.session_state.flag_producto[sec_id] = False

            if st.button(f"➕ Agregar producto a emprendimiento #{sec_id + 1}", key=f"agrega_producto_{sec_id}"):
                st.session_state.flag_producto[sec_id] = True
                st.rerun()

            if st.session_state.flag_producto[sec_id]:
                seccion["productos"].append({})
                st.session_state.flag_producto[sec_id] = False
                st.rerun()

        if st.session_state.productos_vender:
            st.markdown("---")
            st.markdown(f"### 💰 Total general: **${total_general:.2f}**")

        # Selector de tipo de pago
        tipo_pago = st.selectbox("💳 Tipo de pago", ["Efectivo", "Woompi"], key="tipo_pago")

        if st.button("✅ Registrar venta"):
            if not st.session_state.productos_vender:
                st.error("Debes seleccionar al menos un producto.")
                return

            errores = []
            for item in st.session_state.productos_vender:
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
                cursor.execute("INSERT INTO VENTA (Fecha_venta, Tipo_pago) VALUES (NOW(), %s)", (tipo_pago,))
                id_venta = cursor.lastrowid

                for item in st.session_state.productos_vender:
                    cursor.execute(
                        "INSERT INTO PRODUCTOXVENTA (id_venta, ID_Producto, Cantidad, Precio_unitario) "
                        "VALUES (%s, %s, %s, %s)",
                        (
                            id_venta,
                            str(item["id_producto"]),
                            int(item["cantidad"]),
                            float(item["precio_unitario"])
                        )
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

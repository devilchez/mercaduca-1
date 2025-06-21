import streamlit as st
from modulos.config.conexion import obtener_conexion

def mostrar_ventas():
    st.header("🧾 Registrar venta")

    # Inicialización del estado
    if "secciones" not in st.session_state:
        st.session_state.secciones = [{
            "id": 0,
            "emprendimiento": None,
            "productos": [{"producto": None, "cantidad": 1}]
        }]
        st.session_state.contador_secciones = 1

    def recargar():
        st.rerun()

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Cargar emprendimientos
        cursor.execute("SELECT ID_Emprendimiento, Nombre_emprendimiento FROM EMPRENDIMIENTO")
        emprendimientos = cursor.fetchall()
        emprend_dict = {nombre: id_emp for id_emp, nombre in emprendimientos}

        # Cargar productos y agrupar por emprendimiento
        cursor.execute("SELECT ID_Producto, Nombre_producto, Precio, ID_Emprendimiento FROM PRODUCTO")
        productos = cursor.fetchall()
        productos_por_emprendimiento = {}
        for idp, nombre, precio, id_emp in productos:
            productos_por_emprendimiento.setdefault(id_emp, []).append({
                "id": idp,
                "nombre": nombre,
                "precio": precio
            })

        total_general = 0
        productos_vender = []

        # Mostrar cada sección
        for seccion in st.session_state.secciones:
            sec_id = seccion["id"]
            st.subheader(f"🧩 Emprendimiento #{sec_id + 1}")

            # Validar que 'productos' sea lista de dicts correctamente
            if not isinstance(seccion.get("productos"), list):
                seccion["productos"] = [{"producto": None, "cantidad": 1}]
            else:
                # Sanitizar la lista para que cada item sea dict con claves esperadas
                for i, p in enumerate(seccion["productos"]):
                    if not isinstance(p, dict):
                        seccion["productos"][i] = {"producto": None, "cantidad": 1}
                    else:
                        if "producto" not in p:
                            seccion["productos"][i]["producto"] = None
                        if "cantidad" not in p:
                            seccion["productos"][i]["cantidad"] = 1

            opciones_emprendimiento = ["-- Selecciona --"] + list(emprend_dict.keys())
            idx_emp_sel = 0
            if seccion["emprendimiento"]:
                nombre_emp = next((k for k, v in emprend_dict.items() if v == seccion["emprendimiento"]), None)
                if nombre_emp in opciones_emprendimiento:
                    idx_emp_sel = opciones_emprendimiento.index(nombre_emp)

            emprendimiento_sel = st.selectbox(
                "Selecciona un emprendimiento",
                opciones_emprendimiento,
                index=idx_emp_sel,
                key=f"emprend_{sec_id}"
            )

            if emprendimiento_sel == "-- Selecciona --":
                seccion["emprendimiento"] = None
                seccion["productos"] = []
                st.info("Selecciona un emprendimiento para poder agregar productos.")
                continue
            else:
                seccion["emprendimiento"] = emprend_dict[emprendimiento_sel]

            id_emp = seccion["emprendimiento"]
            productos_disponibles = productos_por_emprendimiento.get(id_emp, [])

            if not productos_disponibles:
                st.warning("Este emprendimiento no tiene productos.")
                seccion["productos"] = []
                continue

            opciones_productos = ["-- Selecciona --"] + [p["nombre"] for p in productos_disponibles]

            # Asegurar que haya al menos un producto para mostrar
            if len(seccion["productos"]) == 0:
                seccion["productos"].append({"producto": None, "cantidad": 1})

            for i, prod in enumerate(seccion["productos"]):
                col1, col2 = st.columns([3,1])

                idx_prod_sel = 0
                if prod["producto"] in opciones_productos:
                    idx_prod_sel = opciones_productos.index(prod["producto"])

                with col1:
                    prod_sel = st.selectbox(
                        f"Selecciona producto #{i+1}",
                        opciones_productos,
                        index=idx_prod_sel,
                        key=f"producto_{sec_id}_{i}"
                    )

                with col2:
                    cantidad = st.number_input(
                        f"Cantidad #{i+1}",
                        min_value=1,
                        value=prod.get("cantidad", 1),
                        step=1,
                        key=f"cantidad_{sec_id}_{i}"
                    )

                seccion["productos"][i]["producto"] = prod_sel if prod_sel != "-- Selecciona --" else None
                seccion["productos"][i]["cantidad"] = cantidad

            # Botón para agregar producto a la sección actual
            if st.button(f"➕ Agregar producto a emprendimiento #{sec_id + 1}", key=f"add_prod_{sec_id}"):
                seccion["productos"].append({"producto": None, "cantidad": 1})
                recargar()

            # Calcular subtotal de la sección
            subtotal_seccion = 0
            for p in seccion["productos"]:
                if p["producto"]:
                    p_info = next((x for x in productos_disponibles if x["nombre"] == p["producto"]), None)
                    if p_info:
                        subtotal_seccion += p_info["precio"] * p["cantidad"]
                        productos_vender.append({
                            "id_producto": p_info["id"],
                            "precio_unitario": p_info["precio"],
                            "cantidad": p["cantidad"],
                            "nombre": p_info["nombre"]
                        })

            st.markdown(f"🧮 Subtotal emprendimiento #{sec_id + 1}: **${subtotal_seccion:.2f}**")
            total_general += subtotal_seccion

        # Botón para agregar nueva sección (nuevo emprendimiento)
        if st.button("➕ Agregar emprendimiento"):
            nuevo_id = st.session_state.contador_secciones
            st.session_state.secciones.append({
                "id": nuevo_id,
                "emprendimiento": None,
                "productos": [{"producto": None, "cantidad": 1}]
            })
            st.session_state.contador_secciones += 1
            recargar()

        # Mostrar total general
        if productos_vender:
            st.markdown("---")
            st.markdown(f"### 💰 Total general: **${total_general:.2f}**")

        # Selector tipo de pago
        tipo_pago = st.selectbox("💳 Tipo de pago", ["Efectivo", "Woompi"], key="tipo_pago")

        # Botón registrar venta (pendiente)
        if st.button("✅ Registrar venta"):
            if not productos_vender:
                st.error("Debes seleccionar al menos un producto antes de registrar la venta.")
                st.stop()

            st.success("Lógica para registrar la venta pendiente de implementar.")

    except Exception as e:
        st.error(f"❌ Error general: {e}")

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'con' in locals(): con.close()

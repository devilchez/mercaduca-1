import streamlit as st
from modulos.config.conexion import obtener_conexion

def mostrar_ventas():
    st.header("🧾 Registrar venta")

    # Inicialización de estado
    if "secciones" not in st.session_state:
        st.session_state.secciones = [{
            "id": 0,
            "emprendimiento": None,
            "productos": []  # lista de productos seleccionados en esta sección
        }]
        st.session_state.contador_secciones = 1

    # Conexión y carga de datos
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Obtener emprendimientos
        cursor.execute("SELECT ID_Emprendimiento, Nombre_emprendimiento FROM EMPRENDIMIENTO")
        emprendimientos = cursor.fetchall()
        emprend_dict = {nombre: id_emp for id_emp, nombre in emprendimientos}

        # Obtener productos y agrupar por emprendimiento
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

        # Mostrar secciones (cada una con 1 lista de emprendimiento + productos dependientes)
        for seccion in st.session_state.secciones:
            sec_id = seccion["id"]
            st.subheader(f"🧩 Emprendimiento #{sec_id + 1}")

            # Selección de emprendimiento (1 lista)
            emprendimiento_seleccionado = st.selectbox(
                "Selecciona un emprendimiento",
                ["-- Selecciona --"] + list(emprend_dict.keys()),
                index=(
                    list(emprend_dict.keys()).index(
                        next((k for k,v in emprend_dict.items() if v == seccion["emprendimiento"]), None)
                    ) if seccion["emprendimiento"] else 0
                ),
                key=f"emprend_{sec_id}"
            )

            if emprendimiento_seleccionado == "-- Selecciona --":
                seccion["emprendimiento"] = None
                seccion["productos"] = []
                continue
            else:
                seccion["emprendimiento"] = emprend_dict[emprendimiento_seleccionado]

            id_emp = seccion["emprendimiento"]

            # Productos disponibles para el emprendimiento seleccionado
            productos_disponibles = productos_por_emprendimiento.get(id_emp, [])
            if not productos_disponibles:
                st.warning("Este emprendimiento no tiene productos.")
                continue

            opciones_productos = [p["nombre"] for p in productos_disponibles]

            # Si no hay productos seleccionados aún, inicializa lista vacía
            if not seccion["productos"]:
                seccion["productos"].append({"producto": None, "cantidad": 1})

            # Mostrar productos seleccionados (cada uno con lista desplegable y cantidad)
            for i, prod in enumerate(seccion["productos"]):
                col1, col2 = st.columns([3,1])
                with col1:
                    prod_sel = st.selectbox(
                        f"Selecciona producto #{i+1}",
                        ["-- Selecciona --"] + opciones_productos,
                        index=(opciones_productos.index(prod["producto"]) if prod["producto"] in opciones_productos else 0),
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

                # Actualizar estado
                seccion["productos"][i]["producto"] = prod_sel if prod_sel != "-- Selecciona --" else None
                seccion["productos"][i]["cantidad"] = cantidad

            # Botón para agregar producto en esta sección
            if st.button(f"➕ Agregar producto a emprendimiento #{sec_id + 1}", key=f"add_prod_{sec_id}"):
                seccion["productos"].append({"producto": None, "cantidad": 1})
                st.experimental_rerun()

            # Calcular subtotal por emprendimiento
            subtotal_emprendimiento = 0
            for p in seccion["productos"]:
                if p["producto"]:
                    prod_info = next((x for x in productos_disponibles if x["nombre"] == p["producto"]), None)
                    if prod_info:
                        subtotal_emprendimiento += prod_info["precio"] * p["cantidad"]
                        productos_vender.append({
                            "id_producto": prod_info["id"],
                            "precio_unitario": prod_info["precio"],
                            "cantidad": p["cantidad"],
                            "nombre": prod_info["nombre"]
                        })

            st.markdown(f"🧮 Subtotal emprendimiento #{sec_id + 1}: **${subtotal_emprendimiento:.2f}**")
            total_general += subtotal_emprendimiento

        # Botón para agregar nueva sección (nuevo emprendimiento)
        if st.button("➕ Agregar emprendimiento"):
            nuevo_id = st.session_state.contador_secciones
            st.session_state.secciones.append({
                "id": nuevo_id,
                "emprendimiento": None,
                "productos": []
            })
            st.session_state.contador_secciones += 1
            st.experimental_rerun()

        # Mostrar total general y lista tipo de pago
        if productos_vender:
            st.markdown("---")
            st.markdown(f"### 💰 Total general: **${total_general:.2f}**")

        tipo_pago = st.selectbox("💳 Tipo de pago", ["Efectivo", "Woompi"], key="tipo_pago")

        # Botón registrar venta (a implementar)
        if st.button("✅ Registrar venta"):
            if not productos_vender:
                st.error("Debes seleccionar al menos un producto antes de registrar la venta.")
                st.stop()

            st.success("Lógica para registrar venta pendiente de implementar.")

    except Exception as e:
        st.error(f"❌ Error general: {e}")

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'con' in locals(): con.close()

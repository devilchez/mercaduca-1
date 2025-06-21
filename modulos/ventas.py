import streamlit as st
from modulos.config.conexion import obtener_conexion

def mostrar_ventas():
    st.header("🧾 Registrar venta")

    # Inicialización del estado
    if "secciones" not in st.session_state:
        st.session_state.secciones = [{
            "id": 0,
            "emprendimiento": None,
            "productos": [{}]
        }]
        st.session_state.contador_secciones = 1
        st.session_state.productos_vender = []

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

        total_general = 0
        st.session_state.productos_vender = []

        # Mostrar cada sección
        for seccion in st.session_state.secciones:
            sec_id = seccion["id"]
            st.subheader(f"🧩 Emprendimiento #{sec_id + 1}")
            id_emp = seccion["emprendimiento"]

            if id_emp is None:
                emp_sel = st.selectbox(
                    "Selecciona un emprendimiento",
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
                        f"Producto {i + 1}",
                        ["-- Selecciona --"] + opciones_str,
                        key=f"producto_{sec_id}_{i}"
                    )
                with col2:
                    cantidad = st.number_input(
                        f"Cantidad {i + 1}",
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

            # Botón para agregar producto a esta sección
            if st.button(f"➕ Agregar producto a emprendimiento #{sec_id + 1}", key=f"add_prod_{sec_id}"):
                seccion["productos"].append({})
                st.rerun()

        # Botón para agregar nueva sección de emprendimiento
        if st.button("➕ Agregar otro emprendimiento"):
            nuevo_id = st.session_state.contador_secciones
            st.session_state.secciones.append({
                "id": nuevo_id,
                "emprendimiento": None,
                "productos": [{}]
            })
            st.session_state.contador_secciones += 1
            st.rerun()

        # Mostrar total general
        if st.session_state.productos_vender:
            st.markdown("---")
            st.markdown(f"### 💰 Total general: **${total_general:.2f}**")

        # Mostrar selector de tipo de pago
        tipo_pago = st.selectbox("💳 Tipo de pago", ["Efectivo", "Woompi"], key="tipo_pago")

    except Exception as e:
        st.error(f"❌ Error general: {e}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'con' in locals(): con.close()

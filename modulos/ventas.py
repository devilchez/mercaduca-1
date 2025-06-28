import streamlit as st
from datetime import datetime
import pytz
from modulos.config.conexion import obtener_conexion

def mostrar_ventas():
    st.header("🏷️ Registrar venta")

    if "secciones" not in st.session_state:
        st.session_state.secciones = [{"id": 0, "emprendimiento": None, "productos": []}]
        st.session_state.contador_secciones = 1

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        cursor.execute("SELECT ID_Emprendimiento, Nombre_emprendimiento FROM EMPRENDIMIENTO")
        emprendimientos = cursor.fetchall()
        emprend_dict = {nombre: id_emp for id_emp, nombre in emprendimientos}

        cursor.execute("SELECT ID_Producto, Nombre_producto, Precio, ID_Emprendimiento FROM PRODUCTO")
        productos = cursor.fetchall()
        productos_por_emprendimiento = {}
        productos_dict = {}  # clave: nombre, valor: (id, precio)

        for idp, nombre, precio, id_emp in productos:
            productos_por_emprendimiento.setdefault(id_emp, []).append({
                "id": idp, "nombre": nombre, "precio": precio
            })
            productos_dict[nombre] = {"id": idp, "precio": precio}

        total_general = 0
        productos_vender = []

        for seccion in st.session_state.secciones:
            sec_id = seccion["id"]
            st.markdown(f"## Emprendimiento #{sec_id + 1}")

            opciones_emp = ["-- Selecciona --"] + list(emprend_dict.keys())
            nombre_emp_actual = next((k for k, v in emprend_dict.items() if v == seccion["emprendimiento"]), "-- Selecciona --")
            idx_emp_actual = opciones_emp.index(nombre_emp_actual) if nombre_emp_actual in opciones_emp else 0

            emprendimiento_sel = st.selectbox(
                f"Selecciona un emprendimiento",
                opciones_emp,
                index=idx_emp_actual,
                key=f"emprend_{sec_id}"
            )

            if emprendimiento_sel == "-- Selecciona --":
                st.info("Selecciona un emprendimiento para continuar.")
                continue

            nuevo_id_emp = emprend_dict[emprendimiento_sel]

            if nuevo_id_emp != seccion["emprendimiento"]:
                seccion["emprendimiento"] = nuevo_id_emp
                seccion["productos"] = [{"producto": None, "cantidad": 1}]
                st.rerun()

            id_emp = seccion["emprendimiento"]
            productos_disponibles = productos_por_emprendimiento.get(id_emp, [])

            if not productos_disponibles:
                st.warning("Este emprendimiento no tiene productos.")
                continue

            opciones_productos = ["-- Selecciona --"] + [p["nombre"] for p in productos_disponibles]

            for i, prod in enumerate(seccion["productos"]):
                col1, col2 = st.columns([3, 1])

                idx_prod_sel = 0
                if prod["producto"] in opciones_productos:
                    idx_prod_sel = opciones_productos.index(prod["producto"])

                with col1:
                    prod_sel = st.selectbox(
                        f"Selecciona producto #{i + 1}",
                        opciones_productos,
                        index=idx_prod_sel,
                        key=f"producto_{sec_id}_{i}"
                    )
                with col2:
                    cantidad = st.number_input(
                        f"Cantidad #{i + 1}",
                        min_value=1,
                        value=prod.get("cantidad", 1),
                        step=1,
                        key=f"cantidad_{sec_id}_{i}"
                    )

                seccion["productos"][i]["producto"] = prod_sel if prod_sel != "-- Selecciona --" else None
                seccion["productos"][i]["cantidad"] = cantidad

            if st.button(f"➕ Agregar otro producto a emprendimiento #{sec_id + 1}", key=f"add_prod_{sec_id}"):
                seccion["productos"].append({"producto": None, "cantidad": 1})
                st.rerun()

            subtotal = 0
            for p in seccion["productos"]:
                if p["producto"]:
                    info = productos_dict[p["producto"]]
                    subtotal += info["precio"] * p["cantidad"]
                    productos_vender.append({
                        "id_producto": info["id"],
                        "nombre": p["producto"],
                        "cantidad": p["cantidad"],
                        "precio_unitario": info["precio"]
                    })

            total_general += subtotal
            st.markdown(f"🧮 Subtotal emprendimiento #{sec_id + 1}: **${subtotal:.2f}**")

        if all(sec["emprendimiento"] is not None for sec in st.session_state.secciones):
            if st.button("➕ Agregar otro emprendimiento"):
                nuevo_id = st.session_state.contador_secciones
                st.session_state.secciones.append({
                    "id": nuevo_id,
                    "emprendimiento": None,
                    "productos": []
                })
                st.session_state.contador_secciones += 1
                st.rerun()

        if productos_vender:
            st.markdown("---")
            st.markdown("### 🧾 Resumen de productos a vender:")
            for p in productos_vender:
                st.write(f"🟩 Emprendimiento {e['id_emprendimiento']}  - Producto: {p['id_producto']} - Cantidad: {p['cantidad']} - Precio: ${p['precio_unitario']:.2f}")
        
            st.markdown(f"### 💰 Total general: **${total_general:.2f}**")

            tipo_pago = st.selectbox("💳 Tipo de pago", ["Efectivo", "Woompi"], key="tipo_pago")

            if st.button("✅ Registrar venta"):
                try:
                    timezone = pytz.timezone('America/El_Salvador')
                    ahora = datetime.now(timezone)
                    fecha_venta = ahora.date()
                    hora_venta = ahora.time()

                    total_cantidad_vendida = sum(p["cantidad"] for p in productos_vender)

                    cursor.execute(
                        "INSERT INTO VENTA (fecha_venta, hora_venta, tipo_pago, cantidad_vendida) VALUES (%s, %s, %s, %s)",
                        (fecha_venta, hora_venta, tipo_pago, total_cantidad_vendida)
                    )
                    id_venta = cursor.lastrowid

                    for p in productos_vender:
                        id_producto = p["id_producto"]
                        cantidad_vendida = p["cantidad"]
                        precio_unitario = p["precio_unitario"]

                        cursor.execute(
                            "INSERT INTO PRODUCTOXVENTA (id_venta, id_producto, cantidad, precio_unitario) VALUES (%s, %s, %s, %s)",
                            (id_venta, id_producto, cantidad_vendida, precio_unitario)
                        )

                        restante = cantidad_vendida
                        cursor.execute(
                            "SELECT ID_Inventario, Stock FROM INVENTARIO WHERE ID_Producto = %s AND Stock > 0 ORDER BY Fecha_vencimiento ASC",
                            (id_producto,)
                        )
                        inventario = cursor.fetchall()

                        for id_inv, stock in inventario:
                            if restante <= 0:
                                break
                            if stock <= restante:
                                cursor.execute(
                                    "UPDATE INVENTARIO SET Stock = 0, Fecha_salida = %s, Cantidad_salida = Cantidad_salida + %s WHERE ID_Inventario = %s",
                                    (ahora, stock, id_inv)
                                )
                                restante -= stock
                            else:
                                cursor.execute(
                                    "UPDATE INVENTARIO SET Stock = %s, Fecha_salida = %s, Cantidad_salida = Cantidad_salida + %s WHERE ID_Inventario = %s",
                                    (stock - restante, ahora, restante, id_inv)
                                )
                                restante = 0

                        if restante > 0:
                            raise Exception(f"Stock insuficiente para producto ID {id_producto}")

                    con.commit()
                    st.success(f"✅ Venta registrada correctamente con ID: {id_venta}")
                    st.session_state.secciones = [{"id": 0, "emprendimiento": None, "productos": []}]
                    st.session_state.contador_secciones = 1
                    st.rerun()

                except Exception as e:
                    con.rollback()
                    st.error(f"❌ Error al registrar la venta o actualizar inventario: {e}")

    except Exception as e:
        st.error(f"❌ Error general: {e}")

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'con' in locals(): con.close()

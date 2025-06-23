import streamlit as st
from datetime import datetime
from modulos.config.conexion import obtener_conexion

def mostrar_abastecimiento():
    if "usuario" not in st.session_state:
        st.warning("⚠️ Debes iniciar sesión.")
        st.stop()

    st.header("📦 Registrar abastecimiento")

    if "abast_secciones" not in st.session_state:
        st.session_state.abast_secciones = [{"id": 0, "emprendimiento": None, "productos": []}]
        st.session_state.abast_contador = 1

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        cursor.execute("SELECT ID_Emprendimiento, Nombre_emprendimiento FROM EMPRENDIMIENTO")
        emprendimientos = cursor.fetchall()
        emprend_dict = {nombre: id_emp for id_emp, nombre in emprendimientos}

        cursor.execute("SELECT ID_Producto, Nombre_producto, Precio, ID_Emprendimiento, Tipo_producto FROM PRODUCTO")
        productos = cursor.fetchall()
        productos_por_emprendimiento = {}
        for idp, nombre, precio, id_emp, tipo_producto in productos:
            productos_por_emprendimiento.setdefault(id_emp, []).append({
                "id": idp,
                "nombre": nombre,
                "precio": precio,
                "tipo_producto": tipo_producto  # Guardamos el tipo de producto
            })

        productos_abastecer = []

        for seccion in st.session_state.abast_secciones:
            sec_id = seccion["id"]
            st.subheader(f"🧩 Emprendimiento #{sec_id + 1}")

            opciones_emp = ["-- Selecciona --"] + list(emprend_dict.keys())
            nombre_emp_actual = next((k for k, v in emprend_dict.items() if v == seccion["emprendimiento"]), "-- Selecciona --")
            idx_emp_actual = opciones_emp.index(nombre_emp_actual) if nombre_emp_actual in opciones_emp else 0

            emprendimiento_sel = st.selectbox(
                "Selecciona un emprendimiento",
                opciones_emp,
                index=idx_emp_actual,
                key=f"abast_emp_{sec_id}"
            )

            if emprendimiento_sel == "-- Selecciona --":
                st.info("Selecciona un emprendimiento para continuar.")
                continue

            nuevo_id_emp = emprend_dict[emprendimiento_sel]
            if nuevo_id_emp != seccion["emprendimiento"]:
                seccion["emprendimiento"] = nuevo_id_emp
                seccion["productos"] = [{"producto": None, "cantidad": 1, "fecha_vencimiento": datetime.today().date()}]
                st.rerun()

            productos_disponibles = productos_por_emprendimiento.get(nuevo_id_emp, [])
            opciones_productos = ["-- Selecciona --"] + [p["nombre"] for p in productos_disponibles]

            for i, prod in enumerate(seccion["productos"]):
                col1, col2, col3 = st.columns([3, 1, 2])
                idx_prod_sel = opciones_productos.index(prod["producto"]) if prod["producto"] in opciones_productos else 0

                with col1:
                    prod_sel = st.selectbox(
                        f"Producto #{i + 1}",
                        opciones_productos,
                        index=idx_prod_sel,
                        key=f"abast_producto_{sec_id}_{i}"
                    )
                with col2:
                    cantidad = st.number_input(
                        f"Cantidad #{i + 1}",
                        min_value=1,
                        value=prod.get("cantidad", 1),
                        format="%d",
                        key=f"abast_cantidad_{sec_id}_{i}"
                    )

                # Consultar el tipo de producto solo después de que el usuario selecciona el producto
                if prod_sel != "-- Selecciona --":
                    # Obtener el producto seleccionado
                    producto_info = next((p for p in productos_disponibles if p["nombre"] == prod_sel), None)
                    if producto_info:
                        # Verificar si el producto es perecedero
                        if producto_info["tipo_producto"] == "Perecedero":  # Verificamos si es perecedero
                            with col3:
                                fecha_vencimiento = st.date_input(
                                    f"Vence el #{i + 1}",
                                    value=prod.get("fecha_vencimiento", datetime.today().date()),
                                    key=f"abast_fecha_venc_{sec_id}_{i}"
                                )
                            seccion["productos"][i]["fecha_vencimiento"] = fecha_vencimiento
                        else:
                            seccion["productos"][i]["fecha_vencimiento"] = None  # No es perecedero, no se necesita fecha

                seccion["productos"][i]["producto"] = prod_sel if prod_sel != "-- Selecciona --" else None
                seccion["productos"][i]["cantidad"] = cantidad

            if len(seccion["productos"]) < 200:
                if st.button(f"➕ Agregar otro producto a emprendimiento #{sec_id + 1}", key=f"add_prod_abast_{sec_id}"):
                    seccion["productos"].append({"producto": None, "cantidad": 1, "fecha_vencimiento": datetime.today().date()})
                    st.rerun()
            else:
                st.warning("⚠️ Límite de 200 productos alcanzado para este emprendimiento.")

            for p in seccion["productos"]:
                if p["producto"]:
                    info = next((x for x in productos_disponibles if x["nombre"] == p["producto"]), None)
                    if info:
                        productos_abastecer.append({
                            "id_emprendimiento": seccion["emprendimiento"],
                            "id_producto": str(info["id"]),
                            "cantidad": p["cantidad"],
                            "precio": info["precio"],
                            "fecha_vencimiento": p["fecha_vencimiento"]
                        })

        if all(sec["emprendimiento"] is not None for sec in st.session_state.abast_secciones):
            if st.button("➕ Agregar otro emprendimiento"):
                nuevo_id = st.session_state.abast_contador
                st.session_state.abast_secciones.append({"id": nuevo_id, "emprendimiento": None, "productos": []})
                st.session_state.abast_contador += 1
                st.rerun()

        if productos_abastecer:
            st.markdown("---")
            st.markdown("### 🧾 Resumen de productos a abastecer:")
            for p in productos_abastecer:
                st.write(f"🟩 Emprendimiento {p['id_emprendimiento']} - Producto {p['id_producto']} - Cantidad: {p['cantidad']} - Precio: ${p['precio']:.2f} - Vence: {p['fecha_vencimiento']}")

            if st.button("✅ Registrar abastecimiento"):
                try:
                    agrupados = {}
                    for p in productos_abastecer:
                        agrupados.setdefault(p["id_emprendimiento"], []).append(p)

                    for id_emp, productos in agrupados.items():
                        cursor.execute("INSERT INTO ABASTECIMIENTO (ID_Emprendimiento, Fecha_ingreso) VALUES (%s, NOW())", (id_emp, ))
                        id_abastecimiento = cursor.lastrowid

                        for prod in productos:
                            cursor.execute("""INSERT INTO PRODUCTOXABASTECIMIENTO (ID_Producto, id_abastecimiento, cantidad, precio_unitario)
                                              VALUES (%s, %s, %s, %s)""", (prod["id_producto"], id_abastecimiento, prod["cantidad"], prod["precio"]))

                            cursor.execute("""INSERT INTO INVENTARIO (
                                                  ID_Abastecimiento,
                                                  ID_Producto,
                                                  Fecha_ingreso,
                                                  Cantidad_ingresada,
                                                  Cantidad_salida,
                                                  Stock,
                                                  Fecha_salida,
                                                  Fecha_vencimiento)
                                              VALUES (%s, %s, NOW(), %s, 0, %s, NULL, %s)""",
                                           (id_abastecimiento, prod["id_producto"], prod["cantidad"], prod["cantidad"], prod["fecha_vencimiento"]))

                    con.commit()
                    st.success("✅ Abastecimiento registrado correctamente.")
                    st.session_state.abast_secciones = [{"id": 0, "emprendimiento": None, "productos": []}]
                    st.session_state.abast_contador = 1
                    st.rerun()

                except Exception as e:
                    con.rollback()
                    st.error(f"❌ Error al registrar el abastecimiento: {e}")

    except Exception as e:
        st.error(f"❌ Error general: {e}")

    finally:
        try:
            if 'cursor' in locals() and cursor is not None:
                cursor.close()
        except:
            pass
        try:
            if 'con' in locals() and con is not None:
                con.close()
        except:
            pass

import streamlit as st
from modulos.config.conexion import obtener_conexion
from datetime import datetime

def mostrar_abastecimiento():
    if "usuario" not in st.session_state:
        st.warning("⚠️ Debes iniciar sesión.")
        st.stop()

    st.header("📦 Registrar abastecimiento")

    # Estado inicial para múltiples secciones
    if "abastecimientos" not in st.session_state:
        st.session_state.abastecimientos = [{"id": 0, "emprendimiento": None, "productos": []}]
        st.session_state.contador_abast = 1

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Cargar emprendimientos y productos
        cursor.execute("SELECT ID_Emprendimiento, Nombre_emprendimiento FROM EMPRENDIMIENTO")
        emprendimientos = cursor.fetchall()
        emprend_dict = {nombre: id_emp for id_emp, nombre in emprendimientos}

        cursor.execute("SELECT ID_Producto, Nombre_producto, Precio, ID_Emprendimiento FROM PRODUCTO")
        productos = cursor.fetchall()
        productos_por_emprendimiento = {}
        for idp, nombre, precio, id_emp in productos:
            productos_por_emprendimiento.setdefault(id_emp, []).append({
                "id": idp,
                "nombre": nombre,
                "precio": precio
            })

        # Recorrer secciones de abastecimiento
        for seccion in st.session_state.abastecimientos:
            sec_id = seccion["id"]
            st.markdown(f"## 🧩 Emprendimiento #{sec_id + 1}")

            opciones_emp = ["-- Selecciona --"] + list(emprend_dict.keys())
            nombre_emp_actual = next((k for k, v in emprend_dict.items() if v == seccion["emprendimiento"]), "-- Selecciona --")
            idx_emp_actual = opciones_emp.index(nombre_emp_actual) if nombre_emp_actual in opciones_emp else 0

            emprendimiento_sel = st.selectbox(
                f"Selecciona un emprendimiento",
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
                seccion["productos"] = [{"producto": None, "cantidad": 1}]
                st.rerun()

            id_emp = seccion["emprendimiento"]
            productos_disponibles = productos_por_emprendimiento.get(id_emp, [])

            if not productos_disponibles:
                st.warning("Este emprendimiento no tiene productos registrados.")
                continue

            opciones_productos = ["-- Selecciona --"] + [p["nombre"] for p in productos_disponibles]

            for i, prod in enumerate(seccion["productos"]):
                col1, col2 = st.columns([3, 1])

                idx_prod_sel = 0
                if prod["producto"] in opciones_productos:
                    idx_prod_sel = opciones_productos.index(prod["producto"])

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
                        step=1,
                        key=f"abast_cantidad_{sec_id}_{i}"
                    )

                seccion["productos"][i]["producto"] = prod_sel if prod_sel != "-- Selecciona --" else None
                seccion["productos"][i]["cantidad"] = cantidad

            if st.button(f"➕ Agregar otro producto a emprendimiento #{sec_id + 1}", key=f"add_prod_abast_{sec_id}"):
                seccion["productos"].append({"producto": None, "cantidad": 1})
                st.rerun()

        if all(sec["emprendimiento"] is not None for sec in st.session_state.abastecimientos):
            if st.button("➕ Agregar otro emprendimiento"):
                nuevo_id = st.session_state.contador_abast
                st.session_state.abastecimientos.append({"id": nuevo_id, "emprendimiento": None, "productos": []})
                st.session_state.contador_abast += 1
                st.rerun()

        # Botón para registrar abastecimientos
        if st.button("✅ Registrar abastecimiento"):
            try:
                fecha = datetime.now()
                for seccion in st.session_state.abastecimientos:
                    id_emp = seccion["emprendimiento"]
                    for p in seccion["productos"]:
                        if not p["producto"]:
                            continue
                        prod_info = next((x for x in productos_por_emprendimiento[id_emp] if x["nombre"] == p["producto"]), None)
                        if prod_info:
                            id_prod = prod_info["id"]
                            cantidad = p["cantidad"]

                            # Insertar en ABASTECIMIENTO
                            cursor.execute("""
                                INSERT INTO ABASTECIMIENTO (ID_Emprendimiento, Fecha_ingreso)
                                VALUES (%s, %s)
                            """, (id_emp, fecha))
                            id_abast = cursor.lastrowid

                            # Insertar en tabla cruzada PRODUCTOXABASTECIMIENTO
                            cursor.execute("""
                                INSERT INTO PRODUCTOXABASTECIMIENTO (ID_Producto, id_abastecimiento, cantidad, precio_unitario)
                                VALUES (%s, %s, %s, %s)
                            """, (id_prod, id_abast, cantidad, prod_info["precio"]))

                            # Insertar en INVENTARIO
                            cursor.execute("""
                                INSERT INTO INVENTARIO (ID_Producto, Cantidad_ingresada, Stock, Fecha_ingreso)
                                VALUES (%s, %s, %s, %s)
                            """, (id_prod, cantidad, cantidad, fecha))

                con.commit()
                st.success("✅ Abastecimientos registrados correctamente.")
                st.session_state.abastecimientos = [{"id": 0, "emprendimiento": None, "productos": []}]
                st.session_state.contador_abast = 1
                st.rerun()

            except Exception as e:
                con.rollback()
                st.error(f"❌ Error al registrar abastecimiento: {e}")

    except Exception as e:
        st.error(f"❌ Error general: {e}")

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'con' in locals(): con.close()


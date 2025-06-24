import streamlit as st
from modulos.config.conexion import obtener_conexion

def registrar_producto():
    st.header("📓 Registrar nuevo producto")

    # Estado inicial
    if "secciones_producto" not in st.session_state:
        st.session_state.secciones_producto = [{
            "id": 0,
            "emprendimiento": None,
            "producto": None,
            "nombre_producto": "",
            "descripcion": "",
            "precio": 0.0,
            "tipo_producto": "Perecedero"
        }]
        st.session_state.contador_secciones_producto = 1

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Cargar emprendimientos
        cursor.execute("SELECT ID_Emprendimiento, Nombre_emprendimiento FROM EMPRENDIMIENTO")
        emprendimientos = cursor.fetchall()
        emprend_dict = {nombre: id_emp for id_emp, nombre in emprendimientos}

        # Mostrar secciones de emprendimientos y productos
        for seccion in st.session_state.secciones_producto:
            sec_id = seccion["id"]
            st.markdown(f"## Emprendimiento #{sec_id + 1}")

            # Selección del emprendimiento
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
                st.info("🔹 Selecciona un emprendimiento para continuar.")
                continue

            nuevo_id_emp = emprend_dict[emprendimiento_sel]

            # Si el emprendimiento cambia, reiniciar la sección
            if nuevo_id_emp != seccion["emprendimiento"]:
                seccion["emprendimiento"] = nuevo_id_emp
                seccion["producto"] = None
                seccion["nombre_producto"] = ""
                seccion["descripcion"] = ""
                seccion["precio"] = 0.0
                seccion["tipo_producto"] = "Perecedero"
                st.rerun()

            id_emprendimiento = seccion["emprendimiento"]
            st.text_input("ID del Emprendimiento", value=id_emprendimiento, disabled=True)

            # Formulario del producto
            seccion["producto"] = st.text_input("ID del Producto", value=seccion["producto"], key=f"producto_{sec_id}")
            seccion["nombre_producto"] = st.text_input("Nombre del Producto", value=seccion["nombre_producto"], key=f"nombre_producto_{sec_id}")
            seccion["descripcion"] = st.text_area("Descripción", value=seccion["descripcion"], key=f"descripcion_{sec_id}")
            seccion["precio"] = st.number_input("Precio", min_value=0.0, value=seccion["precio"], step=0.01, key=f"precio_{sec_id}")
            seccion["tipo_producto"] = st.selectbox("Tipo de producto", ["Perecedero", "No perecedero"], index=["Perecedero", "No perecedero"].index(seccion["tipo_producto"]), key=f"tipo_producto_{sec_id}")

            # Registrar el producto
            if st.button(f"Registrar producto #{sec_id + 1}", key=f"registrar_{sec_id}"):
                if not all([seccion["producto"], seccion["nombre_producto"], seccion["descripcion"], seccion["precio"] > 0]):
                    st.warning("⚠️ Por favor, completa todos los campos.")
                else:
                    try:
                        # Comprobamos si el producto ya existe
                        cursor.execute("SELECT COUNT(*) FROM PRODUCTO WHERE ID_Producto = %s", (seccion["producto"],))
                        existe = cursor.fetchone()[0]
                        if existe:
                            st.warning("⚠️ El producto con ese ID ya existe.")
                        else:
                            cursor.execute("""
                                INSERT INTO PRODUCTO (
                                    ID_Producto, Nombre_producto, Descripcion, Precio,
                                    Tipo_producto, ID_Emprendimiento
                                )
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """, (
                                seccion["producto"], seccion["nombre_producto"], seccion["descripcion"],
                                seccion["precio"], seccion["tipo_producto"], id_emprendimiento
                            ))

                            con.commit()
                            st.success(f"✅ Producto #{sec_id + 1} registrado correctamente.")

                            # Limpiar la selección y reiniciar el formulario
                            st.session_state.secciones_producto[sec_id] = {
                                "id": sec_id,
                                "emprendimiento": None,
                                "producto": None,
                                "nombre_producto": "",
                                "descripcion": "",
                                "precio": 0.0,
                                "tipo_producto": "Perecedero"
                            }
                            st.experimental_rerun()

                    except Exception as e:
                        st.error(f"❌ Error al registrar el producto: {e}")

        # Agregar una nueva sección de producto
        if st.button("➕ Agregar otro producto"):
            nuevo_id = st.session_state.contador_secciones_producto
            st.session_state.secciones_producto.append({
                "id": nuevo_id,
                "emprendimiento": None,
                "producto": None,
                "nombre_producto": "",
                "descripcion": "",
                "precio": 0.0,
                "tipo_producto": "Perecedero"
            })
            st.session_state.contador_secciones_producto += 1
            st.rerun()

    except Exception as e:
        st.error(f"❌ Error al cargar los datos de emprendimientos: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'con' in locals():
            con.close()

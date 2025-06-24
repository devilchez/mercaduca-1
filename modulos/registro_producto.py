import streamlit as st
from modulos.config.conexion import obtener_conexion

def registrar_producto():
    st.header("📓 Registrar nuevo producto")

    # Inicializar flags y valores por defecto
    if "emprendimiento_seleccionado" not in st.session_state:
        st.session_state["emprendimiento_seleccionado"] = "— Selecciona —"
    if "resetear_formulario" not in st.session_state:
        st.session_state.resetear_formulario = False

    # Reiniciar valores si es necesario
    if st.session_state.resetear_formulario:
        st.session_state["id_producto"] = ""
        st.session_state["nombre_producto"] = ""
        st.session_state["descripcion"] = ""
        st.session_state["precio"] = 0.0
        st.session_state["tipo_producto"] = "Perecedero"
        st.session_state["emprendimiento_seleccionado"] = "— Selecciona —"
        st.session_state.resetear_formulario = False
        st.rerun()

    # Obtener lista de emprendimientos
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        cursor.execute("SELECT ID_Emprendimiento, Nombre_emprendimiento FROM EMPRENDIMIENTO")
        emprendimientos = cursor.fetchall()
        cursor.close()
        con.close()
    except Exception as e:
        st.error(f"❌ Error al cargar emprendimientos: {e}")
        return

    if not emprendimientos:
        st.warning("⚠️ No hay emprendimientos registrados.")
        return

    opciones = {nombre: id_ for id_, nombre in emprendimientos}
    lista_nombres = ["— Selecciona —"] + list(opciones.keys())

    if st.session_state["emprendimiento_seleccionado"] not in lista_nombres:
        st.session_state["emprendimiento_seleccionado"] = "— Selecciona —"

    seleccion = st.selectbox(
        "Selecciona un emprendimiento",
        lista_nombres,
        key="emprendimiento_seleccionado"
    )

    if seleccion == "— Selecciona —":
        st.info("🔹 Selecciona un emprendimiento para continuar.")
        st.stop()

    id_emprendimiento = opciones[seleccion]
    st.text_input("ID del Emprendimiento", value=id_emprendimiento, disabled=True)

    id_producto = st.text_input("ID del Producto", key="id_producto")
    nombre_producto = st.text_input("Nombre del producto", key="nombre_producto")
    descripcion = st.text_area("Descripción", key="descripcion")
    precio = st.number_input("Precio", min_value=0.0, step=0.01, key="precio")
    tipo_producto = st.selectbox("Tipo de producto", ["Perecedero", "No perecedero"], key="tipo_producto")

    if st.button("Registrar"):
        if not all([
            st.session_state.id_producto,
            st.session_state.nombre_producto,
            st.session_state.descripcion,
            st.session_state.precio,
            st.session_state.tipo_producto,
            id_emprendimiento
        ]):
            st.warning("⚠️ Por favor, completa todos los campos.")
        else:
            try:
                con = obtener_conexion()
                cursor = con.cursor()
                cursor.execute("""
                    INSERT INTO PRODUCTO (
                        ID_Producto, Nombre_producto, Descripcion, Precio,
                        Tipo_producto, ID_Emprendimiento
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    st.session_state.id_producto,
                    st.session_state.nombre_producto,
                    st.session_state.descripcion,
                    st.session_state.precio,
                    st.session_state.tipo_producto,
                    id_emprendimiento
                ))
                con.commit()
                st.success(f"✅ Producto registrado correctamente con ID: {st.session_state.id_producto}")

                # Activar el reinicio del formulario
                st.session_state.resetear_formulario = True
                st.rerun()

            except Exception as e:
                st.error(f"❌ Error al registrar el producto: {e}")
            finally:
                if 'cursor' in locals(): cursor.close()
                if 'con' in locals(): con.close()


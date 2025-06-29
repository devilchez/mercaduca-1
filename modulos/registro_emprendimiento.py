import streamlit as st
from modulos.config.conexion import obtener_conexion

def registrar_emprendimiento():
    if "usuario" not in st.session_state:
        st.warning("⚠️ Debes iniciar sesión.")
        st.stop()

    st.header("📓 Registrar nuevo emprendimiento")

    mensaje_placeholder = st.empty()

    # Si hay que resetear el formulario, borramos los keys antes de crear inputs
    if st.session_state.get("resetear_formulario", False):
        for key in [
            "id_emprendimiento", "nombre_emprendimiento", "nombre_emprendedor",
            "telefono", "carne_uca", "dui", "facultad", "genero", "estado", "tipo_emprendedor"
        ]:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state["resetear_formulario"] = False
        st.session_state["registro_exitoso"] = True
        st.rerun()  # Forzar recarga para aplicar limpieza

    # Inicializar valores por defecto si no existen
    defaults = {
        "id_emprendimiento": "",
        "nombre_emprendimiento": "",
        "nombre_emprendedor": "",
        "telefono": "",
        "carne_uca": "",
        "dui": "",
        "facultad": "Facultad de Ciencias Económicas y Empresariales",
        "genero": "Femenino",
        "estado": "Activo",
        "tipo_emprendedor": "Estudiante",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

    # Crear formulario con keys en session_state
    id_emprendimiento = st.text_input("ID del Emprendimiento", key="id_emprendimiento")
    nombre_emprendimiento = st.text_input("Nombre del emprendimiento", key="nombre_emprendimiento")
    nombre_emprendedor = st.text_input("Nombre del emprendedor", key="nombre_emprendedor")
    telefono = st.text_input("Teléfono", key="telefono")
    carne_uca = st.text_input("Carné UCA", max_chars=10, key="carne_uca")
    dui = st.text_input("DUI", max_chars=9, key="dui")
    facultad = st.selectbox("Facultad", [
        "Facultad de Ciencias Económicas y Empresariales",
        "Facultad de Ciencias Sociales y Humanidades",
        "Facultad de Ingeniería y Arquitectura"
    ], index=[
        "Facultad de Ciencias Económicas y Empresariales",
        "Facultad de Ciencias Sociales y Humanidades",
        "Facultad de Ingeniería y Arquitectura"
    ].index(st.session_state["facultad"]), key="facultad")
    genero = st.selectbox("Género", ["Femenino", "Masculino", "Otro"],
                          index=["Femenino", "Masculino", "Otro"].index(st.session_state["genero"]), key="genero")
    estado = st.selectbox("Estado", ["Activo", "Inactivo"],
                          index=["Activo", "Inactivo"].index(st.session_state["estado"]), key="estado")
    tipo_emprendedor = st.selectbox("Tipo de Emprendedor", ["Estudiante", "Egresado", "Colaborador"],
                                    index=["Estudiante", "Egresado", "Colaborador"].index(st.session_state["tipo_emprendedor"]),
                                    key="tipo_emprendedor")

    if st.button("Registrar"):
        if not (id_emprendimiento and nombre_emprendimiento and nombre_emprendedor and carne_uca and dui):
            mensaje_placeholder.warning("⚠️ Por favor, completa todos los campos.")
        else:
            try:
                con = obtener_conexion()
                cursor = con.cursor()
                cursor.execute("""
                    INSERT INTO EMPRENDIMIENTO (
                        ID_Emprendimiento, Nombre_emprendimiento, Nombre_emprendedor,
                        Telefono, carne_uca, dui, facultad, genero, Estado, tipo_emprendedor
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    id_emprendimiento, nombre_emprendimiento, nombre_emprendedor,
                    telefono, carne_uca, dui, facultad, genero, estado, tipo_emprendedor
                ))
                con.commit()
                cursor.close()
                con.close()

                # Activar reinicio del formulario y recargar la app
                st.session_state.resetear_formulario = True
                st.rerun()

            except Exception as e:
                mensaje_placeholder.error(f"❌ Error al registrar: {e}")

    # Mostrar mensaje de éxito sólo una vez, justo debajo del botón
    if st.session_state.get("registro_exitoso", False):
        mensaje_placeholder.success("✅ Emprendimiento registrado correctamente.")
        st.session_state["registro_exitoso"] = False

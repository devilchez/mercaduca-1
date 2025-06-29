import streamlit as st
from modulos.config.conexion import obtener_conexion

def registrar_emprendimiento():
    if "usuario" not in st.session_state:
        st.warning("⚠️ Debes iniciar sesión.")
        st.stop()

    st.header("📓 Registrar nuevo emprendimiento")

    # Inicializar keys si no existen
    if "id_emprendimiento" not in st.session_state:
        st.session_state["id_emprendimiento"] = ""
    if "nombre_emprendimiento" not in st.session_state:
        st.session_state["nombre_emprendimiento"] = ""
    if "nombre_emprendedor" not in st.session_state:
        st.session_state["nombre_emprendedor"] = ""
    if "telefono" not in st.session_state:
        st.session_state["telefono"] = ""
    if "carne_uca" not in st.session_state:
        st.session_state["carne_uca"] = ""
    if "dui" not in st.session_state:
        st.session_state["dui"] = ""
    if "facultad" not in st.session_state:
        st.session_state["facultad"] = "Facultad de Ciencias Económicas y Empresariales"
    if "genero" not in st.session_state:
        st.session_state["genero"] = "Femenino"
    if "estado" not in st.session_state:
        st.session_state["estado"] = "Activo"
    if "tipo_emprendedor" not in st.session_state:
        st.session_state["tipo_emprendedor"] = "Estudiante"
    if "registro_exitoso" not in st.session_state:
        st.session_state["registro_exitoso"] = False

    mensaje_placeholder = st.empty()

    # Crear formulario con valores en session_state
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
    ], index=["Facultad de Ciencias Económicas y Empresariales",
              "Facultad de Ciencias Sociales y Humanidades",
              "Facultad de Ingeniería y Arquitectura"].index(st.session_state["facultad"]), key="facultad")
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

                # Limpiar los valores en session_state para limpiar formulario sin rerun
                st.session_state["id_emprendimiento"] = ""
                st.session_state["nombre_emprendimiento"] = ""
                st.session_state["nombre_emprendedor"] = ""
                st.session_state["telefono"] = ""
                st.session_state["carne_uca"] = ""
                st.session_state["dui"] = ""
                st.session_state["facultad"] = "Facultad de Ciencias Económicas y Empresariales"
                st.session_state["genero"] = "Femenino"
                st.session_state["estado"] = "Activo"
                st.session_state["tipo_emprendedor"] = "Estudiante"
                st.session_state["registro_exitoso"] = True

            except Exception as e:
                mensaje_placeholder.error(f"❌ Error al registrar: {e}")
            finally:
                if 'cursor' in locals(): cursor.close()
                if 'con' in locals(): con.close()

    if st.session_state["registro_exitoso"]:
        mensaje_placeholder.success("✅ Emprendimiento registrado correctamente.")
        st.session_state["registro_exitoso"] = False


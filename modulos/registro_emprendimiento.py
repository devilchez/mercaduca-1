import streamlit as st
from modulos.config.conexion import obtener_conexion

def registrar_emprendimiento():
    if "usuario" not in st.session_state:
        st.warning("⚠️ Debes iniciar sesión.")
        st.stop()

    st.header("📓 Registrar nuevo emprendimiento")

    # Formulario con keys
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
    ], key="facultad")
    genero = st.selectbox("Género", ["Femenino", "Masculino", "Otro"], key="genero")
    estado = st.selectbox("Estado", ["Activo", "Inactivo"], key="estado")
    tipo_emprendedor = st.selectbox("Tipo de Emprendedor", ["Estudiante", "Egresado", "Colaborador"], key="tipo_emprendedor")

    # Este contenedor es clave: asegura que el mensaje quede justo debajo del botón
    mensaje_placeholder = st.empty()

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

                # ✅ Guardar bandera de éxito para próxima recarga
                st.session_state["registro_exitoso"] = True
                st.rerun()

            except Exception as e:
                mensaje_placeholder.error(f"❌ Error al registrar: {e}")
            finally:
                if 'cursor' in locals(): cursor.close()
                if 'con' in locals(): con.close()

    # ✅ Mostrar mensaje de éxito justo debajo del botón, después del rerun
    if st.session_state.get("registro_exitoso"):
        mensaje_placeholder.success("✅ Emprendimiento registrado correctamente.")
        st.session_state["registro_exitoso"] = False

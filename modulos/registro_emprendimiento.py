import streamlit as st
from modulos.config.conexion import obtener_conexion

def registrar_emprendimiento():
    if "usuario" not in st.session_state:
        st.warning("⚠️ Debes iniciar sesión.")
        st.stop()

    st.header("📓 Registrar nuevo emprendimiento")

    # Formulario
    id_emprendimiento = st.text_input("ID del Emprendimiento")
    nombre_emprendimiento = st.text_input("Nombre del emprendimiento")
    nombre_emprendedor = st.text_input("Nombre del emprendedor")
    telefono = st.text_input("Teléfono")
    carne_uca = st.text_input("Carné UCA", max_chars=10)
    dui = st.text_input("DUI (máximo 10 dígitos)", max_chars=10)
    facultad = st.selectbox("Facultad", [
        "Facultad de Ciencias Económicas y Empresariales",
        "Facultad de Ciencias Sociales y Humanidades",
        "Facultad de Ingeniería y Arquitectura"
    ])
    genero = st.selectbox("Género", ["Femenino", "Masculino"])
    estado = st.selectbox("Estado", ["Activo", "Inactivo"])

    if st.button("Registrar"):
        if not (id_emprendimiento and nombre_emprendimiento and nombre_emprendedor and carne_uca and dui and facultad and genero and estado):
            st.warning("⚠️ Por favor, completa todos los campos.")
        else:
            try:
                con = obtener_conexion()
                cursor = con.cursor()

                # Insertar en EMPRENDIMIENTO
                cursor.execute("""
                    INSERT INTO EMPRENDIMIENTO (
                        ID_Emprendimiento, Nombre_emprendimiento, Nombre_emprendedor,
                        Telefono,, carne_uca, dui, facultad, genero, Estado
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    id_emprendimiento, nombre_emprendimiento, nombre_emprendedor,
                    telefono, carne_uca, dui, facultad, genero, estado
                ))

                con.commit()
                st.success("✅ Emprendimiento registrado correctamente.")

            except Exception as e:
                st.error(f"❌ Error al registrar: {e}")
            finally:
                if 'cursor' in locals(): cursor.close()
                if 'con' in locals(): con.close()


import streamlit as st
from modulos.config.conexion import obtener_conexion

def registrar_emprendedor():
    if "usuario" not in st.session_state:
        st.warning("⚠️ Debes iniciar sesión.")
        st.stop()

    st.header("Registrar nuevo emprendedor")

    # Formulario
    nombre = st.text_input("Nombre")
    apellido = st.text_input("Apellido")
    correo = st.text_input("Correo electrónico")
    telefono = st.text_input("Teléfono")
    nombre_emprendimiento = st.text_input("Nombre del emprendimiento")

    if st.button("Registrar"):
        if not (nombre and apellido and correo and telefono and nombre_emprendimiento):
            st.warning("⚠️ Por favor, completa todos los campos.")
        else:
            try:
                con = obtener_conexion()
                cursor = con.cursor()

                # Insertar en EMPRENDEDOR
                cursor.execute("""
                    INSERT INTO REGISTRO (Nombre, Apellido, Correo, Telefono)
                    VALUES (%s, %s, %s, %s)
                """, (nombre, apellido, correo, telefono))
                id_emprendedor = cursor.lastrowid

                # Insertar en EMPRENDIMIENTO
                cursor.execute("""
                    INSERT INTO EMPRENDIMIENTO (ID_Emprendedor, Nombre_emprendimiento)
                    VALUES (%s, %s)
                """, (id_emprendedor, nombre_emprendimiento))

                con.commit()
                st.success("✅ Emprendedor registrado correctamente.")

            except Exception as e:
                st.error(f"❌ Error al registrar: {e}")
            finally:
                if 'cursor' in locals(): cursor.close()
                if 'con' in locals(): con.close()

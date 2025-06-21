import streamlit as st
from modulos.config.conexion import obtener_conexion

def registrar_emprendimiento():
    if "usuario" not in st.session_state:
        st.warning("⚠️ Debes iniciar sesión.")
        st.stop()

    st.header("Registrar nuevo emprendimiento")

    # Formulario
    id_emprendimiento = st.text_input("ID del Emprendimiento")
    nombre_emprendimiento = st.text_input("Nombre del emprendimiento")
    nombre_emprendedor = st.text_input("Nombre del emprendedor")
    telefono = st.text_input("Teléfono")
    cuenta_bancaria = st.text_input("Cuenta bancaria")
    estado = st.selectbox("Estado", ["Activo", "Inactivo"])

    if st.button("Registrar"):
        if not (id_emprendimiento and nombre_emprendimiento and nombre_emprendedor and telefono and cuenta_bancaria and estado):
            st.warning("⚠️ Por favor, completa todos los campos.")
        else:
            try:
                con = obtener_conexion()
                cursor = con.cursor()

                # Insertar en EMPRENDIMIENTO
                cursor.execute("""
                    INSERT INTO EMPRENDIMIENTO (ID_Emprendimiento, Nombre_emprendimiento, Nombre_emprendedor, Telefono, Cuenta_bancaria, Estado)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (id_emprendimiento, nombre_emprendimiento, nombre_emprendedor, telefono, cuenta_bancaria, estado))

                con.commit()
                st.success("✅ Emprendimiento registrado correctamente.")

            except Exception as e:
                st.error(f"❌ Error al registrar: {e}")
            finally:
                if 'cursor' in locals(): cursor.close()
                if 'con' in locals(): con.close()

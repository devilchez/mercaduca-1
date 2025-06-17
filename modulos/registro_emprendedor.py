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

                cursor.execute("""
                    INSERT INTO registro (Nombre, Apellido, Correo, telefono, Nombre_emprendimiento)
                    VALUES (%s, %s, %s, %s, %s)
                """, (nombre, apellido, correo, telefono, nombre_emprendimiento))

                con.commit()
                st.success("✅ Emprendedor registrado correctamente.")

            except Exception as e:
                st.error(f"❌ Error al registrar: {e}")
            finally:
                if 'cursor' in locals(): cursor.close()
                if 'con' in locals(): con.close()

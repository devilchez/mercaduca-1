def mostrar_emprendimientos():
    """Muestra la tabla de EMPRENDIMIENTOS para permitir edición y eliminación."""
    st.header("📋 Emprendimientos registrados")

    df = obtener_emprendimientos()
    if df.empty:
        st.info("No hay emprendimientos registrados.")
        return

    # Filtro por nombre del emprendimiento con barra buscadora
    nombres_unicos = df["Nombre_emprendimiento"].unique()
    nombre_seleccionado = st.selectbox(
        "🔍 Buscar emprendimiento por nombre:",
        options=["Todos"] + sorted(nombres_unicos.tolist()),
        index=0
    )

    if nombre_seleccionado != "Todos":
        df = df[df["Nombre_emprendimiento"] == nombre_seleccionado]

    # Agregamos columna para eliminar
    df["Eliminar"] = False
    edited_df = st.data_editor(df, num_rows="fixed", use_container_width=True, key="editor_emprendimientos")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Guardar Cambios"):
            actualizar_emprendimiento(edited_df.drop(columns=["Eliminar"]))

    with col2:
        if st.button("🗑️ Eliminar seleccionados"):
            ids_a_eliminar = edited_df[edited_df["Eliminar"] == True]["ID_Emprendimiento"].tolist()
            if ids_a_eliminar:
                eliminar_emprendimientos(ids_a_eliminar)
            else:
                st.info("Selecciona al menos un emprendimiento para eliminar.")


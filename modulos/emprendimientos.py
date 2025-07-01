import streamlit as st
import pandas as pd
from modulos.config.conexion import obtener_conexion

def obtener_emprendimientos():
    try:
        con = obtener_conexion()
        df = pd.read_sql("SELECT * FROM EMPRENDIMIENTO", con)
        con.close()
        return df
    except Exception as e:
        st.error(f"❌ Error al obtener datos: {e}")
        return pd.DataFrame()

def actualizar_emprendimiento(original_df, edited_df):
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        registros_actualizados = 0

        for i in range(len(edited_df)):
            row_editada = edited_df.iloc[i]
            row_original = original_df.iloc[i]

            if not row_editada.equals(row_original):
                cursor.execute("""
                    UPDATE EMPRENDIMIENTO 
                    SET Nombre_emprendimiento=%s,
                        Nombre_emprendedor=%s,
                        Telefono=%s,
                        Estado=%s,
                        carne_uca=%s,
                        dui=%s,
                        facultad=%s,
                        genero=%s,
                        Tipo_emprendedor=%s
                    WHERE ID_Emprendimiento=%s
                """, (
                    row_editada.get("Nombre_emprendimiento"),
                    row_editada.get("Nombre_emprendedor"),
                    row_editada.get("Telefono"),
                    row_editada.get("Estado"),
                    row_editada.get("carne_uca"),
                    row_editada.get("dui"),
                    row_editada.get("facultad"),
                    row_editada.get("genero"),
                    row_editada.get("Tipo_emprendedor"),
                    row_editada.get("ID_Emprendimiento")
                ))
                registros_actualizados += cursor.rowcount

        con.commit()
        cursor.close()
        con.close()

        if registros_actualizados > 0:
            st.success(f"✅ {registros_actualizados} registro(s) actualizado(s).")
        else:
            st.info("⚠️ No hubo cambios detectados.")
    except Exception as e:
        st.error(f"❌ Error al actualizar: {e}")

def eliminar_emprendimientos(ids_a_eliminar):
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        formato_ids = ','.join(['%s'] * len(ids_a_eliminar))
        sql = f"DELETE FROM EMPRENDIMIENTO WHERE ID_Emprendimiento IN ({formato_ids})"
        cursor.execute(sql, tuple(ids_a_eliminar))
        registros_eliminados = cursor.rowcount

        con.commit()
        cursor.close()
        con.close()

        if registros_eliminados > 0:
            st.success(f"🗑️ Se eliminaron {registros_eliminados} emprendimiento(s).")
        else:
            st.warning("⚠️ No se eliminó ningún registro.")
    except Exception as e:
        st.error(f"❌ Error al eliminar: {e}")

def mostrar_emprendimientos():
    st.header("📋 Emprendimientos registrados")

    # Cargar datos originales y congelarlos antes de editar
    df_original = obtener_emprendimientos()
    if df_original.empty:
        st.info("No hay emprendimientos registrados.")
        return

    # Filtro de búsqueda
    nombres_unicos = df_original["Nombre_emprendimiento"].dropna().unique()
    nombre_seleccionado = st.selectbox(
        "🔍 Buscar emprendimiento por nombre:",
        options=["Todos"] + sorted(nombres_unicos.tolist()),
        index=0
    )

    df_filtrado = df_original.copy()
    if nombre_seleccionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Nombre_emprendimiento"] == nombre_seleccionado]

    df_filtrado = df_filtrado.reset_index(drop=True)
    df_filtrado["Eliminar"] = False

    # Copia antes de editar (sin columna de eliminar)
    df_congelado = df_filtrado.drop(columns=["Eliminar"]).copy()

    # Editor de datos
    edited_df = st.data_editor(
        df_filtrado,
        num_rows="fixed",
        use_container_width=True,
        key="editor_emprendimientos"
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Guardar Cambios"):
            actualizar_emprendimiento(
                df_congelado,
                edited_df.drop(columns=["Eliminar"])
            )

    with col2:
        if st.button("🗑️ Eliminar seleccionados"):
            ids_a_eliminar = edited_df[edited_df["Eliminar"] == True]["ID_Emprendimiento"].tolist()
            if ids_a_eliminar:
                eliminar_emprendimientos(ids_a_eliminar)
                st.experimental_rerun()  # Solo recarga si elimina
            else:
                st.info("Selecciona al menos un emprendimiento para eliminar.")

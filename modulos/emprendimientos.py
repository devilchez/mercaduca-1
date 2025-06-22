import streamlit as st
import pandas as pd
from modulos.config.conexion import obtener_conexion

def obtener_emprendimientos():
    """Obtiene todos los registros de EMPRENDIMIENTO de la base de datos."""
    con = obtener_conexion()
    df = pd.read_sql("SELECT * FROM EMPRENDIMIENTO", con)
    con.close()
    return df

def actualizar_emprendimiento(df):
    """Actualiza los registros de EMPRENDIMIENTO en la base de datos."""
    con = obtener_conexion()
    cursor = con.cursor()
    registros_actualizados = 0

    for _, row in df.iterrows():
        cursor.execute("""
            UPDATE EMPRENDIMIENTO 
            SET Nombre_emprendimiento=%s,
                Nombre_emprendedor=%s,
                Telefono=%s,
                Cuenta_bancaria=%s,
                Estado=%s
            WHERE ID_Emprendimiento=%s
        """, (
            str(row["Nombre_emprendimiento"]),
            str(row["Nombre_emprendedor"]),
            str(row["Telefono"]),
            str(row["Cuenta_bancaria"]),
            str(row["Estado"]),
            str(row["ID_Emprendimiento"])
        ))

        registros_actualizados += cursor.rowcount

    con.commit()
    con.close()

    if registros_actualizados > 0:
        st.success(f"✅ Cambios guardados correctamente ({registros_actualizados} registro(s) actualizado(s)).")
    else:
        st.warning("⚠️ No hubo registros actualizados. Verifica que los ID coincidan.")

def mostrar_emprendimientos():
    """Muestra la tabla de EMPRENDIMIENTOS para permitir la edición."""
    st.header("Emprendimientos registrados")
    df = obtener_emprendimientos()
    edited_df = st.data_editor(df, num_rows="fixed")
    if st.button("Guardar Cambios"):
        actualizar_emprendimiento(edited_df)

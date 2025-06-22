import streamlit as st
import pandas as pd
from modulos.config.conexion import obtener_conexion

def obtener_emprendimientos():
    con = obtener_conexion()
    df = pd.read_sql("SELECT * FROM EMPRENDIMIENTO", con)
    con.close()
    return df

def actualizar_emprendimiento(df):
    con = obtener_conexion()
    cursor = con.cursor()
    for _, row in df.iterrows():
        cursor.execute("""
            UPDATE EMPRENDIMIENTO 
            SET Nombre_emprendimiento=%s, Nombre_emprendedor=%s, Telefono=%s, Cuenta_bancaria=%s, Estado=%s 
            WHERE ID_Emprendimiento=%s
        """, (row["Nombre_emprendimiento"], row["Nombre_emprendedor"], row["Telefono"], 
              row["Cuenta_bancaria"], row["Estado"], row["ID_Emprendimiento"]))
    con.commit()
    con.close()
    st.success("✅ Cambios guardados correctamente.")

def mostrar_emprendimientos():
    st.header("Emprendimientos registrados")
    df = obtener_emprendimientos()
    edited_df = st.data_editor(df, num_rows="fixed")
    if st.button("Guardar Cambios"):
        actualizar_emprendimiento(edited_df)

# Llama esta funcion al final de tu flujo de registro para mostrar y permitir la edición.
mostrar_emprendimientos()

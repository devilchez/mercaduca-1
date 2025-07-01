import streamlit as st
import pandas as pd
from modulos.config.conexion import obtener_conexion

def obtener_productos():
    """Obtiene los productos junto con el nombre del emprendimiento."""
    con = obtener_conexion()
    df = pd.read_sql("""
        SELECT 
            p.ID_Producto,
            p.Nombre_producto,
            p.Descripcion,
            p.Precio,
            p.Tipo_producto,
            p.ID_Emprendimiento,
            e.nombre_emprendimiento
        FROM PRODUCTO p
        JOIN EMPRENDIMIENTO e ON p.ID_Emprendimiento = e.ID_Emprendimiento
    """, con)
    con.close()
    return df

def actualizar_productos(df):
    """Actualiza los registros de PRODUCTO en la base de datos."""
    con = obtener_conexion()
    cursor = con.cursor()
    registros_actualizados = 0

    for _, row in df.iterrows():
        cursor.execute("""
            UPDATE PRODUCTO 
            SET Nombre_producto=%s,
                Descripcion=%s,
                Precio=%s,
                Tipo_producto=%s,
                ID_Emprendimiento=%s
            WHERE ID_Producto=%s
        """, (
            str(row["Nombre_producto"]),
            str(row["Descripcion"]),
            float(row["Precio"]),
            str(row["Tipo_producto"]),
            str(row["ID_Emprendimiento"]),
            str(row["ID_Producto"])
        ))
        registros_actualizados += cursor.rowcount

    con.commit()
    con.close()

    if registros_actualizados > 0:
        st.success(f"✅ Cambios guardados correctamente ({registros_actualizados} registro(s) actualizado(s)).")
    else:
        st.warning("⚠️ No hubo registros actualizados. Verifica que los ID coincidan.")

def mostrar_productos():
    """Muestra la tabla de PRODUCTO para edición con filtro por nombre del emprendimiento."""
    st.header("📋 Productos registrados")

    df = obtener_productos()
    if df.empty:
        st.info("No hay productos registrados.")
        return

    # Filtro por nombre del emprendimiento
    nombres_emprendimientos = df["nombre_emprendimiento"].dropna().unique()
    if len(nombres_emprendimientos) > 0:
        seleccionado = st.selectbox(
            "🏢 Buscar producto por nombre del emprendimiento:",
            options=["Todos"] + sorted(nombres_emprendimientos.tolist()),
            index=0
        )

        if seleccionado != "Todos":
            df = df[df["nombre_emprendimiento"] == seleccionado]

    # Editor de tabla
    edited_df = st.data_editor(
        df.drop(columns=["nombre_emprendimiento"]),  # evitamos editar nombre_emprendimiento directamente
        num_rows="fixed",
        use_container_width=True,
        key="editor_productos"
    )

    if st.button("💾 Guardar Cambios"):
        actualizar_productos(edited_df)

# Para ejecución directa
if __name__ == "__main__":
    mostrar_productos()


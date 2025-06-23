import streamlit as st
import pandas as pd
from datetime import datetime
from modulos.config.conexion import obtener_conexion

def mostrar_inventario():
    st.header("📦 Módulo de Inventario")

    # Filtros de fecha
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Desde", value=datetime.today().replace(day=1))
    with col2:
        fecha_fin = st.date_input("Hasta", value=datetime.today())

    if fecha_inicio > fecha_fin:
        st.warning("⚠️ La fecha de inicio no puede ser mayor que la fecha de fin.")
        return

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Mostrar productos abastecidos filtrados por fecha
        cursor.execute("""
            SELECT e.Nombre_emprendimiento, p.Nombre_producto, i.Cantidad_ingresada, i.Fecha_ingreso
            FROM INVENTARIO i
            JOIN PRODUCTO p ON i.ID_Producto = p.ID_Producto
            JOIN EMPRENDIMIENTO e ON p.ID_Emprendimiento = e.ID_Emprendimiento
            WHERE DATE(i.Fecha_ingreso) BETWEEN %s AND %s
            ORDER BY i.Fecha_ingreso DESC
        """, (fecha_inicio, fecha_fin))
        datos_abastecidos = cursor.fetchall()

        if datos_abastecidos:
            df_abastecidos = pd.DataFrame(datos_abastecidos, columns=["Emprendimiento", "Producto", "Cantidad Abastecida", "Fecha de Abastecimiento"])
            st.subheader("📥 Productos Abastecidos (Filtrados por Fecha)")
            st.dataframe(df_abastecidos)
        else:
            st.info("No se encontraron productos abastecidos en el rango seleccionado.")

        # Mostrar stock actual (sin filtrar por fecha, porque es el stock total restante)
        cursor.execute("""
            SELECT e.Nombre_emprendimiento, p.Nombre_producto, SUM(i.Stock) AS Stock_Disponible
            FROM INVENTARIO i
            JOIN PRODUCTO p ON i.ID_Producto = p.ID_Producto
            JOIN EMPRENDIMIENTO e ON p.ID_Emprendimiento = e.ID_Emprendimiento
            GROUP BY e.Nombre_emprendimiento, p.Nombre_producto
            ORDER BY e.Nombre_emprendimiento, p.Nombre_producto
        """)
        datos_stock = cursor.fetchall()

        if datos_stock:
            df_stock = pd.DataFrame(datos_stock, columns=["Emprendimiento", "Producto", "Stock Disponible"])
            st.subheader("📦 Stock Actual")
            st.dataframe(df_stock)
        else:
            st.info("No hay stock disponible registrado.")

    except Exception as e:
        st.error(f"❌ Error al cargar el inventario: {e}")

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'con' in locals(): con.close()

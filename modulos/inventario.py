import streamlit as st
import pandas as pd
from modulos.config.conexion import obtener_conexion

def mostrar_inventario():
    st.header("📦 Módulo de Inventario")

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Mostrar productos abastecidos por emprendimiento (Cantidad ingresada)
        cursor.execute("""
            SELECT e.Nombre_emprendimiento, p.Nombre_producto, SUM(i.Cantidad_ingresada) AS Cantidad_Abastecida
            FROM INVENTARIO i
            JOIN PRODUCTO p ON i.ID_Producto = p.ID_Producto
            JOIN EMPRENDIMIENTO e ON p.ID_Emprendimiento = e.ID_Emprendimiento
            GROUP BY e.Nombre_emprendimiento, p.Nombre_producto
            ORDER BY e.Nombre_emprendimiento, p.Nombre_producto
        """)
        datos_abastecidos = cursor.fetchall()

        if datos_abastecidos:
            df_abastecidos = pd.DataFrame(datos_abastecidos, columns=["Emprendimiento", "Producto", "Cantidad Abastecida"])
            st.subheader("📥 Productos Abastecidos")
            st.dataframe(df_abastecidos)
        else:
            st.info("No se han registrado productos abastecidos aún.")

        # Mostrar stock actual
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

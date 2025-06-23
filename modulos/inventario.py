import streamlit as st
import pandas as pd
from modulos.config.conexion import obtener_conexion

def mostrar_inventario():
    st.header("📦 Módulo de Inventario")

    try:
        # Conexión a la base de datos
        con = obtener_conexion()
        cursor = con.cursor()

        # Consulta para obtener los productos abastecidos por emprendimiento
        query_abastecimiento = """
            SELECT e.Nombre_emprendimiento, p.Nombre_producto, SUM(a.cantidad) AS cantidad_abastecida
            FROM ABASTECIMIENTO a
            JOIN PRODUCTO p ON a.ID_Producto = p.ID_Producto
            JOIN EMPRENDIMIENTO e ON p.ID_Emprendimiento = e.ID_Emprendimiento
            GROUP BY e.Nombre_emprendimiento, p.Nombre_producto
            ORDER BY e.Nombre_emprendimiento, p.Nombre_producto
        """
        cursor.execute(query_abastecimiento)
        rows_abastecimiento = cursor.fetchall()

        # Si no hay productos abastecidos
        if not rows_abastecimiento:
            st.info("No se encontraron productos abastecidos.")
            return

        # Crear DataFrame para los productos abastecidos
        df_abastecimiento = pd.DataFrame(rows_abastecimiento, columns=["Emprendimiento", "Producto", "Cantidad Abastecida"])
        st.subheader("Productos Abastecidos")
        st.dataframe(df_abastecimiento)

        # Consulta para obtener el stock disponible (ventas ya registradas)
        query_ventas = """
            SELECT e.Nombre_emprendimiento, p.Nombre_producto, SUM(pv.cantidad) AS cantidad_vendida
            FROM PRODUCTOXVENTA pv
            JOIN PRODUCTO p ON pv.ID_Producto = p.ID_Producto
            JOIN VENTA v ON pv.ID_Venta = v.ID_Venta
            JOIN EMPRENDIMIENTO e ON p.ID_Emprendimiento = e.ID_Emprendimiento
            GROUP BY e.Nombre_emprendimiento, p.Nombre_producto
            ORDER BY e.Nombre_emprendimiento, p.Nombre_producto
        """
        cursor.execute(query_ventas)
        rows_ventas = cursor.fetchall()

        # Si no hay ventas registradas
        if not rows_ventas:
            st.info("No se han registrado ventas.")
            return

        # Crear DataFrame para las ventas
        df_ventas = pd.DataFrame(rows_ventas, columns=["Emprendimiento", "Producto", "Cantidad Vendida"])

        # Unir ambas tablas para mostrar el stock
        df_inventario = pd.merge(df_abastecimiento, df_ventas, on=["Emprendimiento", "Producto"], how="left")
        df_inventario["Cantidad Vendida"].fillna(0, inplace=True)
        df_inventario["Stock Restante"] = df_inventario["Cantidad Abastecida"] - df_inventario["Cantidad Vendida"]

        st.subheader("Stock Restante después de Ventas")
        st.dataframe(df_inventario)

    except Exception as e:
        st.error(f"❌ Error al cargar el inventario: {e}")
    
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'con' in locals(): con.close()

# Llamar a la función que muestra el inventario
mostrar_inventario()

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from modulos.config.conexion import obtener_conexion

def mostrar_inventario():
    st.header("📟 Inventario")

    # Filtros de fecha para productos abastecidos
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

        # 📥 Productos abastecidos
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

        # 📦 Stock actual
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

        # 📅 Productos próximos a vencer
        fecha_limite = datetime.today() + timedelta(days=30)

        cursor.execute("""
            SELECT e.Nombre_emprendimiento, p.Nombre_producto, 
                   i.Stock AS Stock_Disponible,
                   i.Fecha_vencimiento
            FROM INVENTARIO i
            JOIN PRODUCTO p ON i.ID_Producto = p.ID_Producto
            JOIN EMPRENDIMIENTO e ON p.ID_Emprendimiento = e.ID_Emprendimiento
            WHERE i.Fecha_vencimiento BETWEEN NOW() AND %s
              AND (i.Cantidad_ingresada - i.Cantidad_salida) > 0
            ORDER BY i.Fecha_vencimiento ASC
        """, (fecha_limite,))
        productos_proximos_vencer = cursor.fetchall()

        if productos_proximos_vencer:
            df_proximos_vencer = pd.DataFrame(productos_proximos_vencer, columns=["Emprendimiento", "Producto", "Stock Disponible", "Fecha de Vencimiento"])
            st.subheader("📅 Productos Próximos a Vencer (Próximos 30 días)")
            st.dataframe(df_proximos_vencer)
        else:
            st.info("No hay productos próximos a vencer en los próximos 30 días.")

    except Exception as e:
        st.error(f"❌ Error al cargar el inventario: {e}")

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'con' in locals(): con.close()

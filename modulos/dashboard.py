import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from modulos.config.conexion import obtener_conexion

def dashboard():
    st.header("📊 Dashboard de Ventas y Emprendimientos")

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Filtro de fechas dentro del módulo
        col1, col2 = st.columns(2)
        with col1:
            fecha_inicio = st.date_input("Desde", value=datetime.today().replace(day=1).date())
        with col2:
            fecha_fin = st.date_input("Hasta", value=datetime.today().date())

        if fecha_inicio > fecha_fin:
            st.warning("⚠️ La fecha de inicio no puede ser mayor que la fecha de fin.")
            return

        # Construir filtro de fecha para consultas de ventas
        filtro_fecha = ""
        params = (fecha_inicio, fecha_fin)
        filtro_fecha = "WHERE v.Fecha_venta BETWEEN %s AND %s"

        # ================== 💵 Ventas por Emprendedor ==================
        st.subheader("📈 Ventas por Emprendedor")
        query_ventas_emprendedor = f"""
            SELECT e.Nombre_emprendimiento, p.Nombre_producto, SUM(pxv.cantidad * pxv.precio_unitario) AS Total_Ventas
            FROM PRODUCTOXVENTA pxv
            JOIN VENTA v ON pxv.ID_Venta = v.ID_Venta
            JOIN PRODUCTO p ON pxv.ID_Producto = p.ID_Producto
            JOIN EMPRENDIMIENTO e ON p.ID_Emprendimiento = e.ID_Emprendimiento
            {filtro_fecha}
            GROUP BY e.Nombre_emprendimiento, p.Nombre_producto
            ORDER BY Total_Ventas DESC
        """
        cursor.execute(query_ventas_emprendedor, params)
        ventas_emprendedor = cursor.fetchall()

        if ventas_emprendedor:
            df_ventas_emprendedor = pd.DataFrame(ventas_emprendedor, columns=["Emprendimiento", "Producto", "Total Ventas ($)"])
            fig_ventas_emprendedor = px.bar(df_ventas_emprendedor, x="Emprendimiento", y="Total Ventas ($)", color="Producto", title="Ventas por Emprendedor y Producto")
            st.plotly_chart(fig_ventas_emprendedor, use_container_width=True)
        else:
            st.info("No se encontraron ventas por emprendedor en el rango seleccionado.")

        # ================== 🏪 Top Emprendedores por Ganancia ==================
        st.subheader("🏆 Top Emprendedores por Ganancia")
        query_top_emprendedores = f"""
            SELECT e.Nombre_emprendimiento, SUM(pxv.cantidad * pxv.precio_unitario) AS Total_Ganancia
            FROM PRODUCTOXVENTA pxv
            JOIN VENTA v ON pxv.ID_Venta = v.ID_Venta
            JOIN PRODUCTO p ON pxv.ID_Producto = p.ID_Producto
            JOIN EMPRENDIMIENTO e ON p.ID_Emprendimiento = e.ID_Emprendimiento
            {filtro_fecha}
            GROUP BY e.Nombre_emprendimiento
            ORDER BY Total_Ganancia DESC
        """
        cursor.execute(query_top_emprendedores, params)
        top_emprendedores = cursor.fetchall()

        if top_emprendedores:
            df_top_emprendedores = pd.DataFrame(top_emprendedores, columns=["Emprendimiento", "Total Ganancia ($)"])
            fig_top_emprendedores = px.bar(df_top_emprendedores, x="Emprendimiento", y="Total Ganancia ($)", title="Top Emprendedores por Ganancia")
            st.plotly_chart(fig_top_emprendedores, use_container_width=True)
        else:
            st.info("No se encontraron datos de ganancias por emprendedor.")

        # ================== 📊 Distribución por Tipo de Emprendedor (Pie Chart) ==================
        st.subheader("🗺 Distribución por Tipo de Emprendedor")
        query_tipo_emprendedor = """
            SELECT Tipo_emprendedor, COUNT(*) AS Total
            FROM EMPRENDIMIENTO
            GROUP BY Tipo_emprendedor
        """
        cursor.execute(query_tipo_emprendedor)
        tipo_emprendedor_data = cursor.fetchall()

        if tipo_emprendedor_data:
            df_tipo_emprendedor = pd.DataFrame(tipo_emprendedor_data, columns=["Tipo de Emprendedor", "Cantidad"])
            fig_tipo_emprendedor = px.pie(df_tipo_emprendedor, names="Tipo de Emprendedor", values="Cantidad", title="Distribución por Tipo de Emprendedor")
            st.plotly_chart(fig_tipo_emprendedor, use_container_width=True)
        else:
            st.info("No se encontraron datos de tipos de emprendedores.")

    except Exception as e:
        st.error(f"❌ Error al cargar el dashboard: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'con' in locals():
            con.close()

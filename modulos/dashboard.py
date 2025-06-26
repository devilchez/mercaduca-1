import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from modulos.config.conexion import obtener_conexion

def dashboard(fecha_inicio=None, fecha_fin=None, emprendimiento_filtro=None):
    st.header("📊 Dashboard de Ventas y Emprendimientos")

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Construir filtro fecha para ventas mensuales
        filtro_fecha = ""
        params = ()
        if fecha_inicio and fecha_fin:
            filtro_fecha = "WHERE v.Fecha_venta BETWEEN %s AND %s"
            params = (fecha_inicio, fecha_fin)
        elif fecha_inicio:
            filtro_fecha = "WHERE v.Fecha_venta >= %s"
            params = (fecha_inicio,)
        elif fecha_fin:
            filtro_fecha = "WHERE v.Fecha_venta <= %s"
            params = (fecha_fin,)

        # ================== 💵 Ventas por Mes (filtrado por fecha) ==================
        query_ventas = f"""
            SELECT DATE_FORMAT(v.Fecha_venta, '%%Y-%%m') AS Mes,
                   SUM(pxv.cantidad * pxv.precio_unitario) AS Total_Ventas
            FROM PRODUCTOXVENTA pxv
            JOIN VENTA v ON pxv.ID_Venta = v.ID_Venta
            {filtro_fecha}
            GROUP BY Mes
            ORDER BY Mes
        """
        cursor.execute(query_ventas, params)
        ventas_mensuales = cursor.fetchall()

        if ventas_mensuales:
            df_ventas = pd.DataFrame(ventas_mensuales, columns=["Mes", "Total Ventas ($)"])
            st.subheader("📈 Ventas Mensuales")
            fig_ventas = px.line(df_ventas, x="Mes", y="Total Ventas ($)", markers=True, title="Total vendido por mes")
            st.plotly_chart(fig_ventas, use_container_width=True)

            # Total mes actual (considerando filtro)
            mes_actual = datetime.today().strftime("%Y-%m")
            total_mes = df_ventas[df_ventas["Mes"] == mes_actual]["Total Ventas ($)"].sum()
            st.metric(label="💰 Total Vendido este Mes", value=f"${total_mes:,.2f}")
        else:
            st.info("No hay datos de ventas en el rango seleccionado.")
            st.metric(label="💰 Total Vendido este Mes", value="$0.00")

        # ================== 🏪 Emprendimientos Activos (sin filtro) ==================
        cursor.execute("""
            SELECT DISTINCT p.ID_Emprendimiento
            FROM PRODUCTOXVENTA pxv
            JOIN PRODUCTO p ON pxv.ID_Producto = p.ID_Producto
        """)
        emprendimientos_activos = cursor.fetchall()
        total_activos = len(emprendimientos_activos)
        st.metric(label="🏪 Emprendimientos Activos", value=total_activos)

        # ================== 📊 Distribución por Género ==================
        cursor.execute("""
            SELECT genero, COUNT(*) AS total
            FROM EMPRENDIMIENTO
            GROUP BY genero
        """)
        genero_data = cursor.fetchall()
        df_genero = pd.DataFrame(genero_data, columns=["Género", "Cantidad"])
        st.subheader("👥 Emprendedores por Género")
        fig_genero = px.pie(df_genero, names="Género", values="Cantidad", title="Distribución por Género")
        st.plotly_chart(fig_genero, use_container_width=True)

        # ================== 🎓 Distribución por Facultad (Pie Chart) ==================
        cursor.execute("""
            SELECT facultad, COUNT(*) AS total
            FROM EMPRENDIMIENTO
            GROUP BY facultad
        """)
        facultad_data = cursor.fetchall()
        df_facultad = pd.DataFrame(facultad_data, columns=["Facultad", "Cantidad"])
        st.subheader("🏫 Emprendedores por Facultad")
        fig_facultad = px.pie(df_facultad, names="Facultad", values="Cantidad", title="Distribución por Facultad")
        st.plotly_chart(fig_facultad, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error al cargar el dashboard: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'con' in locals():
            con.close()

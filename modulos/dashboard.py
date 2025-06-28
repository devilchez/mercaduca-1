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

        # ================== 📅 Filtro de Fechas ==================
        col1, col2 = st.columns(2)
        with col1:
            fecha_inicio = st.date_input("Desde", value=datetime.today().replace(day=1).date())
        with col2:
            fecha_fin = st.date_input("Hasta", value=datetime.today().date())

        if fecha_inicio > fecha_fin:
            st.warning("⚠️ La fecha de inicio no puede ser mayor que la fecha de fin.")
            return

        params = (fecha_inicio, fecha_fin)
        filtro_fecha = "WHERE v.Fecha_venta BETWEEN %s AND %s"

        # ================== 💵 Ventas por Rango de Fecha ==================
        query_ventas = f"""
            SELECT DATE_FORMAT(v.Fecha_venta, '%Y-%m') AS Mes,
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
            st.subheader("📈 Ventas por Rango de Fecha")
            fig_ventas = px.line(df_ventas, x="Mes", y="Total Ventas ($)", markers=True, title="Total vendido por rango de fechas")
            st.plotly_chart(fig_ventas, use_container_width=True)

            total_rango = df_ventas["Total Ventas ($)"].sum()
            st.metric(label="💰 Total Vendido en el Rango", value=f"${total_rango:,.2f}")
        else:
            st.info("No hay datos de ventas en el rango seleccionado.")
            st.metric(label="💰 Total Vendido en el Rango", value="$0.00")

        # ================== 📈 Productos Estrella por Emprendedor ==================
        st.subheader("🌟 Productos Estrella por Emprendedor")

        # Obtener lista de emprendimientos
        cursor.execute("SELECT Nombre_emprendimiento FROM EMPRENDIMIENTO ORDER BY Nombre_emprendimiento")
        emprendimientos = [row[0] for row in cursor.fetchall()]
        selected_emprendimiento = st.selectbox("Selecciona un emprendimiento", emprendimientos)

        query_productos = f"""
            SELECT e.Nombre_emprendimiento, p.Nombre_producto, SUM(pxv.cantidad * pxv.precio_unitario) AS Total_Ventas
            FROM PRODUCTOXVENTA pxv
            JOIN VENTA v ON pxv.ID_Venta = v.ID_Venta
            JOIN PRODUCTO p ON pxv.ID_Producto = p.ID_Producto
            JOIN EMPRENDIMIENTO e ON p.ID_Emprendimiento = e.ID_Emprendimiento
            {filtro_fecha} AND e.Nombre_emprendimiento = %s
            GROUP BY p.Nombre_producto
            ORDER BY Total_Ventas DESC
        """
        cursor.execute(query_productos, params + (selected_emprendimiento,))
        productos_estrella = cursor.fetchall()

        if productos_estrella:
            df_productos = pd.DataFrame(productos_estrella, columns=["Emprendimiento", "Producto", "Total Ventas ($)"])
            fig_productos = px.bar(df_productos, x="Producto", y="Total Ventas ($)", title=f"Productos más vendidos - {selected_emprendimiento}")
            st.plotly_chart(fig_productos, use_container_width=True)
        else:
            st.info("No hay productos vendidos por este emprendedor en el rango seleccionado.")

        # ================== 🏆 Top Emprendedores por Ganancia ==================
        st.subheader("🏆 Top Emprendedores por Ganancia")
        query_top = f"""
            SELECT e.Nombre_emprendimiento, SUM(pxv.cantidad * pxv.precio_unitario) AS Total_Ganancia
            FROM PRODUCTOXVENTA pxv
            JOIN VENTA v ON pxv.ID_Venta = v.ID_Venta
            JOIN PRODUCTO p ON pxv.ID_Producto = p.ID_Producto
            JOIN EMPRENDIMIENTO e ON p.ID_Emprendimiento = e.ID_Emprendimiento
            {filtro_fecha}
            GROUP BY e.Nombre_emprendimiento
            ORDER BY Total_Ganancia DESC
        """
        cursor.execute(query_top, params)
        top_emprendedores = cursor.fetchall()

        if top_emprendedores:
            df_top = pd.DataFrame(top_emprendedores, columns=["Emprendimiento", "Total Ganancia ($)"])
            fig_top = px.bar(df_top, x="Emprendimiento", y="Total Ganancia ($)", title="Top Emprendedores por Ganancia")
            st.plotly_chart(fig_top, use_container_width=True)
        else:
            st.info("No se encontraron datos de ganancias por emprendedor.")

        # ================== 🧭 Distribución por Tipo de Emprendedor ==================
        st.subheader("🗺 Distribución por Tipo de Emprendedor")
        cursor.execute("""
            SELECT Tipo_emprendedor, COUNT(*) AS Total
            FROM EMPRENDIMIENTO
            GROUP BY Tipo_emprendedor
        """)
        tipo_data = cursor.fetchall()

        if tipo_data:
            df_tipo = pd.DataFrame(tipo_data, columns=["Tipo de Emprendedor", "Cantidad"])
            fig_tipo = px.pie(df_tipo, names="Tipo de Emprendedor", values="Cantidad", title="Distribución por Tipo de Emprendedor")
            st.plotly_chart(fig_tipo, use_container_width=True)
        else:
            st.info("No hay datos de tipo de emprendedor.")

        # ================== 👥 Emprendedores por Género ==================
        st.subheader("👥 Emprendedores por Género")
        cursor.execute("""
            SELECT genero, COUNT(*) AS total
            FROM EMPRENDIMIENTO
            GROUP BY genero
        """)
        genero_data = cursor.fetchall()

        df_genero = pd.DataFrame(genero_data, columns=["Género", "Cantidad"])
        fig_genero = px.pie(df_genero, names="Género", values="Cantidad", title="Distribución por Género")
        st.plotly_chart(fig_genero, use_container_width=True)

        # ================== 🎓 Distribución por Facultad ==================
        st.subheader("🏫 Emprendedores por Facultad")
        cursor.execute("""
            SELECT facultad, COUNT(*) AS total
            FROM EMPRENDIMIENTO
            GROUP BY facultad
        """)
        facultad_data = cursor.fetchall()

        df_facultad = pd.DataFrame(facultad_data, columns=["Facultad", "Cantidad"])
        fig_facultad = px.pie(df_facultad, names="Facultad", values="Cantidad", title="Distribución por Facultad")
        st.plotly_chart(fig_facultad, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error al cargar el dashboard: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'con' in locals():
            con.close()

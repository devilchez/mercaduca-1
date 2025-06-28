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

        # Filtro de fechas
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

        # ================== 📈 Ventas por Rango de Fecha ==================
        query_ventas = f"""
            SELECT v.Fecha_venta, SUM(pxv.cantidad * pxv.precio_unitario) AS Total_Ventas
            FROM PRODUCTOXVENTA pxv
            JOIN VENTA v ON pxv.ID_Venta = v.ID_Venta
            {filtro_fecha}
            GROUP BY v.Fecha_venta
            ORDER BY v.Fecha_venta
        """
        cursor.execute(query_ventas, params)
        ventas_rango = cursor.fetchall()

        if ventas_rango:
            df_rango = pd.DataFrame(ventas_rango, columns=["Fecha", "Total Ventas ($)"])
            st.subheader("📈 Ventas por Rango de Fecha")
            fig_rango = px.line(df_rango, x="Fecha", y="Total Ventas ($)", markers=True, title="Total vendido por rango de fechas")
            st.plotly_chart(fig_rango, use_container_width=True)

            total_mes = df_rango["Total Ventas ($)"].sum()
            st.metric(label="💰 Total Vendido en el Rango", value=f"${total_mes:,.2f}")
        else:
            st.info("No hay ventas registradas en ese rango.")
            st.metric(label="💰 Total Vendido en el Rango", value="$0.00")

        # ================== 📌 Filtro dinámico de Emprendimiento ==================
        cursor.execute("SELECT Nombre_emprendimiento FROM EMPRENDIMIENTO ORDER BY Nombre_emprendimiento")
        lista_emprendimientos = [row[0] for row in cursor.fetchall()]
        filtro_emprendimiento = st.selectbox("Selecciona un emprendimiento", ["Todos"] + lista_emprendimientos)

        # ================== 📉 Productos Estrella por Emprendimiento ==================
        st.subheader("📈 Productos Estrella por Emprendedor")
        query_productos = f"""
            SELECT e.Nombre_emprendimiento, p.Nombre_producto, SUM(pxv.cantidad) AS Total_Ventas
            FROM PRODUCTOXVENTA pxv
            JOIN VENTA v ON pxv.ID_Venta = v.ID_Venta
            JOIN PRODUCTO p ON pxv.ID_Producto = p.ID_Producto
            JOIN EMPRENDIMIENTO e ON p.ID_Emprendimiento = e.ID_Emprendimiento
            {filtro_fecha}
        """
        if filtro_emprendimiento != "Todos":
            query_productos += " AND e.Nombre_emprendimiento = %s"
            params_productos = params + (filtro_emprendimiento,)
        else:
            params_productos = params

        query_productos += " GROUP BY e.Nombre_emprendimiento, p.Nombre_producto ORDER BY Total_Ventas DESC"

        cursor.execute(query_productos, params_productos)
        productos_data = cursor.fetchall()

        if productos_data:
            df_productos = pd.DataFrame(productos_data, columns=["Emprendimiento", "Producto", "Total Ventas"])
            fig_productos = px.bar(df_productos, x="Producto", y="Total Ventas", color="Emprendimiento", title="Productos Estrella")
            st.plotly_chart(fig_productos, use_container_width=True)
        else:
            st.info("No hay datos de productos vendidos para ese filtro.")

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
        top_data = cursor.fetchall()

        if top_data:
            df_top = pd.DataFrame(top_data, columns=["Emprendimiento", "Total Ganancia ($)"])
            fig_top = px.bar(df_top, x="Emprendimiento", y="Total Ganancia ($)", title="Top Emprendedores por Ganancia")
            st.plotly_chart(fig_top, use_container_width=True)
        else:
            st.info("No hay datos de ganancias para el rango seleccionado.")

        # ================== 📚 Distribución por Tipo de Emprendedor ==================
        st.subheader("📚 Distribución por Tipo de Emprendedor")
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
            st.info("No se encontraron datos de tipos de emprendedores.")

        # ================== 🏛️ Emprendedores por Facultad ==================
        st.subheader("🏛️ Emprendedores por Facultad")
        cursor.execute("""
            SELECT Facultad, COUNT(*) AS Total
            FROM EMPRENDIMIENTO
            GROUP BY Facultad
            ORDER BY Total DESC
        """)
        facultad_data = cursor.fetchall()

        if facultad_data:
            df_facultad = pd.DataFrame(facultad_data, columns=["Facultad", "Cantidad"])
            fig_facultad = px.bar(df_facultad, x="Facultad", y="Cantidad", title="Cantidad de Emprendedores por Facultad")
            st.plotly_chart(fig_facultad, use_container_width=True)
        else:
            st.info("No hay datos de facultades.")

        # ================== 🚻 Emprendedores por Género ==================
        st.subheader("🚻 Emprendedores por Género")
        cursor.execute("""
            SELECT Genero, COUNT(*) AS Total
            FROM EMPRENDIMIENTO
            GROUP BY Genero
            ORDER BY Total DESC
        """)
        genero_data = cursor.fetchall()

        if genero_data:
            df_genero = pd.DataFrame(genero_data, columns=["Género", "Cantidad"])
            fig_genero = px.pie(df_genero, names="Género", values="Cantidad", title="Distribución de Emprendedores por Género")
            st.plotly_chart(fig_genero, use_container_width=True)
        else:
            st.info("No hay datos de género de los emprendedores.")

    except Exception as e:
        st.error(f"❌ Error al cargar el dashboard: {e}")

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'con' in locals(): con.close()

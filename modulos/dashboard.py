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
        filtro_fecha = "WHERE v.Fecha_venta BETWEEN %s AND %s"
        params = (fecha_inicio, fecha_fin)

        # ================== 💵 Ventas por Emprendedor ==================
        st.subheader("📈 Ventas por Emprendedor")
        cursor.execute("SELECT Nombre_emprendimiento FROM EMPRENDIMIENTO ORDER BY Nombre_emprendimiento")
        lista_emprendimientos = [row[0] for row in cursor.fetchall()]

        emprendimiento_filtro = st.selectbox("Seleccionar Emprendimiento", ["Todos"] + lista_emprendimientos)

        # Filtrar productos por el emprendedor seleccionado
        query_productos = f"""
            SELECT p.Nombre_producto, SUM(pxv.cantidad * pxv.precio_unitario) AS Total_Ventas
            FROM PRODUCTOXVENTA pxv
            JOIN VENTA v ON pxv.ID_Venta = v.ID_Venta
            JOIN PRODUCTO p ON pxv.ID_Producto = p.ID_Producto
            JOIN EMPRENDIMIENTO e ON p.ID_Emprendimiento = e.ID_Emprendimiento
            {filtro_fecha}
        """
        params_productos = (fecha_inicio, fecha_fin)

        if emprendimiento_filtro != "Todos":
            query_productos += " AND e.Nombre_emprendimiento = %s"
            params_productos = (fecha_inicio, fecha_fin, emprendimiento_filtro)

        query_productos += """
            GROUP BY p.Nombre_producto
            ORDER BY Total_Ventas DESC
        """

        cursor.execute(query_productos, params_productos)
        productos_ventas = cursor.fetchall()

        if productos_ventas:
            df_productos_ventas = pd.DataFrame(productos_ventas, columns=["Producto", "Total Ventas ($)"])
            fig_productos_ventas = px.bar(df_productos_ventas, x="Producto", y="Total Ventas ($)", title=f"Productos Estrella de {emprendimiento_filtro}")
            st.plotly_chart(fig_productos_ventas, use_container_width=True)
        else:
            st.info("No se encontraron ventas para el emprendedor seleccionado en este rango de fechas.")

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
            st.subheader("📈 Ventas por Rango de Fecha")
            fig_ventas = px.line(df_ventas, x="Mes", y="Total Ventas ($)", markers=True, title="Total vendido por rango de fechas")
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


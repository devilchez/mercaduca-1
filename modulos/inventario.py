import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
from modulos.config.conexion import obtener_conexion

def mostrar_inventario():
    st.header("📟 Inventario")

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Obtener lista de emprendimientos
        cursor.execute("SELECT Nombre_emprendimiento FROM EMPRENDIMIENTO ORDER BY Nombre_emprendimiento")
        lista_emprendimientos = [row[0] for row in cursor.fetchall()]

        # ========================== 📥 Productos Abastecidos ==========================
        st.subheader("📥 Productos Abastecidos (Filtrados por Fecha y Emprendimiento)")
        col1, col2 = st.columns(2)
        with col1:
            fecha_inicio = st.date_input("Desde", value=datetime.today().replace(day=1).date())
        with col2:
            fecha_fin = st.date_input("Hasta", value=datetime.today().date())

        if fecha_inicio > fecha_fin:
            st.warning("⚠️ La fecha de inicio no puede ser mayor que la fecha de fin.")
            return

        emprendimiento_abastecimiento = st.selectbox("🔍 Filtrar abastecimiento por emprendimiento", ["Todos"] + lista_emprendimientos)

        query_abastecidos = """
            SELECT e.Nombre_emprendimiento, p.Nombre_producto, i.Cantidad_ingresada, i.Fecha_ingreso
            FROM INVENTARIO i
            JOIN PRODUCTO p ON i.ID_Producto = p.ID_Producto
            JOIN EMPRENDIMIENTO e ON p.ID_Emprendimiento = e.ID_Emprendimiento
            WHERE DATE(i.Fecha_ingreso) BETWEEN %s AND %s
        """
        params_abastecidos = [fecha_inicio, fecha_fin]

        if emprendimiento_abastecimiento != "Todos":
            query_abastecidos += " AND e.Nombre_emprendimiento = %s"
            params_abastecidos.append(emprendimiento_abastecimiento)

        query_abastecidos += " ORDER BY i.Fecha_ingreso DESC"

        cursor.execute(query_abastecidos, params_abastecidos)
        datos_abastecidos = cursor.fetchall()

        if datos_abastecidos:
            df_abastecidos = pd.DataFrame(datos_abastecidos, columns=["Emprendimiento", "Producto", "Cantidad Abastecida", "Fecha de Abastecimiento"])
            st.dataframe(df_abastecidos)
        else:
            st.info("No se encontraron productos abastecidos con esos filtros.")

        # ========================== 📦 Stock Actual ==========================
        st.subheader("📦 Stock Actual")
        emprendimiento_stock = st.selectbox("🔍 Filtrar stock por emprendimiento", ["Todos"] + lista_emprendimientos)

        query_stock = """
            SELECT e.Nombre_emprendimiento, p.Nombre_producto, SUM(i.Stock) AS Stock_Disponible
            FROM INVENTARIO i
            JOIN PRODUCTO p ON i.ID_Producto = p.ID_Producto
            JOIN EMPRENDIMIENTO e ON p.ID_Emprendimiento = e.ID_Emprendimiento
        """
        params_stock = []

        if emprendimiento_stock != "Todos":
            query_stock += " WHERE e.Nombre_emprendimiento = %s"
            params_stock.append(emprendimiento_stock)

        query_stock += " GROUP BY e.Nombre_emprendimiento, p.Nombre_producto ORDER BY e.Nombre_emprendimiento, p.Nombre_producto"

        cursor.execute(query_stock, params_stock)
        datos_stock = cursor.fetchall()

        if datos_stock:
            df_stock = pd.DataFrame(datos_stock, columns=["Emprendimiento", "Producto", "Stock Disponible"])
            st.dataframe(df_stock)
        else:
            st.info("No hay stock disponible para ese filtro.")

        # ========================== 📅 Productos Próximos a Vencer ==========================
        st.subheader("📅 Productos Próximos a Vencer (Próximos 30 días)")
        fecha_limite = datetime.today() + timedelta(days=30)
        emprendimiento_vencer = st.selectbox("🔍 Filtrar vencimientos por emprendimiento", ["Todos"] + lista_emprendimientos)

        query_vencimiento = """
            SELECT e.Nombre_emprendimiento, p.Nombre_producto, 
                   i.Stock AS Stock_Disponible, i.Fecha_vencimiento
            FROM INVENTARIO i
            JOIN PRODUCTO p ON i.ID_Producto = p.ID_Producto
            JOIN EMPRENDIMIENTO e ON p.ID_Emprendimiento = e.ID_Emprendimiento
            WHERE i.Fecha_vencimiento BETWEEN CURDATE() AND %s
              AND (i.Cantidad_ingresada - i.Cantidad_salida) > 0
        """
        params_vencimiento = [fecha_limite.date()]

        if emprendimiento_vencer != "Todos":
            query_vencimiento += " AND e.Nombre_emprendimiento = %s"
            params_vencimiento.append(emprendimiento_vencer)

        query_vencimiento += " ORDER BY i.Fecha_vencimiento ASC"

        cursor.execute(query_vencimiento, params_vencimiento)
        productos_proximos_vencer = cursor.fetchall()

        if productos_proximos_vencer:
            df_proximos_vencer = pd.DataFrame(productos_proximos_vencer, columns=["Emprendimiento", "Producto", "Stock Disponible", "Fecha de Vencimiento"])

            # Calcular días restantes
            hoy = date.today()
            df_proximos_vencer["Días Restantes"] = df_proximos_vencer["Fecha de Vencimiento"].apply(
                lambda x: (x - hoy).days
            )

            # Representación visual con advertencias
            def advertencia(dias):
                if dias <= 0:
                    return "⚠️ Vencido"
                elif dias <= 3:
                    return f"🔴 {dias} días"
                elif dias <= 7:
                    return f"🟠 {dias} días"
                elif dias <= 15:
                    return f"🟡 {dias} días"
                else:
                    return f"🟢 {dias} días"

            df_proximos_vencer["Días Restantes"] = df_proximos_vencer["Días Restantes"].apply(advertencia)

            # Mostrar tabla ordenada
            st.dataframe(df_proximos_vencer.sort_values("Fecha de Vencimiento"))

        else:
            st.info("No hay productos próximos a vencer para ese filtro.")

    except Exception as e:
        st.error(f"❌ Error al cargar el inventario: {e}")

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'con' in locals(): con.close()

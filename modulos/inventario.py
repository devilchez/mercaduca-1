import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
from modulos.config.conexion import obtener_conexion

def mostrar_inventario():
    st.header("📟 Inventario")

    # Filtros de fecha para productos abastecidos
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Desde", value=datetime.today().replace(day=1).date())
    with col2:
        fecha_fin = st.date_input("Hasta", value=datetime.today().date())

    if fecha_inicio > fecha_fin:
        st.warning("⚠️ La fecha de inicio no puede ser mayor que la fecha de fin.")
        return

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Obtener lista de emprendimientos
        cursor.execute("SELECT DISTINCT Nombre_emprendimiento FROM EMPRENDIMIENTO ORDER BY Nombre_emprendimiento")
        emprendimientos = [row[0] for row in cursor.fetchall()]
        emprendimiento_seleccionado = st.selectbox("🔍 Filtrar por Emprendimiento (Próximos a vencer)", options=["Todos"] + emprendimientos)

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

        query = """
            SELECT e.Nombre_emprendimiento, p.Nombre_producto, 
                   i.Stock AS Stock_Disponible, i.Fecha_vencimiento
            FROM INVENTARIO i
            JOIN PRODUCTO p ON i.ID_Producto = p.ID_Producto
            JOIN EMPRENDIMIENTO e ON p.ID_Emprendimiento = e.ID_Emprendimiento
            WHERE i.Fecha_vencimiento BETWEEN CURDATE() AND %s
              AND (i.Cantidad_ingresada - i.Cantidad_salida) > 0
        """

        params = [fecha_limite.date()]
        if emprendimiento_seleccionado != "Todos":
            query += " AND e.Nombre_emprendimiento = %s"
            params.append(emprendimiento_seleccionado)

        query += " ORDER BY i.Fecha_vencimiento ASC"
        cursor.execute(query, params)
        productos_proximos_vencer = cursor.fetchall()

        if productos_proximos_vencer:
            df_proximos_vencer = pd.DataFrame(productos_proximos_vencer, columns=["Emprendimiento", "Producto", "Stock Disponible", "Fecha de Vencimiento"])

            # Añadir columna de días restantes
            hoy = date.today()
            df_proximos_vencer["Días Restantes"] = df_proximos_vencer["Fecha de Vencimiento"].apply(
                lambda x: (x - hoy).days
            )

            # Añadir advertencia visual con emojis
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

            # Ordenar por vencimiento cercano
            st.subheader("📅 Productos Próximos a Vencer (Próximos 30 días)")
            st.dataframe(df_proximos_vencer.sort_values("Fecha de Vencimiento"))

        else:
            st.info("No hay productos próximos a vencer en los próximos 30 días.")

    except Exception as e:
        st.error(f"❌ Error al cargar el inventario: {e}")

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'con' in locals(): con.close()

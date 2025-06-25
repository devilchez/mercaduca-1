import streamlit as st
import pandas as pd
from modulos.config.conexion import obtener_conexion
from datetime import datetime
from io import BytesIO
from fpdf import FPDF

def reporte_ventas():
    st.header("📊 Reporte de Ventas por Emprendimiento")

    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Desde", value=datetime.today().replace(day=1))
    with col2:
        fecha_fin = st.date_input("Hasta", value=datetime.today())

    if fecha_inicio > fecha_fin:
        st.warning("⚠️ La fecha de inicio no puede ser mayor que la de fin.")
        return

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Obtener lista de emprendimientos únicos
        cursor.execute("SELECT DISTINCT Nombre_emprendimiento FROM EMPRENDIMIENTO ORDER BY Nombre_emprendimiento")
        emprendimientos = [row[0] for row in cursor.fetchall()]

        # Agregar opción "Todos"
        emprendimientos.insert(0, "Todos")
        emprendimiento_seleccionado = st.selectbox("🔽 Filtrar por emprendimiento", emprendimientos)

        # Construcción del query dinámico
        fecha_ini_str = fecha_inicio.strftime('%Y-%m-%d')
        fecha_fin_str = fecha_fin.strftime('%Y-%m-%d')

        query = f"""
            SELECT v.ID_Venta, e.Nombre_emprendimiento, pr.Nombre_producto, pv.cantidad, pv.precio_unitario, 
                   v.fecha_venta, DATE_FORMAT(v.hora_venta, '%H:%i:%s') AS hora_venta, pr.ID_Producto
            FROM VENTA v
            JOIN PRODUCTOXVENTA pv ON v.ID_Venta = pv.ID_Venta
            JOIN PRODUCTO pr ON pv.ID_Producto = pr.ID_Producto
            JOIN EMPRENDIMIENTO e ON pr.ID_Emprendimiento = e.ID_Emprendimiento
            WHERE v.fecha_venta BETWEEN '{fecha_ini_str}' AND '{fecha_fin_str}'
        """

        if emprendimiento_seleccionado != "Todos":
            query += f" AND e.Nombre_emprendimiento = '{emprendimiento_seleccionado}'"

        query += " ORDER BY v.ID_Venta DESC"

        cursor.execute(query)
        rows = cursor.fetchall()

        if not rows:
            st.info("No se encontraron ventas con los filtros seleccionados.")
            return

        # Crear DataFrame
        df = pd.DataFrame(rows, columns=[
            "ID_Venta", "Emprendimiento", "Producto", "Cantidad", "Precio Unitario", 
            "Fecha Venta", "Hora Venta", "ID_Producto"
        ])
        df["Hora Venta"] = df["Hora Venta"].astype(str)
        df["Total"] = df["Cantidad"] * df["Precio Unitario"]

        st.markdown("---")
        st.markdown("### 🖋️ Detalles de Ventas")

        for index, row in df.iterrows():
            col1, col2 = st.columns([6, 1])
            with col1:
                st.markdown(
                    f"**Venta ID:** {row['ID_Venta']}  \n"
                    f"**Emprendimiento:** {row['Emprendimiento']}  \n"
                    f"**Producto:** {row['Producto']}  \n"
                    f"**Cantidad:** {row['Cantidad']}  \n"
                    f"**Total:** ${row['Total']:.2f}  \n"
                    f"**Hora de Venta:** {row['Hora Venta']}"
                )
            with col2:
                if st.button("🗑", key=f"delete_{row['ID_Venta']}_{row['ID_Producto']}_{index}"):
                    try:
                        cursor.execute(
                            f"DELETE FROM PRODUCTOXVENTA WHERE ID_Venta = {row['ID_Venta']} AND ID_Producto = {row['ID_Producto']}"
                        )
                        con.commit()

                        cursor.execute(
                            f"SELECT COUNT(*) FROM PRODUCTOXVENTA WHERE ID_Venta = {row['ID_Venta']}"
                        )
                        count = cursor.fetchone()[0]
                        if count == 0:
                            cursor.execute(
                                f"DELETE FROM VENTA WHERE ID_Venta = {row['ID_Venta']}"
                            )
                            con.commit()
                            st.success(f"✅ Venta ID {row['ID_Venta']} eliminada completamente.")

                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ Error al eliminar el producto: {e}")

        # Exportación
        st.markdown("---")
        st.markdown("### 📁 Exportar ventas filtradas")
        col1, col2 = st.columns(2)

        with col1:
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                df.drop(columns=["ID_Producto"]).to_excel(writer, index=False, sheet_name='ReporteVentas')
            st.download_button(
                label="⬇️ Descargar Excel",
                data=excel_buffer.getvalue(),
                file_name="reporte_ventas.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        with col2:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Reporte de Ventas", ln=True, align='C')
            pdf.set_font("Arial", size=10)

            for index, row in df.iterrows():
                texto = (
                    f"{row['Emprendimiento']} | {row['Producto']} | "
                    f"{row['Cantidad']} x ${row['Precio Unitario']:.2f} = ${row['Total']:.2f} | "
                    f"Hora: {row['Hora Venta']}"
                )
                pdf.cell(0, 10, txt=texto, ln=True)

            pdf_buffer = BytesIO()
            pdf.output(pdf_buffer)
            st.download_button(
                label="⬇️ Descargar PDF",
                data=pdf_buffer.getvalue(),
                file_name="reporte_ventas.pdf",
                mime="application/pdf"
            )

    except Exception as e:
        st.error(f"❌ Error al generar el reporte: {e}")

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'con' in locals(): con.close()

import streamlit as st
import pandas as pd
from modulos.config.conexion import obtener_conexion
from datetime import datetime
from io import BytesIO
from fpdf import FPDF

def reporte_ventas():
    st.header("📊 Reporte de Ventas por Emprendimiento")

    # Filtros de fecha
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

        query = """
            SELECT v.ID_Venta, e.Nombre_emprendimiento, pr.Nombre_producto, pv.cantidad, pv.precio_unitario, v.fecha_venta
            FROM VENTA v
            JOIN PRODUCTOXVENTA pv ON v.ID_Venta = pv.ID_Venta
            JOIN PRODUCTO pr ON pv.ID_Producto = pr.ID_Producto
            JOIN EMPRENDIMIENTO e ON pr.ID_Emprendimiento = e.ID_Emprendimiento
            WHERE v.fecha_venta BETWEEN %s AND %s
            ORDER BY v.ID_Venta DESC
        """

        cursor.execute(query, (fecha_inicio, fecha_fin))
        rows = cursor.fetchall()

        if not rows:
            st.info("No se encontraron ventas en el rango seleccionado.")
            return

        df = pd.DataFrame(rows, columns=[
            "ID_Venta", "Emprendimiento", "Producto", "Cantidad", "Precio Unitario", "Fecha Venta"
        ])
        df["Total"] = df["Cantidad"] * df["Precio Unitario"]

        # Mostrar ventas agrupadas
        ventas_ids = df['ID_Venta'].unique()

        for venta_id in ventas_ids:
            st.markdown("---")
            st.subheader(f"🧾 Venta ID: {venta_id}")
            venta_df = df[df['ID_Venta'] == venta_id][["Producto", "Cantidad", "Precio Unitario", "Total"]]
            st.table(venta_df)

            if st.button(f"🗑 Eliminar venta ID {venta_id}", key=f"delete_{venta_id}"):
                try:
                    cursor.execute("DELETE FROM PRODUCTOXVENTA WHERE ID_Venta = %s", (venta_id,))
                    cursor.execute("DELETE FROM VENTA WHERE ID_Venta = %s", (venta_id,))
                    con.commit()
                    st.success(f"✅ Venta ID {venta_id} eliminada correctamente.")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al eliminar la venta: {e}")

        # Mostrar tabla completa si se desea exportar
        st.markdown("---")
        st.markdown("### 📁 Exportar todas las ventas filtradas")
        col1, col2 = st.columns(2)

        with col1:
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='ReporteVentas')
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
                texto = f"{row['Emprendimiento']} | {row['Producto']} | {row['Cantidad']} x ${row['Precio Unitario']:.2f} = ${row['Total']:.2f}"
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

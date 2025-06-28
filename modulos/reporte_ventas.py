import streamlit as st
import pandas as pd
from modulos.config.conexion import obtener_conexion
from datetime import datetime
from io import BytesIO
from fpdf import FPDF

def reporte_ventas():
    st.header("📊 Reporte de Ventas por Emprendimiento")

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

        cursor.execute("SELECT Nombre_emprendimiento FROM EMPRENDIMIENTO")
        emprendimientos = [row[0] for row in cursor.fetchall()]
        emprendimiento_seleccionado = st.selectbox("Filtrar por Emprendimiento", ["Todos"] + emprendimientos)

        fecha_ini_str = fecha_inicio.strftime('%Y-%m-%d')
        fecha_fin_str = fecha_fin.strftime('%Y-%m-%d')

        query = f"""
            SELECT v.ID_Venta, e.Nombre_emprendimiento, pr.Nombre_producto, pv.cantidad, pv.precio_unitario, 
                   v.fecha_venta, DATE_FORMAT(v.hora_venta, '%H:%i:%s') AS hora_venta, pr.ID_Producto, v.tipo_pago
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
            st.info("No se encontraron ventas en el rango seleccionado.")
            return

        df = pd.DataFrame(rows, columns=[
            "ID_Venta", "Emprendimiento", "Producto", "Cantidad", "Precio Unitario",
            "Fecha Venta", "Hora Venta", "ID_Producto", "Tipo Pago"
        ])
        df["Hora Venta"] = df["Hora Venta"].astype(str)
        df["Total"] = df["Cantidad"] * df["Precio Unitario"]

        st.markdown("---")
        st.markdown("### 🗂 Detalles de Ventas")

        ventas_unicas = df.drop_duplicates(subset=["ID_Venta"])

        for index, row in ventas_unicas.iterrows():
            productos_de_venta = df[df["ID_Venta"] == row["ID_Venta"]]

            with st.container():
                st.markdown(f"### 🧾 Venta ID: {row['ID_Venta']}")

                for _, producto in productos_de_venta.iterrows():
                    col1, col2 = st.columns([6, 1])
                    with col1:
                        st.markdown(
                            f"<span style='font-size:16px;'>"
                            f"🔹 <strong>Producto:</strong> {producto['Producto']} &nbsp; | &nbsp; "
                            f"<strong>Cantidad:</strong> {producto['Cantidad']} &nbsp; | &nbsp; "
                            f"<strong>Precio:</strong> ${producto['Precio Unitario']:.2f} &nbsp; | &nbsp; "
                            f"<strong>Total:</strong> ${producto['Total']:.2f}"
                            f"</span>",
                            unsafe_allow_html=True
                        )
                    with col2:
                        if st.button("🗑", key=f"delete_{row['ID_Venta']}_{producto['ID_Producto']}"):
                            try:
                                producto_id = producto['ID_Producto']
                                venta_id = producto['ID_Venta']

                                cursor.execute(
                                    "DELETE FROM PRODUCTOXVENTA WHERE ID_Venta = %s AND ID_Producto = %s",
                                    (venta_id, producto_id)
                                )
                                con.commit()

                                cursor.execute("SELECT COUNT(*) FROM PRODUCTOXVENTA WHERE ID_Venta = %s", (venta_id,))
                                count = cursor.fetchone()[0]

                                if count == 0:
                                    cursor.execute("DELETE FROM VENTA WHERE ID_Venta = %s", (venta_id,))
                                    con.commit()
                                    st.success(f"✅ Venta ID {venta_id} eliminada completamente.")
                                else:
                                    cursor.execute(
                                        "SELECT SUM(cantidad) FROM PRODUCTOXVENTA WHERE ID_Venta = %s", (venta_id,)
                                    )
                                    nueva_cantidad = cursor.fetchone()[0] or 0
                                    cursor.execute(
                                        "UPDATE VENTA SET cantidad_vendida = %s WHERE ID_Venta = %s",
                                        (nueva_cantidad, venta_id)
                                    )
                                    con.commit()
                                    st.success("✅ Producto eliminado y cantidad total actualizada.")

                                st.rerun()

                            except Exception as e:
                                st.error(f"❌ Error al eliminar el producto: {e}")

                st.markdown(
                    f"**Emprendimiento:** {row['Emprendimiento']}  \n"
                    f"**Tipo de Pago:** {row['Tipo Pago']}  \n"
                    f"**Fecha Venta:** {row['Fecha Venta']}  \n"
                    f"**Hora Venta:** {row['Hora Venta']}"
                )

                if st.button("✏️ Editar tipo de pago", key=f"editar_pago_{row['ID_Venta']}"):
                    with st.form(key=f"form_editar_pago_{row['ID_Venta']}"):
                        nuevo_tipo = st.selectbox(
                            "Nuevo tipo de pago",
                            ["Efectivo", "Woompi"],
                            index=["Efectivo", "Woompi"].index(row['Tipo Pago']) if row['Tipo Pago'] in ["Efectivo", "Woompi"] else 0
                        )
                        guardar = st.form_submit_button("💾 Guardar")

                        if guardar:
                            try:
                                cursor.execute(
                                    "UPDATE VENTA SET tipo_pago = %s WHERE ID_Venta = %s",
                                    (nuevo_tipo, row["ID_Venta"])
                                )
                                con.commit()
                                st.success("✅ Tipo de pago actualizado.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error al actualizar: {e}")

        # Exportar Excel y PDF
        st.markdown("---")
        st.markdown("### 📁 Exportar ventas filtradas")
        nombre_archivo = "reporte_ventas"
        if emprendimiento_seleccionado != "Todos":
            nombre_archivo += f"_{emprendimiento_seleccionado.replace(' ', '_')}"

        col1, col2 = st.columns(2)

        with col1:
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                df.drop(columns=["ID_Producto"]).to_excel(writer, index=False, sheet_name='ReporteVentas')
            st.download_button(
                label="⬇️ Descargar Excel",
                data=excel_buffer.getvalue(),
                file_name=f"{nombre_archivo}.xlsx",
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
                    f"Pago: {row['Tipo Pago']} | Fecha: {row['Fecha Venta']} | Hora: {row['Hora Venta']}"
                )
                pdf.cell(0, 10, txt=texto, ln=True)

            pdf_buffer = BytesIO()
            pdf.output(pdf_buffer)
            st.download_button(
                label="⬇️ Descargar PDF",
                data=pdf_buffer.getvalue(),
                file_name=f"{nombre_archivo}.pdf",
                mime="application/pdf"
            )

    except Exception as e:
        st.error(f"❌ Error al generar el reporte: {e}")

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'con' in locals(): con.close()

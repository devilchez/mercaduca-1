import streamlit as st
from modulos.config.conexion import obtener_conexion

def mostrar_ventas():
    st.header("Registrar venta")
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Obtener productos
        cursor.execute("SELECT ID_Producto, Nombre_producto, Precio FROM PRODUCTO")
        productos = cursor.fetchall()
        producto_dict = {nombre: (idp, precio) for idp, nombre, precio in productos}

        producto_sel = st.selectbox("Producto", list(producto_dict.keys()))
        cantidad = st.number_input("Cantidad vendida", min_value=1)
        tipo_pago = st.selectbox("Tipo de pago", ["Efectivo", "Woompi"])

        id_producto, precio_unitario = producto_dict[producto_sel]
        total = cantidad * precio_unitario
        st.markdown(f"**Precio unitario:** ${precio_unitario:.2f}")
        st.markdown(f"**Total a cobrar:** ${total:.2f}")

        if st.button("Registrar venta"):
            # Obtener el stock total disponible
            cursor.execute(
                "SELECT SUM(Stock) FROM INVENTARIO WHERE ID_Producto = %s",
                (id_producto,)
            )
            resultado = cursor.fetchone()
            stock_disponible = int(resultado[0]) if resultado and resultado[0] else 0

            if stock_disponible >= cantidad:
                try:
                    # Insertar en la tabla VENTA
                    cursor.execute(
                        "INSERT INTO VENTA (Fecha_venta, ID_Producto, Cantidad_vendida, Tipo_pago) "
                        "VALUES (NOW(), %s, %s, %s)",
                        (id_producto, cantidad, tipo_pago)
                    )

                    # Actualizar inventario con lógica FIFO
                    cantidad_restante = cantidad
                    cursor.execute(
                        "SELECT ID_Inventario, Stock FROM INVENTARIO "
                        "WHERE ID_Producto = %s AND Stock > 0 ORDER BY Fecha_ingreso ASC",
                        (id_producto,)
                    )
                    inventarios = cursor.fetchall()

                    for inv_id, stock_en_fila in inventarios:
                        if cantidad_restante <= 0:
                            break
                        a_restar = min(cantidad_restante, stock_en_fila)
                        cursor.execute(
                            "UPDATE INVENTARIO SET Stock = Stock - %s WHERE ID_Inventario = %s",
                            (a_restar, inv_id)
                        )
                        cantidad_restante -= a_restar

                    if cantidad_restante > 0:
                        raise Exception("❌ Stock inconsistente. No se pudo descontar toda la cantidad.")

                    con.commit()
                    st.success("✅ Venta registrada correctamente")

                except Exception as e:
                    con.rollback()
                    st.error(f"❌ Error al registrar la venta: {e}")
            else:
                st.error("⚠️ No hay suficiente stock para esta venta.")

    except Exception as e:
        st.error(f"Error de conexión o consulta: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'con' in locals():
            con.close()

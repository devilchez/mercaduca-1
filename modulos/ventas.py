import streamlit as st
from modulos.config.conexion import obtener_conexion

def mostrar_ventas():
    st.header("Registrar venta")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor(buffered=True)  # Importante para evitar errores de múltiples queries

        # Obtener productos con precio
        cursor.execute("SELECT ID_Producto, Nombre_producto, Precio FROM PRODUCTO")
        productos = cursor.fetchall()

        if not productos:
            st.warning("No hay productos disponibles.")
            return

        # Diccionarios para acceder a ID y precio
        producto_dict = {nombre: (idp, precio) for idp, nombre, precio in productos}
        lista_nombres = list(producto_dict.keys())

        producto_sel = st.selectbox("Producto", lista_nombres)
        cantidad = st.number_input("Cantidad vendida", min_value=1)
        tipo_pago = st.selectbox("Tipo de pago", ["Efectivo", "Woompi"])

        # Obtener precio unitario
        id_producto, precio_unitario = producto_dict[producto_sel]
        total = precio_unitario * cantidad

        # Mostrar información de precio
        st.markdown(f"**Precio unitario:** ${precio_unitario:.2f}")
        st.markdown(f"**Total a pagar:** ${total:.2f}")

        if st.button("Registrar venta"):
            # Verificar stock
            cursor.execute(
                "SELECT Stock FROM INVENTARIO WHERE ID_Producto = %s",
                (id_producto,)
            )
            stock = cursor.fetchone()

            if stock and stock[0] >= cantidad:
                try:
                    st.write(f"Insertando venta: Producto ID {id_producto}, Cantidad {cantidad}, Pago {tipo_pago}, Total ${total:.2f}")
                    
                    # Insertar en VENTA (agrega total si tienes esa columna)
                    cursor.execute(
                        "INSERT INTO VENTA (Fecha_venta, ID_Producto, Cantidad_vendida, Tipo_pago) "
                        "VALUES (NOW(), %s, %s, %s)",
                        (id_producto, cantidad, tipo_pago)
                    )

                    # Actualizar inventario
                    cursor.execute(
                        "UPDATE INVENTARIO SET Stock = Stock - %s WHERE ID_Producto = %s",
                        (cantidad, id_producto)
                    )

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
        if 'cursor' in locals(): cursor.close()
        if 'con' in locals(): con.close()

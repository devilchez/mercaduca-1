import streamlit as st
from modulos.config.conexion import obtener_conexion

def mostrar_ventas():
    st.header("Registrar venta")
    con = obtener_conexion()
    cursor = con.cursor()

    cursor.execute("SELECT ID_Producto, Nombre_producto FROM PRODUCTO")
    productos = cursor.fetchall()
    producto_dict = {nombre: idp for idp, nombre in productos}

    producto_sel = st.selectbox("Producto", list(producto_dict.keys()))
    cantidad = st.number_input("Cantidad vendida", min_value=1)
    tipo_pago = st.selectbox("Tipo de pago", ["Efectivo", "Tarjeta"])

    if st.button("Registrar venta"):
        id_producto = producto_dict[producto_sel]
        cursor.execute("SELECT Stock FROM INVENTARIO WHERE ID_Producto = %s", (id_producto,))
        stock = cursor.fetchone()

        if stock and stock[0] >= cantidad:
            cursor.execute(
                "INSERT INTO VENTA (Fecha_venta, ID_Producto, Cantidad_vendida, Tipo_pago) VALUES (NOW(), %s, %s, %s)",
                (id_producto, cantidad, tipo_pago)
            )
            cursor.execute(
                "UPDATE INVENTARIO SET Stock = Stock - %s WHERE ID_Producto = %s",
                (cantidad, id_producto)
            )
            con.commit()
            st.success("Venta registrada")
        else:

import streamlit as st
from modulos.config.conexion import obtener_conexion
from datetime import datetime

def mostrar_abastecimiento(usuario):
    st.header("Registrar abastecimiento")

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Obtener lista de emprendimientos
        cursor.execute("SELECT ID_Emprendimiento, Nombre_emprendimiento FROM EMPRENDIMIENTO")
        emprendedores = cursor.fetchall()

        if not emprendedores:
            st.warning("No hay emprendimientos registrados.")
            return

        # Diccionario nombre -> id
        opciones = {nombre: emp_id for emp_id, nombre in emprendedores}
        lista_emprendedores = list(opciones.keys())

        # Select emprendedor
        emprendedor = st.selectbox("Selecciona un emprendedor", lista_emprendedores, key="select_emprendedor")
        id_emprendimiento = opciones[emprendedor]

        # Obtener productos con sus ID y precio
        cursor.execute("SELECT ID_Producto, Nombre_producto, Precio FROM PRODUCTO WHERE ID_Emprendimiento = %s", (id_emprendimiento,))
        productos_data = cursor.fetchall()

        if not productos_data:
            st.warning("Este emprendedor aún no tiene productos registrados.")
            return

        # Diccionario nombre -> (ID, precio)
        productos_dict = {row[1]: (row[0], row[2]) for row in productos_data}
        nombres_productos = list(productos_dict.keys())

        producto_seleccionado = st.selectbox("Selecciona el producto", nombres_productos, key="producto_seleccionado")
        id_producto, precio_unitario = productos_dict[producto_seleccionado]

        st.markdown(f"**Código del producto:** `{id_producto}`")
        st.markdown(f"**Precio unitario:** ${precio_unitario:.2f}")

        cantidad = st.number_input("Cantidad a ingresar", min_value=1, max_value=1000, step=1, key="cantidad_producto")
        st.markdown(f"**Precio total:** ${precio_unitario * cantidad:.2f}")

        if st.button("Registrar"):
            try:
                st.write("📌 Registrando abastecimiento...")
                st.write(f"ID Emprendimiento: {id_emprendimiento}, ID Producto: {id_producto}, Cantidad: {cantidad}")

                # Insertar en ABASTECIMIENTO
                cursor.execute("""
                    INSERT INTO ABASTECIMIENTO (ID_Emprendimiento, ID_Producto, Cantidad, Fecha_ingreso)
                    VALUES (%s, %s, %s, NOW())
                """, (id_emprendimiento, id_producto, cantidad))

                # Insertar en INVENTARIO
                cursor.execute("""
                    INSERT INTO INVENTARIO (ID_Producto, Cantidad_ingresada, Stock, Fecha_ingreso)
                    VALUES (%s, %s, %s, NOW())
                """, (id_producto, cantidad, cantidad))

                con.commit()
                st.success("✅ Abastecimiento registrado exitosamente.")

            except Exception as e:
                st.error(f"❌ Error al registrar en base de datos: {e}")

    except Exception as e:
        st.error(f"❌ Error general: {e}")

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'con' in locals(): con.close()

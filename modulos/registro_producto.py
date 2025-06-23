import streamlit as st
from modulos.config.conexion import obtener_conexion

def registrar_producto():
    st.header("📓 Registrar nuevo producto")

    # Inicializar estado si no existe
    if "emprendimiento_seleccionado" not in st.session_state:
        st.session_state.emprendimiento_seleccionado = "— Selecciona —"

    # Obtener lista de emprendimientos
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        cursor.execute("SELECT ID_Emprendimiento, Nombre_emprendimiento FROM EMPRENDIMIENTO")
        emprendimientos = cursor.fetchall()
        cursor.close()
        con.close()
    except Exception as e:
        st.error(f"❌ Error al cargar emprendimientos: {e}")
        return

    if not emprendimientos:
        st.warning("⚠️ No hay emprendimientos registrados.")
        return

    # Crear diccionario {nombre: id}
    opciones = {nombre: id_ for id_, nombre in emprendimientos}
    lista_nombres = ["— Selecciona —"] + list(opciones.keys())

    # Restablecer st.session_state.emprendimiento_seleccionado antes de renderizar el selectbox
    if st.session_state.emprendimiento_seleccionado not in lista_nombres:
        st.session_state.emprendimiento_seleccionado = "— Selecciona —"

    # Renderizar el selectbox
    seleccion = st.selectbox(
        "Selecciona un emprendimiento",
        lista_nombres,
        index=lista_nombres.index(st.session_state.emprendimiento_seleccionado),
        key="emprendimiento_seleccionado"
    )

    # Si no se ha seleccionado un emprendimiento, detener
    if seleccion == "— Selecciona —":
        st.info("🔹 Selecciona un emprendimiento para continuar.")
        st.stop()

    id_emprendimiento = opciones[seleccion]
    st.text_input("ID del Emprendimiento", value=id_emprendimiento, disabled=True)

    # Formulario del producto
    id_producto = st.text_input("ID del Producto")
    nombre_producto = st.text_input("Nombre del producto")
    descripcion = st.text_area("Descripción")
    precio = st.number_input("Precio", min_value=0.0, step=0.01)
    tipo_producto = st.selectbox("Tipo de producto", ["Perecedero", "No perecedero"])

    if st.button("Registrar"):
        if not all([id_producto, nombre_producto, descripcion, precio, tipo_producto, id_emprendimiento]):
            st.warning("⚠️ Por favor, completa todos los campos.")
        else:
            try:
                # Verificar la conexión y ejecutar la inserción
                con = obtener_conexion()
                cursor = con.cursor()

                # Comprobamos si el producto ya existe para evitar duplicados
                cursor.execute("SELECT COUNT(*) FROM PRODUCTO WHERE ID_Producto = %s", (id_producto,))
                existe = cursor.fetchone()[0]
                if existe:
                    st.warning("⚠️ El producto con ese ID ya existe.")
                else:
                    cursor.execute("""
                        INSERT INTO PRODUCTO (
                            ID_Producto, Nombre_producto, Descripcion, Precio,
                            Tipo_producto, ID_Emprendimiento
                        )
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        id_producto, nombre_producto, descripcion, precio,
                        tipo_producto, id_emprendimiento
                    ))

                    con.commit()
                    st.success("✅ Producto registrado correctamente.")

                    # Restablecer la selección antes de la recarga
                    st.session_state.emprendimiento_seleccionado = "— Selecciona —"

                    # Recargar la página para reiniciar el formulario
                    st.experimental_rerun()

            except Exception as e:
                st.error(f"❌ Error al registrar el producto: {e}")
            finally:
                if 'cursor' in locals(): cursor.close()
                if 'con' in locals(): con.close()

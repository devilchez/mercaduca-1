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

    # Modificar st.session_state.emprendimiento_seleccionado antes de crear el selectbox
    if st.session_state.emprendimiento_seleccionado not in lista_nombres:
        st.session_state.emprendimiento_seleccionado = "— Selecciona —"

    # Determinar el índice de la opción seleccionada
    indice = lista_nombres.index(st.session_state.emprendimiento_seleccionado)

    # Renderizar el selectbox
    seleccion = st.selectbox(
        "Selecciona un emprendimiento",
        lista_nombres,
        index=indice,
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
                con = obtener_conexion()
                cursor = con.cursor()

                # Insertar el producto en la tabla
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
                st.success(f"✅ Producto registrado correctamente con ID: {id_producto}")
                st.session_state.secciones = [{"id": 0, "emprendimiento": None, "productos": []}]
                st.session_state.contador_secciones = 1
                st.rerun()

            except Exception as e:
                st.error(f"❌ Error al registrar el producto: {e}")
            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'con' in locals():
                    con.close()

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

    # Validar valor actual en el estado
    if st.session_state.emprendimiento_seleccionado not in lista_nombres:
        st.session_state.emprendimiento_seleccionado = "— Selecciona —"

    # Determinar el índice de la opción seleccionada
    indice = lista_nombres.index(st.session_state.emprendimiento_seleccionado)

    # Selectbox con clave de estado
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

    # Formulario con claves para poder limpiar luego
    id_producto = st.text_input("ID del Producto", key="id_producto")
    nombre_producto = st.text_input("Nombre del producto", key="nombre_producto")
    descripcion = st.text_area("Descripción", key="descripcion")
    precio = st.number_input("Precio", min_value=0.0, step=0.01, key="precio")
    tipo_producto = st.selectbox("Tipo de producto", ["Perecedero", "No perecedero"], key="tipo_producto")

    if st.button("Registrar"):
        if not all([
            st.session_state.id_producto,
            st.session_state.nombre_producto,
            st.session_state.descripcion,
            st.session_state.precio,
            st.session_state.tipo_producto,
            id_emprendimiento
        ]):
            st.warning("⚠️ Por favor, completa todos los campos.")
        else:
            try:
                con = obtener_conexion()
                cursor = con.cursor()

                # Insertar el producto
                cursor.execute("""
                    INSERT INTO PRODUCTO (
                        ID_Producto, Nombre_producto, Descripcion, Precio,
                        Tipo_producto, ID_Emprendimiento
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    st.session_state.id_producto,
                    st.session_state.nombre_producto,
                    st.session_state.descripcion,
                    st.session_state.precio,
                    st.session_state.tipo_producto,
                    id_emprendimiento
                ))

                con.commit()
                st.success(f"✅ Producto registrado correctamente con ID: {st.session_state.id_producto}")

                # Limpiar los campos del formulario
                st.session_state.emprendimiento_seleccionado = "— Selecciona —"
                st.session_state.pop("id_producto", None)
                st.session_state.pop("nombre_producto", None)
                st.session_state.pop("descripcion", None)
                st.session_state.pop("precio", None)
                st.session_state.pop("tipo_producto", None)

                st.rerun()

            except Exception as e:
                st.error(f"❌ Error al registrar el producto: {e}")
            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'con' in locals():
                    con.close()


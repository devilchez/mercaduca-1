import streamlit as st
from modulos.config.conexion import obtener_conexion
from datetime import date

def registrar_producto():
    if "usuario" not in st.session_state:
        st.warning("⚠️ Debes iniciar sesión.")
        st.stop()

    st.header("📓 Registrar nuevo producto")

    # Obtener lista de emprendimientos desde la BD
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        cursor.execute("SELECT ID_Emprendimiento, Nombre_emprendimiento FROM EMPRENDIMIENTO")
        emprendimientos = cursor.fetchall()
    except Exception as e:
        st.error(f"❌ Error al obtener emprendimientos: {e}")
        return
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'con' in locals(): con.close()

    # Convertir a diccionario para fácil acceso
    emprend_dict = {nombre: id_ for id_, nombre in emprendimientos}

    # Selección desde lista desplegable
    nombre_emprendimiento = st.selectbox("Selecciona el emprendimiento", ["— Selecciona —"] + list(emprend_dict.keys()))

    # Inicializar ID
    id_emprendimiento = ""
    if nombre_emprendimiento != "— Selecciona —":
        id_emprendimiento = emprend_dict[nombre_emprendimiento]

    # Mostrar el ID del emprendimiento como campo deshabilitado solo para mostrar
    st.text_input("ID del Emprendimiento", value=id_emprendimiento, disabled=True)

    # Resto del formulario
    id_producto = st.text_input("ID del Producto")
    nombre_producto = st.text_input("Nombre del producto")
    descripcion = st.text_area("Descripción")
    precio = st.number_input("Precio", min_value=0.0, step=0.01)
    tipo_producto = st.selectbox("Tipo de producto", ["Perecedero", "No perecedero"])

    if st.button("Registrar"):
        if not (id_producto and nombre_producto and descripcion and precio and tipo_producto and id_emprendimiento):
            st.warning("⚠️ Por favor, completa todos los campos.")
        else:
            try:
                con = obtener_conexion()
                cursor = con.cursor()

                cursor.execute("""
                    INSERT INTO PRODUCTO (
                        ID_Producto, Nombre_producto, Descripcion, Precio,
                        Tipo_producto, ID_Emprendimiento
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    id_producto, nombre_producto, descripcion, precio,
                    tipo_producto, id_emprendimiento,
                ))

                con.commit()
                st.success("✅ Producto registrado correctamente.")

            except Exception as e:
                st.error(f"❌ Error al registrar: {e}")
            finally:
                if 'cursor' in locals(): cursor.close()
                if 'con' in locals(): con.close()

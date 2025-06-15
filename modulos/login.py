import streamlit as st
from modulos.config.conexion import obtener_conexion
from modulos.ventas import mostrar_ventas
from modulos.abastecimiento import mostrar_abastecimiento

def verificar_usuario(usuario, contrasena):
    con = obtener_conexion()
    if not con:
        st.error("⚠️ No se pudo conectar a la base de datos.")
        return None

    try:
        cursor = con.cursor()
        query = "SELECT Tipo_usuario FROM USUARIO WHERE usuario = %s AND contrasena = %s"
        cursor.execute(query, (usuario, contrasena))
        result = cursor.fetchone()
        return result[0] if result else None
    finally:
        con.close()

def login():
    st.title("Inicio de sesión")
    usuario = st.text_input("Usuario", key="usuario_input")
    contrasena = st.text_input("Contraseña", type="password", key="contrasena_input")

    if st.button("Iniciar sesión"):
        tipo = verificar_usuario(usuario, contrasena)
        if tipo:
            st.session_state["usuario"] = usuario
            st.session_state["tipo_usuario"] = tipo
            st.success(f"Bienvenido ({tipo})")
            st.experimental_rerun()
        else:
            st.error("Credenciales incorrectas")

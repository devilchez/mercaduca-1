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
    usuario = st.text_input("Usuario")
    contrasena = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):
        tipo = verificar_usuario(usuario, contrasena)
        if tipo:
            st.success(f"Bienvenido ({tipo})")
            if tipo == "Administrador":
                mostrar_ventas()
            elif tipo == "Asistente":
                mostrar_abastecimiento(usuario)
        else:
            st.error("Credenciales incorrectas")

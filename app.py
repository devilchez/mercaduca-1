import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'modulos'))

import streamlit as st
from modulos.login import login
from modulos.ventas import mostrar_ventas
from modulos.reporte_ventas import reporte_ventas
from modulos.abastecimiento import mostrar_abastecimiento
from modulos.registro_emprendimiento import registrar_emprendimiento
from modulos.registro_producto import registrar_producto
from modulos.emprendimientos import mostrar_emprendimientos
from modulos.productos import mostrar_productos
from modulos.inventario import mostrar_inventario
from modulos.dashboard import dashboard

st.set_page_config(page_title="MERCADUCA", layout="centered")

# ========== ESTILO PERSONALIZADO ==========
st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700&display=swap" rel="stylesheet">
    <style>
    .centered-title {
        text-align: center;
        font-size: 4em;
        font-weight: bold;
        color: #4b7045;
        margin-bottom: 0;
        font-family: 'Montserrat', sans-serif;
    }
    .subtext {
        text-align: center;
        font-size: 1.2em;
        color: #777777;
        margin-top: 0;
        font-style: italic;
    }
    </style>
    <div class="centered-title">MERCAGESTIÓN</div>
    <div class="subtext">Para MERCADUCA</div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    .logo-bottom-left {
        position: fixed;
        bottom: 15px;
        left: 15px;
        width: 120px;
        z-index: 100;
    }
    </style>
    """, unsafe_allow_html=True
)

st.markdown(
    '<img class="logo-bottom-left" src="https://raw.githubusercontent.com/devilchez/mercaduca-1/main/img/logo.png">',
    unsafe_allow_html=True
)

# ========== AUTENTICACIÓN ==========
if "usuario" not in st.session_state or "tipo_usuario" not in st.session_state:
    login()
else:
    tipo = st.session_state["tipo_usuario"]

    st.sidebar.title("Menú")

    # Menú según tipo de usuario
    if tipo == "Administrador":
        opciones_menu = [
            "Dashboard",
            "Ventas",
            "Reporte de ventas",
            "Abastecimiento",
            "Registrar Emprendimiento",
            "Gestionar Emprendimiento",
            "Registrar Productos",
            "Gestionar Productos",
            "Inventario",
        ]
    elif tipo == "Asistente":
        opciones_menu = [
            "Ventas",
            "Reporte de ventas"
            "Inventario",
        ]
    else:
        opciones_menu = []

    # Mostrar el menú si hay opciones
    if opciones_menu:
        opcion = st.sidebar.radio("Ir a:", opciones_menu)
    else:
        st.warning("⚠️ Tu tipo de usuario no tiene módulos asignados.")
        st.stop()

    st.sidebar.markdown("<br><hr><br>", unsafe_allow_html=True)

    if st.sidebar.button("🔓 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

    # === Rutas a módulos según tipo y opción seleccionada ===
    if opcion == "Ventas":
        mostrar_ventas()
    elif opcion == "Dashboard" and tipo == "Administrador":
        dashboard()
    elif opcion == "Reporte de ventas" and tipo == "Administrador":
        reporte_ventas()
    elif opcion == "Abastecimiento" and tipo == "Administrador":
        mostrar_abastecimiento()
    elif opcion == "Registrar Emprendimiento" and tipo == "Administrador":
        registrar_emprendimiento()
    elif opcion == "Gestionar Emprendimiento" and tipo == "Administrador":
        mostrar_emprendimientos()
    elif opcion == "Registrar Productos" and tipo == "Administrador":
        registrar_producto()
    elif opcion == "Gestionar Productos" and tipo == "Administrador":
        mostrar_productos()
    elif opcion == "Inventario":
        mostrar_inventario()
    else:
        st.warning("No tienes permiso para acceder a esta sección.")

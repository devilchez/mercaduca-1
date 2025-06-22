import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'modulos'))

import streamlit as st
from modulos.login import login
from modulos.ventas import mostrar_ventas
from modulos.abastecimiento import mostrar_abastecimiento
from modulos.registro_emprendimiento import registrar_emprendimiento
from modulos.registro_producto import registrar_producto
from modulos.emprendimientos import mostrar_emprendimientos
from modulos.productos import mostrar_productos

st.set_page_config(page_title="MERCADUCA", layout="centered")

st.markdown(
    """
    <style>
    .centered-title {
        text-align: center;
        font-size: 4em;
        font-weight: bold;
        color: #2e4d26;
        margin-bottom: 0.1em;
    }
    .subtext {
        text-align: center;
        font-size: 1.2em;
        color: #777777;
        margin-top: 0;
    }
    </style>
    <div class="centered-title">MERCAGESTIÓN</div>
    <div class="subtext">para MERCADUCA</div>
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
        width: 80px;  /* Tamaño del logo */
        z-index: 100;
    }
    </style>
    """, unsafe_allow_html=True
)

# ✅ Mostrar el logo con clase correcta y ruta válida
st.markdown(
    '<img class="logo-bottom-left" src="https://raw.githubusercontent.com/devilchez/mercaduca-1/main/img/logo.png">',
    unsafe_allow_html=True
)


# 🔐 Control de sesión
if "usuario" not in st.session_state or "tipo_usuario" not in st.session_state:
    login()
else:
    tipo = st.session_state["tipo_usuario"]

    st.sidebar.title("Menú")
    opcion = st.sidebar.radio(
        "Ir a:",
        [
            "Ventas",
            "Abastecimiento",
            "Registrar Emprendedor",
            "Gestionar Emprendedores",
            "Registrar Producto",
            "Gestionar Productos",
        ]
    )

    st.sidebar.markdown("<br><hr><br>", unsafe_allow_html=True)

    if st.sidebar.button("🔓 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

    if opcion == "Ventas" and tipo in ["Asistente", "Administrador"]:
        mostrar_ventas()
    elif opcion == "Abastecimiento" and tipo in ["Administrador"]:
        mostrar_abastecimiento()
    elif opcion == "Registrar Emprendedor" and tipo in ["Administrador"]:
        registrar_emprendimiento()
    elif opcion == "Gestionar Emprendedores" and tipo in ["Administrador"]:
        mostrar_emprendimientos()
    elif opcion == "Registrar Producto" and tipo in ["Administrador"]:
        registrar_producto()
    elif opcion == "Gestionar Productos" and tipo in ["Administrador"]:
        mostrar_productos()
    else:
        st.warning("No tienes permiso para acceder a esta sección.")

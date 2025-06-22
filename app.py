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
    .top-right {
        position: absolute;
        top: 10px;
        right: 10px;
        width: 100px;  /* Ajusta el tamaño de la imagen */
    }
    </style>
    """, unsafe_allow_html=True
)

# ✅ Insertar la imagen con el estilo aplicado
st.markdown('<img class="top-right" src="https://github.com/devilchez/mercaduca-1/raw/main/img/logo.png">', unsafe_allow_html=True)


# 🔐 Control de sesión
if "usuario" not in st.session_state or "tipo_usuario" not in st.session_state:
    login()
else:
    tipo = st.session_state["tipo_usuario"]

    # 📌 Menú lateral
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

    # Espacio para separar el botón inferior
    st.sidebar.markdown("<br><hr><br>", unsafe_allow_html=True)

    # 🔲 Botón de cerrar sesión al final de la barra lateral
    if st.sidebar.button("🔓 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()


    # ▶️ Ejecutar módulo correspondiente
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

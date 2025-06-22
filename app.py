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
from modulos.productos import mostrar_productos  # ✅ Importamos la función para gestionar productos

st.set_page_config(page_title="MERCADUCA", layout="centered")

# 🔐 Control de sesión
if "usuario" not in st.session_state or "tipo_usuario" not in st.session_state:
    login()
else:
    tipo = st.session_state["tipo_usuario"]

    # 🔲 Botón de cerrar sesión en la esquina superior derecha
    col1, col2 = st.columns([9, 1])
    with col2:
        if st.button("🔓 Cerrar sesión"):
            st.session_state.clear()
            st.rerun()

    # 📌 Menú lateral con radio
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

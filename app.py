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

    # ✅ Inicializar la opción en el estado si no existe
    if "opcion_menu" not in st.session_state:
        st.session_state.opcion_menu = None

    st.sidebar.title("Menú")

    # ✅ Definir botones que actualizan el estado
    if st.sidebar.button("Ventas"):
        st.session_state.opcion_menu = "Ventas"
    elif st.sidebar.button("Abastecimiento"):
        st.session_state.opcion_menu = "Abastecimiento"
    elif st.sidebar.button("Registrar Emprendedor"):
        st.session_state.opcion_menu = "Registrar Emprendedor"
    elif st.sidebar.button("Gestionar Emprendedores"):
        st.session_state.opcion_menu = "Gestionar Emprendedores"
    elif st.sidebar.button("Registrar Producto"):
        st.session_state.opcion_menu = "Registrar Producto"
    elif st.sidebar.button("Gestionar Productos"):
        st.session_state.opcion_menu = "Gestionar Productos"
    elif st.sidebar.button("Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

    # ✅ Ejecutar la opción activa
    opcion = st.session_state.opcion_menu

    if opcion == "Ventas" and tipo == "Administrador":
        mostrar_ventas()
    elif opcion == "Abastecimiento" and tipo in ["Asistente", "Administrador"]:
        mostrar_abastecimiento()
    elif opcion == "Registrar Emprendedor" and tipo in ["Asistente", "Administrador"]:
        registrar_emprendimiento()
    elif opcion == "Gestionar Emprendedores" and tipo in ["Asistente", "Administrador"]:
        mostrar_emprendimientos()
    elif opcion == "Registrar Producto" and tipo in ["Asistente", "Administrador"]:
        registrar_producto()
    elif opcion == "Gestionar Productos" and tipo in ["Asistente", "Administrador"]:
        mostrar_productos()
    elif opcion is not None:
        st.warning("No tienes permiso para acceder a esta sección.")

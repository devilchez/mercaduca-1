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

    st.sidebar.title("Menú")

    opcion = None
    if st.sidebar.button("Ventas"):
        opcion = "Ventas"
    elif st.sidebar.button("Abastecimiento"):
        opcion = "Abastecimiento"
    elif st.sidebar.button("Registrar Emprendedor"):
        opcion = "Registrar Emprendedor"
    elif st.sidebar.button("Gestionar Emprendedores"):
        opcion = "Gestionar Emprendedores"
    elif st.sidebar.button("Registrar Producto"):
        opcion = "Registrar Producto"
    elif st.sidebar.button("Gestionar Productos"):
        opcion = "Gestionar Productos"
    elif st.sidebar.button("Cerrar sesión"):
        opcion = "Cerrar sesión"

    # 🔄 Redirigir según la opción seleccionada
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
    elif opcion == "Cerrar sesión":
        st.session_state.clear()
        st.rerun()
    elif opcion is not None:
        st.warning("No tienes permiso para acceder a esta sección.")

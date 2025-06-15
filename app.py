import streamlit as st
from modulos.config.login import login

st.set_page_config(page_title="MERCADUCA", layout="centered")
login()

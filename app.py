import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'modulos'))

from modulos.login import log


import streamlit as st


st.set_page_config(page_title="MERCADUCA", layout="centered")
login()

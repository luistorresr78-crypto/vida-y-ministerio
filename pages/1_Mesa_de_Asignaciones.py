import streamlit as st
import requests

st.set_page_config(page_title="Mesa de Asignaciones", page_icon="📋", layout="wide")
st.title("📋 Mesa de Asignaciones")

URL_BASE = "https://supabase.co"
HEADERS_NUBE = {
    "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV0cnhkemRodmdmbXJuZnRtdm52Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcyNTI4MzM2MCwiZXhwIjoyMDQwODU5MzYwfQ.jRPh_3C65GzZ_r2Z6tU1jD6V_T11_354Jv_t11VvT-w",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV0cnhkemRodmdmbXJuZnRtdm52Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcyNTI4MzM2MCwiZXhwIjoyMDQwODU5MzYwfQ.jRPh_3C65GzZ_r2Z6tU1jD6V_T11_354Jv_t11VvT-w",
    "Content-Type": "application/json"
}

st.info("Módulo 1 inicializado de forma multimodular blindada. Listo para recibir la carga de programaciones mensuales.")

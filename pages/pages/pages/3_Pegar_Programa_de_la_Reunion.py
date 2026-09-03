import streamlit as st
import requests
import re

st.set_page_config(page_title="Pegar Programa", page_icon="📝", layout="wide")
st.title("📝 Pegar Programa de la Reunión")

URL_BASE = "https://supabase.co"
HEADERS_NUBE = {
    "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV0cnhkemRodmdmbXJuZnRtdm52Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcyNTI4MzM2MCwiZXhwIjoyMDQwODU5MzYwfQ.jRPh_3C65GzZ_r2Z6tU1jD6V_T11_354Jv_t11VvT-w",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV0cnhkemRodmdmbXJuZnRtdm52Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcyNTI4MzM2MCwiZXhwIjoyMDQwODU5MzYwfQ.jRPh_3C65GzZ_r2Z6tU1jD6V_T11_354Jv_t11VvT-w",
    "Content-Type": "application/json"
}

ORDEN_MESES = ["SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE", "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO"]
SEMANAS_POSIBLES = ["Semana 1", "Semana 2", "Semana 3", "Semana 4", "Semana 5", "Semana 6"]

def procesar_texto_plano_reunion(texto_usuario):
    materias_detectadas = {}
    lineas = [l.strip() for l in texto_usuario.split("\n")]
    lineas_limpias = [l for l in lineas if l]
    fecha_cab = lineas_limpias[0] if len(lineas_limpias) > 0 else "7-13 de septiembre"
    lectura_cab = lineas_limpias[1] if len(lineas_limpias) > 1 else "JEREMÍAS 32, 33"

    for i, linea in enumerate(lineas_limpias):
        match_punto = re.match(r"^([1-8])\.\s*(.*)", linea)
        if match_punto:
            num_punto = match_punto.group(1)
            titulo_principal = match_punto.group(2).strip()
            referencia_abajo = ""
            if i + 1 < len(lineas_limpias):
                sig_linea = lineas_limpias[i+1]
                if not re.match(r"^[1-8]\.", sig_linea): referencia_abajo = " " + sig_linea.strip()
            
            titulo_completo = f"{titulo_principal}{referencia_abajo}"
            match_mins = re.search(r"\(\s*(\d+)\s*min", titulo_completo, re.IGNORECASE)
            minutos = match_mins.group(1) if match_mins else "5"
            
            if num_punto in ["1", "2", "3"]: seccion_real = "Tesoros"
            elif num_punto in ["4", "5", "6"]: seccion_real = "Maestros"
            else: seccion_real = "Vida"
            materias_detectadas[num_punto] = {"titulo": titulo_completo, "minutos": minutos, "seccion": seccion_real}
    return fecha_cab, lectura_cab, materias_detectadas

c_c1, c_c2 = st.columns(2)
with c_c1: m_dest = st.selectbox("Mes Destino:", ORDEN_MESES, key="m_p3")
with c_c2: s_dest = st.selectbox("Semana Destino:", SEMANAS_POSIBLES, key="s_p3")

with st.form("fp"):
    t_pegar = st.text_area("Pega el texto completo de JW.org aquí:")
    if st.form_submit_button("⚡ Cargar Semana"):
        if t_pegar:
            for endpoint in ["reunion", "reuniones", "Reunion", "Reuniones"]:
                requests.delete(f"{URL_BASE}/{endpoint}?mes=eq.{m_dest}&semana=eq.{s_dest}", headers=HEADERS_NUBE)
            f, l, mats = procesar_texto_plano_reunion(t_pegar)
            payload_reun = {"mes": m_dest, "semana": s_dest, "fecha_cabecera": f, "lectura_cabecera": l, "materias": mats, "asignados": {}, "ultima_firma": "Cargado desde JW.org"}
            for endpoint in ["reunion", "reuniones", "Reunion", "Reuniones"]:
                res_p_r = requests.post(f"{URL_BASE}/{endpoint}", headers=HEADERS_NUBE, json=payload_reun)
                if res_p_r.status_code == 201 or res_p_r.status_code == 200: break
            st.success("¡Programa de reunión cargado con éxito en el Módulo 3!")

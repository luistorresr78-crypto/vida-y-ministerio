import streamlit as st
import json
import os
import re
import requests
import reglas

# Configuración adaptativa de la página web
st.set_page_config(page_title="Mesa de Asignaciones Teocráticas", page_icon="📝", layout="wide")

# CONEXIÓN BLINDADA A TU BASE DE DATOS SUPABASE
SUPABASE_URL = "https://supabase.co"
SUPABASE_HEADERS = {
    "apikey": "sb_publishable_GpDoDvr1ejZChSiAThb4uQ_-60A9S08",
    "Authorization": "Bearer sb_publishable_GpDoDvr1ejZChSiAThb4uQ_-60A9S08",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# Carga en tiempo real desde la nube con ordenamiento estricto por Nombre
def cargar_hermanos_cloud():
    try:
        response = requests.get(SUPABASE_URL, headers=SUPABASE_HEADERS, timeout=10)
        if response.status_code == 200:
            lista_raw = response.json()
            # Estandariza a Tipo Título y ordena de la A a la Z por el Nombre de pila
            lista_saneada = []
            for h in lista_raw:
                lista_saneada.append({
                    "id": h.get("id"),
                    "nombre": h.get("nombre", "").strip().title(),
                    "apellido": h.get("apellido", "").strip().title(),
                    "sexo": h.get("sexo", "Varón"),
                    "aptitudes": h.get("aptitudes", [])
                })
            return sorted(lista_saneada, key=lambda x: (x.get("nombre", "").lower(), x.get("apellido", "").lower()))
    except Exception:
        pass
    return []

lista_hermanos = cargar_hermanos_cloud()

# --- PROCESADOR EXTRACTOR DE JW.ORG ---
def procesar_texto_plano_reunion(texto_usuario):
    materias_detectadas = {}
    lineas = [l.strip() for l in texto_usuario.split("\n") if l.strip()]
    
    fecha_cab = lineas[0] if len(lineas) > 0 else "7-13 de septiembre"
    lectura_cab = lineas[1] if len(lineas) > 1 else "JEREMÍAS 32, 33"

    for linea in lineas:
        match_punto = re.match(r"^([1-8])\.\s*(.*)", linea)
        if match_punto:
            num_punto = match_punto.group(1)
            contenido = match_punto.group(2)
            
            match_mins = re.search(r"\(\s*(\d+)\s*min", contenido, re.IGNORECASE)
            minutos = match_mins.group(1) if match_mins else "5"
            titulo_completo = contenido.strip()
            
            if num_punto in ["1", "2", "3"]: seccion_real = "Tesoros"
            elif num_punto in ["4", "5", "6"]: seccion_real = "Maestros"
            else: seccion_real = "Vida"
                
            materias_detectadas[num_punto] = {
                "titulo": titulo_completo,
                "minutos": minutos,
                "seccion": seccion_real
            }
            
    if not materias_detectadas:
        materias_detectadas = {
            "1": {"titulo": "1. Discurso (10 mins.)", "minutos": "10", "seccion": "Tesoros"},
            "2": {"titulo": "2. Perlas de la Biblia (10 mins.)", "minutos": "10", "seccion": "Tesoros"},
            "3": {"titulo": "3. Lectura de la Biblia (4 mins.)", "minutos": "4", "seccion": "Tesoros"}
        }
    return fecha_cab, lectura_cab, materias_detectadas

# --- MENÚ SUPERIOR DE PESTAÑAS WEB ---
pestana_programa, pestana_hermanos = st.tabs([
    "🚀 Fabricador en Caliente de Folletos", 
    "👥 Gestión de Hermanos (Nómina)"
])

with pestana_programa:
    st.header("⚡ Generador Instantáneo de Folletos Oficiales")
    texto_jw_entrada = st.text_area("Pega aquí el texto completo copiado de JW.org:", height=180, key="txt_jw_live")

    f_cab, l_cab, materias_dinamicas = procesar_texto_plano_reunion(texto_jw_entrada)

    st.markdown("---")
    st.subheader(f"📅 Vista Previa: {f_cab}")
    st.info(f"📖 Lectura Bíblica Detectada: **{l_cab}**")

    with st.sidebar:
        st.header("⚙️ Control de Operación")
        coordinador_activo = st.selectbox("¿Quién asigna hoy?", ["Sergio", "Jonathan", "Luis"], key="coord_live")

    with st.form("formulario_live_seguro"):
        st.markdown("### 🎚️ Asignar Privilegios para el Folleto")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            opciones_presi = reglas.filtrar_ayudantes_inteligente("", lista_hermanos, "Presidencia")
            presidente = st.selectbox("Presidente", [h["nombre"] for h in opciones_presi], key="sel_presi_v")
        with col_p2:
            opciones_ora = reglas.filtrar_ayudantes_inteligente("", lista_hermanos, "Oración")
            oracion_inicial = st.selectbox("Oración Inicial", [h["nombre"] for h in opciones_ora], key="sel_ora_v")

        st.markdown("---")
        asignados_en_vivo = {"presidente": presidente, "oracion_inicial": oracion_inicial}
        
        for k in sorted(materias_dinamicas.keys(), key=lambda x: int(x) if x.isdigit() else 999):
            m = materias_dinamicas[k]
            tipo_seccion = m.get("seccion", "Tesoros")
            color_sub = "Seamos Mejores Maestros" if tipo_seccion == "Maestros" else ("Vida Cristiana" if tipo_seccion == "Vida" else "Tesoros de la Biblia")
            
            st.markdown(f"**{k}. {m.get('titulo', '')}**")
            opciones_materia = reglas.filtrar_ayudantes_inteligente("", lista_hermanos, color_sub)
            nombres_materia = [h["nombre"] for h in opciones_materia]
            if "" not in nombres_materia: nombres_materia.insert(0, "")
                
            c1, c2 = st.columns(2)
            with c1:
                titular = st.selectbox(f"Asignado punto {k}", nombres_materia, key=f"t_{k}_live")
                asignados_en_vivo[f"p{k}_t"] = titular
            with c2:
                if tipo_seccion == "Maestros":
                    opciones_ayudante = reglas.filtrar_ayudantes_inteligente(titular, lista_hermanos, "Seamos Mejores Maestros")
                    nombres_ayudante = [h["nombre"] for h in opciones_ayudante]
                    if "" not in nombres_ayudante: nombres_ayudante.insert(0, "")
                    ayudante = st.selectbox(f"Ayudante punto {k}", nombres_ayudante, key=f"a_{k}_live")
                    asignados_en_vivo[f"p{k}_a"] = ayudante

        boton_armar = st.form_submit_button("⚙️ Procesar Datos para Descarga")

    st.markdown("### 🖨️ Descargar Documento Final (Paso 2)")
    if boton_armar:
        reglas.generar_pdf_estilo_oficial(l_cab, f_cab, materias_dinamicas, asignados_en_vivo)
        st.session_state["pdf_listo"] = True
        st.session_state["f_cab_guardada"] = f_cab
        st.session_state["l_cab_guardada"] = l_cab
        st.success("¡Folleto procesado con éxito total!")

    if st.session_state.get("pdf_listo", False):
        nombre_archivo_pdf = "Reunion_PROCESADO_WEB.pdf"
        f_cab_g = st.session_state.get("f_cab_guardada", "Semana")
        if os.path.exists(nombre_archivo_pdf):
            with open(nombre_archivo_pdf, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()
            st.download_button(label="🟣 Descargar Folleto Oficial en PDF", data=pdf_bytes, file_name=f"Reunion_{f_cab_g.replace(' ', '_')}.pdf", mime="application/pdf", key="btn_descarga_final_live")

with pestana_hermanos:
    st.header("👥 Control de la Nómina de la Congregación")
    col_add, col_del = st.columns(2)
    
    with col_add:
        st.subheader("➕ Agregar Nuevo Hermano/a")
        with st.form("form_alta_hermano_live"):
            nuevo_nom = st.text_input("Nombre:")
            nuevo_ape = st.text_input("Apellido:")
            nuevo_sexo = st.selectbox("Sexo:", ["Varón", "Mujer"])
            nuevas_apt = st.multiselect("Asignar Aptitudes:", ["Tesoros", "Lectura", "Seamos Mejores Maestros", "Presidencia", "Oración", "Vida Cristiana"])
            if st.form_submit_button("Añadir Publicador"):
                if nuevo_nom and nuevo_ape:
                    payload = {"nombre": nuevo_nom.strip().title(), "apellido": nuevo_ape.strip().title(), "sexo": nuevo_sexo, "aptitudes": nuevas_apt}
                    requests.post(SUPABASE_URL, headers=SUPABASE_HEADERS, json=payload)
                    st.success("¡Añadido a la nube de por vida!")
                    st.rerun()

    with col_del:
        st.subheader("❌ Dar de Baja Publicador")
        nombres_baja = [f"{h['nombre']} {h['apellido']}" for h in lista_hermanos]
        hermano_a_eliminar = st.selectbox("Seleccione quién dar de baja:", nombres_baja, key="baja_sel_live")
        if st.button("Confirmar Eliminación Permanente", type="primary"):
            target = next((h for h in lista_hermanos if f"{h['nombre']} {h['apellido']}" == hermano_a_eliminar), None)
            if target and target.get("id"):
                requests.delete(f"{SUPABASE_URL}?id=eq.{target['id']}", headers=SUPABASE_HEADERS)
                st.warning("Eliminado de la nube.")
                st.rerun()

    st.markdown("---")
    st.subheader("📜 Listado Oficial de la Congregación (Nube - Orden Alfabético por Nombre)")
    st.table([{"Nombre": h.get("nombre"), "Apellido": h.get("apellido"), "Sexo": h.get("sexo"), "Aptitudes": ", ".join(h.get("aptitudes", []))} for h in lista_hermanos])

import streamlit as st
import json
import os
import re
import requests
import reglas

# --- CONFIGURACIÓN Y LLAVES DE CONEXIÓN BLINDADA A TU CUENTA DE SUPABASE ---
SUPABASE_URL = "https://supabase.co"
SUPABASE_KEY = "sb_publishable_GpDoDvr1ejZChSiAThb4uQ_-60A9S08"

SUPABASE_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

ORDEN_MESES = ["SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE", "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO"]
SEMANAS_POSIBLES = ["Semana 1", "Semana 2", "Semana 3", "Semana 4", "Semana 5", "Semana 6"]

# 1. CARGA DE LA NÓMINA DESDE LA NUBE (ORDEN ALFABÉTICO POR NOMBRE)
def cargar_hermanos_cloud():
    try:
        url = f"{SUPABASE_URL}/rest/v1/hermanos"
        res = requests.get(url, headers=SUPABASE_HEADERS, timeout=10)
        if res.status_code == 200:
            lista = res.json()
            saneada = []
            for h in lista:
                saneada.append({
                    "id": h.get("id"),
                    "nombre": h.get("nombre", "").strip().title(),
                    "apellido": h.get("apellido", "").strip().title(),
                    "sexo": h.get("sexo", "Varón"),
                    "aptitudes": h.get("aptitudes", [])
                })
            return sorted(saneada, key=lambda x: (x.get("nombre", "").lower(), x.get("apellido", "").lower()))
    except Exception: pass
    return []

# 2. CARGA DEL HISTORIAL CONTINUO DESDE LA NUBE (SEPTIEMBRE A AGOSTO)
def cargar_reuniones_cloud():
    try:
        url = f"{SUPABASE_URL}/rest/v1/reuniones"
        res = requests.get(url, headers=SUPABASE_HEADERS, timeout=10)
        if res.status_code == 200:
            lista = res.json()
            dicc_reuns = {}
            for r in lista:
                m = r.get("mes")
                s = r.get("semana")
                if m not in dicc_reuns: dicc_reuns[m] = {}
                dicc_reuns[m][s] = {
                    "fecha_cabecera": r.get("fecha_cabecera"),
                    "lectura_cabecera": r.get("lectura_cabecera"),
                    "materias": r.get("materias", {}),
                    "asignados": r.get("asignados", {}),
                    "ultima_firma": r.get("ultima_firma", "")
                }
            return dicc_reuns
    except Exception: pass
    return {}

# 3. CARGA DE LA BITÁCORA DE REEMPLAZOS DE ÚLTIMA HORA
def cargar_reemplazos_cloud():
    try:
        url = f"{SUPABASE_URL}/rest/v1/reemplazos"
        res = requests.get(url, headers=SUPABASE_HEADERS, timeout=10)
        if res.status_code == 200: return res.json()
    except Exception: pass
    return []

lista_hermanos = cargar_hermanos_cloud()
datos_reuniones = cargar_reuniones_cloud()
lista_reemplazos = cargar_reemplazos_cloud()

# --- PROCESADOR EXTRACTOR DE JW.ORG (ABSORBE MINS. Y REF. LARGAS) ---
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
                
            materias_detectadas[num_punto] = {"titulo": titulo_completo, "minutos": minutos, "seccion": seccion_real}
            
    if not materias_detectadas:
        materias_detectadas = {
            "1": {"titulo": "1. Discurso (10 mins.)", "minutos": "10", "seccion": "Tesoros"},
            "2": {"titulo": "2. Perlas de la Biblia (10 mins.)", "minutos": "10", "seccion": "Tesoros"},
            "3": {"titulo": "3. Lectura de la Biblia (4 mins.)", "minutos": "4", "seccion": "Tesoros"}
        }
    return fecha_cab, lectura_cab, materias_detectadas

# --- MENÚ SUPERIOR DE PESTAÑAS WEB ---
pestana_asignaciones, pestana_hermanos, pestana_reuniones = st.tabs([
    "📋 Mesa de Asignaciones", "👥 Gestión de Hermanos (Nómina)", "📝 Pegar Programa de la Reunión"
])
# =========================================================================
# PESTAÑA 1: MESA DE ASIGNACIONES (HISTORIAL, REEMPLAZOS Y ALERTAS)
# =========================================================================
with pestana_asignaciones:
    col_mes, col_sem = st.columns(2)
    with col_mes:
        mes_seleccionado = st.selectbox("Seleccione el Mes (Historial Continuo):", ORDEN_MESES, key="sel_mes_v2")
    with col_sem:
        semana_seleccionada = st.selectbox("Seleccione la Semana:", SEMANAS_POSIBLES, key="sel_sem_v2")

    if mes_seleccionado not in datos_reuniones: datos_reuniones[mes_seleccionado] = {}
    if semana_seleccionada not in datos_reuniones[mes_seleccionado]:
        datos_reuniones[mes_seleccionado][semana_seleccionada] = {
            "fecha_cabecera": f"Semana de {mes_seleccionado.capitalize()}", "lectura_cabecera": "Lectura Oficial por Cargar",
            "materias": {
                "1": {"titulo": "1. Discurso (10 mins.)", "minutos": "10", "seccion": "Tesoros"}, 
                "2": {"titulo": "2. Perlas de la Biblia (10 mins.)", "minutos": "10", "seccion": "Tesoros"}, 
                "3": {"titulo": "3. Lectura de la Biblia (4 mins.)", "minutos": "4", "seccion": "Tesoros"}
            },
            "asignados": {}, "ultima_firma": ""
        }

    semana_data = datos_reuniones[mes_seleccionado][semana_seleccionada]
    materias = semana_data.get("materias", {})
    asignados_actuales = semana_data.get("asignados", {})

    st.subheader(f"📅 Rango de Fecha: {semana_data.get('fecha_cabecera')}")
    st.info(f"📖 Lectura de la Semana: **{semana_data.get('lectura_cabecera')}**")
    if semana_data.get("ultima_firma"): st.caption(f"✍️ {semana_data.get('ultima_firma')}")

    with st.sidebar:
        st.header("⚙️ Control de Operación")
        coordinador_activo = st.selectbox("¿Quién firma hoy?", ["Sergio", "Jonathan", "Luis"], key="coord_firma")
        st.markdown("---")
        st.header("♻️ Reemplazos del Mes")
        with st.form("form_reemplazos_live"):
            h_ausente = st.text_input("Hermano Ausente:")
            h_sustituto = st.text_input("Hermano Suplente:")
            if st.form_submit_button("Guardar Reemplazo"):
                if h_ausente and h_sustituto:
                    pld = {"hermano_ausente": h_ausente.strip().title(), "hermano_sustituto": h_sustituto.strip().title()}
                    url_remp = f"{SUPABASE_URL}/rest/v1/reemplazos"
                    requests.post(url_remp, headers=SUPABASE_HEADERS, json=pld)
                    st.success("¡Suplencia registrada!")
                    st.rerun()
        if lista_reemplazos:
            with st.expander("📝 Ver bitácora de suplentes"):
                for rem in lista_reemplazos[-5:]: st.text(f"❌ {rem.get('hermano_ausente')} -> ✅ {rem.get('hermano_sustituto')}")

    conteo_mes = {}
    for sem_k, sem_v in datos_reuniones[mes_seleccionado].items():
        if sem_k != semana_seleccionada:
            asig_sem = sem_v.get("asignados", {})
            for rol, nom_val in asig_sem.items():
                if nom_val and nom_val != "Por asignar": conteo_mes[nom_val] = conteo_mes.get(nom_val, 0) + 1

    with st.form("formulario_mesa_v2"):
        st.markdown("### 🎎️ Asignar Privilegios de la Semana")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            opciones_presi = reglas.filtrar_ayudantes_inteligente("", lista_hermanos, "Presidencia")
            nom_presi = [h["nombre"] for h in opciones_presi]
            idx_presi = nom_presi.index(asignados_actuales.get("presidente")) if asignados_actuales.get("presidente") in nom_presi else 0
            presidente = st.selectbox("Presidente de la Reunión", nom_presi, index=idx_presi)
        with col_p2:
            opciones_ora = reglas.filtrar_ayudantes_inteligente("", lista_hermanos, "Oración")
            nom_ora = [h["nombre"] for h in opciones_ora]
            idx_ora = nom_ora.index(asignados_actuales.get("oracion_inicial")) if asignados_actuales.get("oracion_inicial") in nom_ora else 0
            oracion_inicial = st.selectbox("Oración Inicial", nom_ora, index=idx_ora)

        st.markdown("---")
        nuevos_asignados = {"presidente": presidente, "oracion_inicial": oracion_inicial}
        
        for k in sorted(materias.keys(), key=lambda x: int(x) if x.isdigit() else 999):
            m = materias[k]
            tipo_seccion = m.get("seccion", "Tesoros")
            color_sub = "Seamos Mejores Maestros" if tipo_seccion == "Maestros" else ("Vida Cristiana" if tipo_seccion == "Vida" else "Tesoros de la Biblia")
            st.markdown(f"**{k}. {m.get('titulo', '')}** ({m.get('minutos', '')} mins.)")
            opciones_materia = reglas.filtrar_ayudantes_inteligente("", lista_hermanos, color_sub)
            
            opciones_con_alerta = []
            for h in opciones_materia:
                nombre_h = h["nombre"]
                if nombre_h in conteo_mes: opciones_con_alerta.append(f"{nombre_h} (⚠️ REPETIDO x{conteo_mes[nombre_h]})")
                else: opciones_con_alerta.append(nombre_h)
            if "" not in opciones_con_alerta: opciones_con_alerta.insert(0, "")
            
            idx_t = 0
            curr_val = asignados_actuales.get(f"p{k}_t", "")
            if curr_val:
                for idx_item, item_txt in enumerate(opciones_con_alerta):
                    if item_txt.startswith(curr_val): idx_t = idx_item; break

            c1, c2 = st.columns(2)
            with c1:
                titular_sel = st.selectbox(f"Asignado punto {k}", opciones_con_alerta, index=idx_t, key=f"t_v2_{k}")
                titular_limpio = titular_sel.split(" (⚠️") if titular_sel else ""
                nuevos_asignados[f"p{k}_t"] = titular_limpio
            with c2:
                if tipo_seccion == "Maestros":
                    opciones_ayudante = reglas.filtrar_ayudantes_inteligente(titular_limpio, lista_hermanos, "Seamos Mejores Maestros")
                    opciones_ayu_alerta = []
                    for h in opciones_ayudante:
                        nombre_h = h["nombre"]
                        if nombre_h in conteo_mes: opciones_ayu_alerta.append(f"{nombre_h} (⚠️ REPETIDO x{conteo_mes[nombre_h]})")
                        else: opciones_ayu_alerta.append(nombre_h)
                    if "" not in opciones_ayu_alerta: opciones_ayu_alerta.insert(0, "")
                    
                    idx_a = 0
                    curr_ayu = asignados_actuales.get(f"p{k}_a", "")
                    if curr_ayu:
                        for idx_item, item_txt in enumerate(opciones_ayu_alerta):
                            if item_txt.startswith(curr_ayu): idx_a = idx_item; break
                                
                    ayudante_sel = st.selectbox(f"Ayudante punto {k}", opciones_ayu_alerta, index=idx_a, key=f"a_v2_{k}")
                    ayudante_limpio = ayudante_sel.split(" (⚠️") if ayudante_sel else ""
                    nuevos_asignados[f"p{k}_a"] = ayudante_limpio

        st.markdown("---")
        boton_guardar = st.form_submit_button("💾 Guardar Asignaciones en la Nube")

    if boton_guardar:
        firma_texto = f"Modificado por: {coordinador_activo}"
        payload_reun = {"mes": mes_seleccionado, "semana": semana_seleccionada, "fecha_cabecera": semana_data.get("fecha_cabecera"), "lectura_cabecera": semana_data.get("lectura_cabecera"), "materias": materias, "asignados": nuevos_asignados, "ultima_firma": firma_texto}
        url_reun = f"{SUPABASE_URL}/rest/v1/reurniones" if "reurniones" in locals() else f"{SUPABASE_URL}/rest/v1/reuniones"
        requests.post(url_reun, headers={**SUPABASE_HEADERS, "Prefer": "resolution=merge-duplicates"}, json=payload_reun)
        st.success(f"¡Cambios guardados permanentemente por {coordinador_activo}!")
        st.rerun()

    st.markdown("### 🖨️ Generación de Documento")
    if st.button("⚙️ Procesa Formato Carta/A4 (Paso 1)"):
        reglas.generar_pdf_estilo_oficial(semana_data.get('lectura_cabecera'), semana_data.get('fecha_cabecera'), materias, nuevos_asignados)
        st.session_state["pdf_listo_v2"] = True
        st.success("¡Folleto estirado y procesado de forma oficial!")

    if st.session_state.get("pdf_listo_v2", False):
        nombre_archivo_pdf = "Reunion_PROCESADO_WEB.pdf"
        if os.path.exists(nombre_archivo_pdf):
            with open(nombre_archivo_pdf, "rb") as pdf_file: pdf_bytes = pdf_file.read()
            st.download_button(label="🟣 Descargar Folleto Oficial en PDF", data=pdf_bytes, file_name=f"Reunion_{semana_seleccionada}_{mes_seleccionado}.pdf", mime="application/pdf")
# =========================================================================
# PESTAÑA 2: GESTIÓN DE HERMANOS (NÓMINA INDESTRUCTIBLE CON SUPABASE)
# =========================================================================
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
            btn_dar_alta = st.form_submit_button("Añadir Publicador")
            
            if btn_dar_alta:
                if nuevo_nom and nuevo_ape:
                    payload = {"nombre": nuevo_nom.strip().title(), "apellido": nuevo_ape.strip().title(), "sexo": nuevo_sexo, "aptitudes": nuevas_apt}
                    url_alta = f"{SUPABASE_URL}/rest/v1/hermanos"
                    requests.post(url_alta, headers=SUPABASE_HEADERS, json=payload)
                    st.success(f"¡{nuevo_nom.strip().title()} ha sido añadido a la nube de por vida!")
                    st.rerun()
                else: st.error("Por favor ingresa Nombre y Apellido.")

    with col_del:
        st.subheader("❌ Dar de Baja Publicador")
        nombres_baja = [f"{h['nombre']} {h['apellido']}" for h in lista_hermanos]
        hermano_a_eliminar = st.selectbox("Seleccione quién dar de baja:", nombres_baja, key="baja_sel_live")
        
        if st.button("Confirmar Eliminación Permanente", type="primary", key="btn_baja_live"):
            target = next((h for h in lista_hermanos if f"{h['nombre']} {h['apellido']}" == hermano_a_eliminar), None)
            if target and target.get("id"):
                url_baja = f"{SUPABASE_URL}/rest/v1/hermanos?id=eq.{target['id']}"
                requests.delete(url_baja, headers=SUPABASE_HEADERS)
                st.warning(f"¡{hermano_a_eliminar} ha sido eliminado de la nube!")
                st.rerun()

    st.markdown("---")
    st.subheader("📜 Listado Oficial de la Congregación (Nube - Orden Alfabético por Nombre)")
    tabla_visual = []
    for h in lista_hermanos:
        tabla_visual.append({"Nombre": h.get("nombre", ""), "Apellido": h.get("apellido", ""), "Sexo": h.get("sexo", "Varón"), "Aptitudes Registradas": ", ".join(h.get("aptitudes", []))})
    st.table(tabla_visual)

# =========================================================================
# PESTAÑA 3: NUEVO COPIADOR ADAPTATIVO CON FUSIONADO EN NUBE
# =========================================================================
with pestana_reuniones:
    st.header("📝 Pegar Programa de la Reunión (Copiador Humano)")
    st.markdown("Copia la Guía de Actividades semanal desde **JW.org**, pégala aquí abajo en español común y el programa extraerá automáticamente la fecha, la lectura bíblica y los minutos reales.")
    
    col_cfg1, col_cfg2 = st.columns(2)
    with col_cfg1:
        mes_destino_txt = st.selectbox("¿A qué mes pertenece esta lectura?", ORDEN_MESES, key="mes_p3")
    with col_cfg2:
        semana_destino_txt = st.selectbox("¿A qué semana deseas asignarle esta programación?", SEMANAS_POSIBLES, key="sem_p3")

    with st.form("form_pegar_texto_plano"):
        st.markdown("⚠️ **Nota:** Asegúrate de que las dos primeras líneas del texto que pegues abajo sean la **Fecha** y la **Lectura Bíblica**.")
        texto_plano_pegar = st.text_area("Pega aquí el texto completo copiado de JW.org:", height=250, placeholder="Escribe o pega aquí el texto...")
        btn_procesar_humano = st.form_submit_button("⚡ Procesar y Cargar Semana Inmediatamente")
        
        if btn_procesar_humano:
            if texto_plano_pegar:
                f_cab, l_cab, materias_detectadas = procesar_texto_plano_reunion(texto_plano_pegar)
                
                payload_reun = {
                    "mes": mes_destino_txt, "semana": semana_destino_txt,
                    "fecha_cabecera": f_cab, "lectura_cabecera": l_cab,
                    "materias": materias_detectadas, "asignados": {},
                    "ultima_firma": "Cargado automáticamente desde JW.org"
                }
                url_reun_p3 = f"{SUPABASE_URL}/rest/v1/reuniones"
                requests.post(url_reun_p3, headers={**SUPABASE_HEADERS, "Prefer": "resolution=merge-duplicates"}, json=payload_reun)
                st.success(f"¡Éxito rotundo! {semana_destino_txt} de {mes_destino_txt} cargada con fecha y lectura automática en internet.")
                st.rerun()
            else: st.error("El cuadro de texto está vacío.")

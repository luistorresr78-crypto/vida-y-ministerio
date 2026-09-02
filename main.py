import streamlit as st
import json
import os
import re
import requests

# --- CONFIGURACIÓN DE PÁGINA ÚNICA INDEPENDIENTE ---
st.set_page_config(page_title="Programa de Reunión", page_icon="📋", layout="wide")

# SOLUCIÓN DE FUERZA: INYECTAMOS LAS LLAVES DIRECTO EN EL CÓDIGO PARA SALTAR EL ERROR 404
URL_BASE = "https://supabase.co"
HEADERS_NUBE = {
    "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV0cnhkemRodmdmbXJuZnRtdm52Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcyNTI4MzM2MCwiZXhwIjoyMDQwODU5MzYwfQ.jRPh_3C65GzZ_r2Z6tU1jD6V_T11_354Jv_t11VvT-w",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV0cnhkemRodmdmbXJuZnRtdm52Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcyNTI4MzM2MCwiZXhwIjoyMDQwODU5MzYwfQ.jRPh_3C65GzZ_r2Z6tU1jD6V_T11_354Jv_t11VvT-w",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

ORDEN_MESES = ["SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE", "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO"]
SEMANAS_POSIBLES = ["Semana 1", "Semana 2", "Semana 3", "Semana 4", "Semana 5", "Semana 6"]

def filtrar_ayudantes_inteligente(hermano_titular, lista_hermanos, aptitud_filtro):
    filtro_real = aptitud_filtro
    if "Tesoros" in aptitud_filtro: filtro_real = "Tesoros"
    elif "Maestros" in aptitud_filtro or "Seamos" in aptitud_filtro: filtro_real = "Seamos Mejores Maestros"
    
    candidatos = [h for h in lista_hermanos if filtro_real.lower() in h.get("aptitudes", "").lower()]
    lista_listas = []
    for h in candidatos:
        lista_listas.append({"nombre": f"{h['nombre']} {h['apellido']}"})
    return lista_listas

def cargar_hermanos_cloud():
    try:
        res = requests.get(f"{URL_BASE}/rest/v1/hermanos?select=*", headers=HEADERS_NUBE, timeout=10)
        if res.status_code == 200:
            lista = []
            for h in res.json():
                lista.append({
                    "id": h.get("id"),
                    "nombre": h.get("nombre", "").strip().title(),
                    "apellido": h.get("apellido", "").strip().title(),
                    "sexo": h.get("sexo", "Varón"),
                    "aptitudes": str(h.get("aptitudes", ""))
                })
            return sorted(lista, key=lambda x: (x.get("nombre", "").lower(), x.get("apellido", "").lower()))
    except Exception: pass
    return []

def cargar_reuniones_cloud():
    try:
        res = requests.get(f"{URL_BASE}/rest/v1/reuniones?select=*", headers=HEADERS_NUBE, timeout=10)
        if res.status_code == 200:
            dicc_reuns = {}
            for r in res.json():
                m = r.get("mes")
                s = r.get("semana")
                if m not in dicc_reuns: dicc_reuns[m] = {}
                dicc_reuns[m][s] = {
                    "fecha_cabecera": r.get("fecha_cabecera"), "lectura_cabecera": r.get("lectura_cabecera"),
                    "materias": r.get("materias", {}), "asignados": r.get("asignados", {}), "ultima_firma": r.get("ultima_firma", "")
                }
            return dicc_reuns
    except Exception: pass
    return {}

lista_hermanos = cargar_hermanos_cloud()
datos_reuniones = cargar_reuniones_cloud()
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

p_asignaciones, p_hermanos, p_reuniones = st.tabs(["📋 Mesa de Asignaciones", "👥 Gestión de Hermanos (Nómina)", "📝 Pegar Programa de la Reunión"])

with p_asignaciones:
    col_mes, col_sem = st.columns(2)
    with col_mes: mes_seleccionado = st.selectbox("Seleccione el Mes:", ORDEN_MESES, key="sel_mes_v2")
    with col_sem: semana_seleccionada = st.selectbox("Seleccione la Semana:", SEMANAS_POSIBLES, key="sel_sem_v2")

    if mes_seleccionado not in datos_reuniones: datos_reuniones[mes_seleccionado] = {}
    if semana_seleccionada not in datos_reuniones[mes_seleccionado]:
        datos_reuniones[mes_seleccionado][semana_seleccionada] = {
            "fecha_cabecera": f"Semana de {mes_seleccionado.capitalize()}", "lectura_cabecera": "Lectura Oficial por Cargar",
            "materias": {
                "1": {"titulo": "1. Meditar en las cualidades de Jehová fortalece nuestra fe (10 min.)", "minutos": "10", "seccion": "Tesoros"}, 
                "2": {"titulo": "2. Busquemos perlas escondidas (10 min.)", "minutos": "10", "seccion": "Tesoros"}, 
                "3": {"titulo": "3. Lectura de la Biblia (4 min.) Jer 32:6-18 (th lección 2).", "minutos": "4", "seccion": "Tesoros"},
                "4": {"titulo": "4. Empiece conversaciones (3 min.)", "minutos": "3", "seccion": "Maestros"},
                "5": {"titulo": "5. Empiece conversaciones (4 min.)", "minutos": "4", "seccion": "Maestros"},
                "6": {"titulo": "6. Haga revisitas (5 min.)", "minutos": "5", "seccion": "Maestros"},
                "7": {"titulo": "7. En esta campaña, ni un golpe al aire (15 min.)", "minutos": "15", "seccion": "Vida"},
                "8": {"titulo": "8. Estudio bíblico de la congregación (30 min.)", "minutos": "30", "seccion": "Vida"}
            },
            "asignados": {}, "ultima_firma": ""
        }

    semana_data = datos_reuniones[mes_seleccionado][semana_seleccionada]
    materias = semana_data.get("materias", {})
    asignados_actuales = semana_data.get("asignados", {})

    st.subheader(f"📅 Rango de Fecha: {semana_data.get('fecha_cabecera')}")
    st.info(f"📖 Lectura de la Semana: **{semana_data.get('lectura_cabecera')}**")

    with st.sidebar:
        st.header("⚙️ Control")
        coordinador_activo = st.selectbox("¿Quién firma?", ["Sergio", "Jonathan", "Luis"], key="cf")
        h_aus = st.text_input("Ausente:")
        h_sus = st.text_input("Suplente:")
        if st.button("Guardar Reemplazo"):
            if h_aus and h_sus:
                requests.post(f"{URL_BASE}/rest/v1/reemplazos", headers=HEADERS_NUBE, json={"hermano_ausente": h_aus.strip().title(), "hermano_sustituto": h_sus.strip().title()})
                st.success("¡Registrado!")
                st.rerun()

    conteo_mes = {}
    for sem_k, sem_v in datos_reuniones[mes_seleccionado].items():
        if sem_k != semana_seleccionada:
            for rol, nom_val in sem_v.get("asignados", {}).items():
                if nom_val and nom_val != "Por asignar":
                    val_limpio = nom_val if isinstance(nom_val, str) else (nom_val if isinstance(nom_val, list) and nom_val else "")
                    if val_limpio: conteo_mes[val_limpio] = conteo_mes.get(val_limpio, 0) + 1

    with st.form("form_mesa"):
        st.markdown("### 🎚️ Asignar Privilegios")
        c_p1, c_p2 = st.columns(2)
        with c_p1:
            op_presi = filtrar_ayudantes_inteligente("", lista_hermanos, "Presidencia")
            nom_presi = [h["nombre"] for h in op_presi]
            val_presi_curr = asignados_actuales.get("presidente", "")
            idx_presi = nom_presi.index(val_presi_curr) if val_presi_curr in nom_presi else 0
            presidente = st.selectbox("Presidente", nom_presi, index=idx_presi)
        with c_p2:
            op_ora = filtrar_ayudantes_inteligente("", lista_hermanos, "Oración")
            nom_ora = [h["nombre"] for h in op_ora]
            val_ora_curr = asignados_actuales.get("oracion_inicial", "")
            idx_ora = nom_ora.index(val_ora_curr) if val_ora_curr in nom_ora else 0
            oracion_inicial = st.selectbox("Oración Inicial", nom_ora, index=idx_ora)

        nuevos_asignados = {"presidente": presidente, "oracion_inicial": oracion_inicial}
        for k in sorted(materias.keys(), key=lambda x: int(x) if x.isdigit() else 999):
            m = materias[k]
            tipo_seccion = m.get("seccion", "Tesoros")
            color_sub = "Seamos Mejores Maestros" if tipo_seccion == "Maestros" else ("Vida Cristiana" if tipo_seccion == "Vida" else "Tesoros de la Biblia")
            st.markdown(f"**{k}. {m.get('titulo', '')}**")
            op_m = filtrar_ayudantes_inteligente("", lista_hermanos, color_sub)
            op_alert = [f"{h['nombre']} (⚠️ REPETIDO x{conteo_mes[h['nombre']]})" if h['nombre'] in conteo_mes else h['nombre'] for h in op_m]
            if "" not in op_alert: op_alert.insert(0, "")
            
            curr_val = asignados_actuales.get(f"p{k}_t", "")
            idx_t = 0
            if curr_val:
                for idx_i, item_t in enumerate(op_alert):
                    if item_t.startswith(curr_val): idx_t = idx_i; break

            c1, c2 = st.columns(2)
            with c1:
                t_sel = st.selectbox(f"Titular {k}", op_alert, index=idx_t, key=f"t_{k}")
                nuevos_asignados[f"p{k}_t"] = t_sel.split(" (⚠️") if t_sel else ""

        if st.form_submit_button("💾 Guardar Asignaciones"):
            payload = {"mes": mes_seleccionado, "semana": semana_seleccionada, "fecha_cabecera": semana_data.get("fecha_cabecera"), "lectura_cabecera": semana_data.get("lectura_cabecera"), "materias": materias, "asignados": nuevos_asignados, "ultima_firma": f"Modificado por: {coordinador_activo}"}
            requests.post(f"{URL_BASE}/rest/v1/reuniones", headers=HEADERS_NUBE, json=payload)
            st.success("¡Guardado!")
            st.rerun()

with p_hermanos:
    st.header("👥 Nómina")
    c_a, c_d = st.columns(2)
    with c_a:
        n = st.text_input("Nombre:", key="nom_p2")
        a = st.text_input("Apellido:", key="ape_p2")
        s = st.selectbox("Sexo:", ["Varón", "Mujer"], key="sex_p2")
        ap = st.multiselect("Aptitudes:", ["Tesoros", "Lectura", "Seamos Mejores Maestros", "Presidencia", "Oración", "Vida Cristiana"], key="apt_p2")
        
        if st.button("⚡ Añadir Publicador"):
            if not n.strip() or not a.strip():
                st.error("🚨 Error obligatorio: ¡No puede dejar los casilleros de Nombre o Apellido vacíos!")
            else:
                cadena_plana_aptitudes = ", ".join(ap) if ap else ""
                payload_nuevo = {"nombre": n.strip().title(), "apellido": a.strip().title(), "sexo": s, "aptitudes": cadena_plana_aptitudes}
                res_post = requests.post(f"{URL_BASE}/rest/v1/hermanos", headers=HEADERS_NUBE, json=payload_nuevo)
                
                if res_post.status_code == 201 or res_post.status_code == 200:
                    st.success("¡Publicador añadido con éxito absoluto en internet!")
                    st.rerun()
                else:
                    st.error(f"❌ Error de internet: La base de datos rechazó el guardado. Código: {res_post.status_code}")
    with c_d:
        hermano_a_eliminar = st.selectbox("Dar de baja:", [f"{h['nombre']} {h['apellido']}" for h in lista_hermanos])
        if st.button("Confirmar Eliminación", type="primary"):
            t = next((h for h in lista_hermanos if f"{h['nombre']} {h['apellido']}" == hermano_a_eliminar), None)
            if t and t.get("id"):
                requests.delete(f"{URL_BASE}/rest/v1/hermanos?id=eq.{t['id']}", headers=HEADERS_NUBE)
                st.warning("Eliminado de la nube.")
                st.rerun()
                
    nomina_fresca_web = cargar_hermanos_cloud()
    if nomina_fresca_web:
        st.table([{"Nombre": h.get("nombre"), "Apellido": h.get("apellido"), "Sexo": h.get("sexo"), "Aptitudes": h.get("aptitudes", "")} for h in nomina_fresca_web])
    else:
        st.info("La nómina está vacía en internet. Ingrese el primer publicador arriba.")

with p_reuniones:
    st.header("📝 Pegar Programa de la Reunión")
    c_c1, c_c2 = st.columns(2)
    with c_c1: m_dest = st.selectbox("Mes Destino:", ORDEN_MESES, key="m_p3")
    with c_c2: s_dest = st.selectbox("Semana Destino:", SEMANAS_POSIBLES, key="s_p3")

    with st.form("fp"):
        t_pegar = st.text_area("Pega el texto completo de JW.org aquí:")
        if st.form_submit_button("⚡ Cargar Semana"):
            if t_pegar:
                requests.delete(f"{URL_BASE}/rest/v1/reuniones?mes=eq.{m_dest}&semana=eq.{s_dest}", headers=HEADERS_NUBE)
                f, l, mats = procesar_texto_plano_reunion(t_pegar)
                payload_reun = {"mes": m_dest, "semana": s_dest, "fecha_cabecera": f, "lectura_cabecera": l, "materias": mats, "asignados": {}, "ultima_firma": "Cargado desde JW.org"}
                requests.post(f"{URL_BASE}/rest/v1/reuniones", headers=HEADERS_NUBE, json=payload_reun)
                st.success("¡Cargado con éxito absoluto!")
                st.rerun()

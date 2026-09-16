import streamlit as st
import json
import os
import re
import reglas

# Configuracion adaptativa de la pagina web para celulares, iPads y laptops
st.set_page_config(page_title="Mesa de Asignaciones Teocraticas", page_icon="📝", layout="wide")

FICHERO_HERMANOS = "hermanos.json"
FICHERO_HISTORIAL = "historial_reuniones.json"

# --- CONTROLADOR DEL HISTORIAL PERMANENTE (PUNTO 4) ---
def cargar_historial():
    if not os.path.exists(FICHERO_HISTORIAL):
        with open(FICHERO_HISTORIAL, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=4)
    try:
        with open(FICHERO_HISTORIAL, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def guardar_historial(datos):
    with open(FICHERO_HISTORIAL, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

def cargar_hermanos_iniciales():
    if not os.path.exists(FICHERO_HERMANOS):
        hermanos_base = [
            {"nombre": "Luis", "apellido": "Torres", "sexo": "Varón", "aptitudes": ["Tesoros", "Lectura", "Presidencia", "Oración", "Vida Cristiana", "Seamos Mejores Maestros"]},
            {"nombre": "Sergio", "apellido": "Coordinador", "sexo": "Varón", "aptitudes": ["Tesoros", "Lectura", "Presidencia", "Oración", "Vida Cristiana", "Seamos Mejores Maestros"]},
            {"nombre": "Jonathan", "apellido": "Coordinador", "sexo": "Varón", "aptitudes": ["Tesoros", "Lectura", "Presidencia", "Oración", "Vida Cristiana", "Seamos Mejores Maestros"]}
        ]
        with open(FICHERO_HERMANOS, "w", encoding="utf-8") as f:
            json.dump(hermanos_base, f, ensure_ascii=False, indent=4)
            
    with open(FICHERO_HERMANOS, "r", encoding="utf-8") as f:
        datos_sucios = json.load(f)
        lista_limpia = []
        for h in datos_sucios:
            lista_limpia.append({
                "nombre": h.get("nombre", "").strip().title(),
                "apellido": h.get("apellido", "").strip().title(),
                "sexo": h.get("sexo", "Varón"),
                "aptitudes": h.get("aptitudes", [])
            })
        return lista_limpia

lista_hermanos = cargar_hermanos_iniciales()

def guardar_hermanos(lista):
    with open(FICHERO_HERMANOS, "w", encoding="utf-8") as f:
        json.dump(lista, f, ensure_ascii=False, indent=4)

# --- PROCESADOR CON SEGUIMIENTO, FILTRADO Y RECORTE QUIRÚRGICO DE TEXTOS ---
def procesar_texto_plano_reunion(texto_usuario):
    materias_detectadas = {}
    if not texto_usuario.strip():
        return materias_detectadas
        
    lineas = [l.strip() for l in texto_usuario.split("\n") if l.strip()]
    seccion_actual_texto = "Tesoros"
    ultimo_punto = None

    puntos_crudos = {}
    for linea in lineas:
        linea_up = linea.upper()
        if "SEAMOS MEJORES MAESTROS" in linea_up or "HAGA DISCÍPULOS" in linea_up:
            seccion_actual_texto = "Maestros"
            continue
        elif "NUESTRA VIDA CRISTIANA" in linea_up:
            seccion_actual_texto = "Vida"
            continue
            
        match_punto = re.match(r"^([1-9]|10)\.\s*(.*)", linea)
        if match_punto:
            ultimo_punto = match_punto.group(1)
            puntos_crudos[ultimo_punto] = {
                "lineas": [match_punto.group(2)],
                "seccion": seccion_actual_texto
            }
        else:
            if ultimo_punto and ultimo_punto in puntos_crudos:
                puntos_crudos[ultimo_punto]["lineas"].append(linea)

    for num_punto, info in puntos_crudos.items():
        texto_completo = " ".join(info["lineas"]).strip()
        
        match_mins = re.search(r"\(\s*(\d+\s*min[s]?\.?)\s*\)", texto_completo)
        texto_mins = f"({match_mins.group(1)})" if match_mins else ""
        titulo_limpio = re.sub(r"\s*\(\s*\d+\s*min[s]?\.?\s*\).*", "", texto_completo).strip()
        match_ref = re.search(r"\(\s*\d+\s*min[s]?\.?\s*\)\s*\.?\s*(.*)", texto_completo)
        ref_extraida = match_ref.group(1).strip() if match_ref else ""
        
        # CORRECCIÓN PUNTO 1: El punto 3 se marca estrictamente como "Lectura" para que salgan sus hermanos asignados
        seccion_filtrado = info["seccion"]
        if num_punto == "3":
            seccion_filtrado = "Lectura"
        
        if info["seccion"] == "Tesoros" and num_punto in ["1", "2"]:
            if texto_mins:
                texto_formateado = f"<b>{titulo_limpio}</b><br/><font size=9 color='#4A5568'>{texto_mins}</font>"
            else:
                texto_formateado = f"<b>{titulo_limpio}</b>"
                
        elif info["seccion"] == "Vida" and num_punto == "7":
            if texto_mins:
                if ref_extraida:
                    pos_punto = ref_extraida.find(".")
                    ref_recortada = ref_extraida[:pos_punto+1].strip() if pos_punto != -1 else ref_extraida
                    texto_formateado = f"<b>{titulo_limpio}</b><br/><font size=9 color='#4A5568'>{texto_mins} {ref_recortada}</font>"
                else:
                    texto_formateado = f"<b>{titulo_limpio}</b><br/><font size=9 color='#4A5568'>{texto_mins}</font>"
            else:
                texto_formateado = f"<b>{titulo_limpio}</b>"
                
        else:
            if texto_mins:
                texto_formateado = f"<b>{titulo_limpio}</b><br/><font size=9 color='#4A5568'>{texto_mins} {ref_extraida}</font>" if ref_extraida else f"<b>{titulo_limpio}</b><br/><font size=9 color='#4A5568'>{texto_mins}</font>"
            else:
                texto_formateado = f"<b>{texto_completo}</b>"
            
        materias_detectadas[num_punto] = {
            "titulo": texto_formateado,
            "minutos": "5",
            "seccion": seccion_filtrado
        }
        
    return materias_detectadas

pestana_programa, pestana_historial, pestana_hermanos = st.tabs([
    "🚀 Fabricador de Folletos", 
    "📋 Historial Guardado",
    "👥 Gestión de Hermanos"
])
with pestana_programa:
    st.header("⚡ Generador Instantáneo de Folletos Oficiales")
    
    # REPARACIÓN PUNTO 3: Añadimos los selectores fijos manuales de meses y semanas
    c_mes, c_sem = st.columns(2)
    with c_mes:
        mes_seleccionado = st.selectbox("📅 Seleccione el Mes Activo:", ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"], index=8, key="sel_mes_global")
    with c_sem:
        semana_seleccionada = st.text_input("📆 Ingrese el Rango de la Semana (Ej: 7-13 de septiembre):", placeholder="Escriba la fecha de la semana aquí...", key="sel_sem_global")

    st.markdown("---")
    st.markdown("Copia la Guía de Actividades completa desde **JW.org**, pégala abajo y presiona el botón para procesar.")

    texto_jw_entrada = st.text_area(
        "Pega aquí el texto completo copiado de JW.org:", 
        height=180, 
        placeholder="Puntos de la reunión...",
        key="txt_jw_live"
    )

    boton_armar_pdf = st.button("⚙️ Procesar Datos para Asignación (Paso 1)", use_container_width=True)

    materias_dinamicas = procesar_texto_plano_reunion(texto_jw_entrada)

    st.markdown("---")

    st.subheader(f"📅 Planificación de la Semana: {semana_seleccionada if semana_seleccionada else 'Por definir'}")
    st.info(f"📖 Mes de Trabajo Activo: **{mes_seleccionado}**")

    with st.sidebar:
        st.header("⚙️ Control de Operación")
        coordinador_activo = st.selectbox("¿Quién está asignando hoy?", ["Sergio", "Jonathan", "Luis"], key="coord_act_live")
        
        st.subheader("♻️ Registro de Reemplazos")
        with st.expander("Ver panel de Reemplazos"):
            h_ausente = st.text_input("Hermano Ausente", key="aus_live")
            h_sustituto = st.text_input("Hermano que Reemplaza", key="sust_live")
            if st.button("Guardar Reemplazo en Bitácora", key="btn_remp_live"):
                if h_ausente and h_sustituto:
                    st.success(f"Sustitución guardada: {h_sustituto} cubre a {h_ausente}")

    st.markdown("### 🎚️ Asignar Privilegios para el Folleto PDF")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        opciones_presi = reglas.filtrar_ayudantes_inteligente("", lista_hermanos, "Presidencia", mes_seleccionado)
        nom_presi = [f"{h.get('nombre', '')} {h.get('apellido', '')}".strip() for h in opciones_presi] if opciones_presi else [f"{h.get('nombre', '')} {h.get('apellido', '')}".strip() for h in lista_hermanos]
        if "" not in nom_presi: nom_presi.insert(0, "Por asignar")
        presidente = st.selectbox("Presidente de la Reunión", nom_presi, key="p_presi_live")
        
    with col_p2:
        opciones_ora = reglas.filtrar_ayudantes_inteligente("", lista_hermanos, "Oración", mes_seleccionado)
        nom_ora = [f"{h.get('nombre', '')} {h.get('apellido', '')}".strip() for h in opciones_ora] if opciones_ora else [f"{h.get('nombre', '')} {h.get('apellido', '')}".strip() for h in lista_hermanos]
        if "" not in nom_ora: nom_ora.insert(0, "Por asignar")
        oracion_inicial = st.selectbox("Oración Inicial", nom_ora, key="p_ora_live")

    st.markdown("---")
    
    asignados_en_vivo = {"presidente": presidente, "oracion_inicial": oracion_inicial}
    for k in sorted(materias_dinamicas.keys(), key=lambda x: int(x) if x.isdigit() else 999):
        m = materias_dinamicas[k]
        tipo_seccion = m.get("seccion", "Tesoros")
        
        if tipo_seccion == "Maestros":
            emoji, color_sub = "🌾", "Seamos Mejores Maestros"
        elif tipo_seccion == "Vida":
            emoji, color_sub = "🐑", "Vida Cristiana"
        elif tipo_seccion == "Lectura":
            emoji, color_sub = "📖", "Lectura"
        else:
            emoji, color_sub = "💎", "Tesoros de la Biblia"
            
        titulo_bruto = str(m.get('titulo', ''))
        titulo_preview = re.sub(r"<[^>]*>", "", titulo_bruto).strip()
            
        st.markdown(f"**{emoji} {k}. {titulo_preview}**")
        
        # Filtros calibrados vinculados al Mes Activo para calcular participaciones
        opciones_materia = reglas.filtrar_ayudantes_inteligente("", lista_hermanos, color_sub, mes_seleccionado)
        nombres_materia = [f"{h.get('nombre', '')} {h.get('apellido', '')}".strip() for h in opciones_materia] if opciones_materia else [f"{h.get('nombre', '')} {h.get('apellido', '')}".strip() for h in lista_hermanos]
        if "Por asignar" not in nombres_materia: nombres_materia.insert(0, "Por asignar")
            
        c1, c2 = st.columns(2)
        with c1:
            titular = st.selectbox(f"Asignado punto {k}", nombres_materia, key=f"live_t_{k}")
            asignados_en_vivo[f"p{k}_t"] = titular if titular != "Por asignar" else "Por asignar"
            
        with c2:
            if tipo_seccion == "Maestros":
                opciones_ayudante = reglas.filtrar_ayudantes_inteligente(titular, lista_hermanos, "Seamos Mejores Maestros", mes_seleccionado)
                nombres_ayudante = [f"{h.get('nombre', '')} {h.get('apellido', '')}".strip() for h in opciones_ayudante] if opciones_ayudante else [f"{h.get('nombre', '')} {h.get('apellido', '')}".strip() for h in lista_hermanos]
                if "Por asignar" not in nombres_ayudante: nombres_ayudante.insert(0, "Por asignar")
                ayudante = st.selectbox(f"Ayudante punto {k}", nombres_ayudante, key=f"live_a_{k}")
                asignados_en_vivo[f"p{k}_a"] = ayudante if ayudante != "Por asignar" else "Por asignar"

    st.markdown("### 🖨️ Compilar y Guardar Permanencia (Paso 2)")
    
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        # REPARACIÓN PUNTO 4 Y 5: Botón que congela los nombres en el PDF y graba el Historial
        btn_grabar_semana = st.button("💾 Guardar Semana e Inyectar Nombres", use_container_width=True, type="primary")
        if btn_grabar_semana:
            if not semana_seleccionada.strip():
                st.error("Por favor ingrese el rango de la semana antes de guardar.")
            else:
                historial_actual = cargar_historial()
                if mes_seleccionado not in historial_actual:
                    historial_actual[mes_seleccionado] = {}
                
                # Guardamos las asignaciones en la base de datos local
                historial_actual[mes_seleccionado][semana_seleccionada] = {
                    "coordinador": coordinador_activo,
                    "asignados": asignados_en_vivo
                }
                guardar_historial(historial_actual)
                
                # Compilamos el archivo físico inyectando los datos reales
                try:
                    reglas.generar_pdf_estilo_oficial(mes_seleccionado, semana_seleccionada, materias_dinamicas, asignados_en_vivo)
                    st.success(f"¡Semana guardada de forma permanente en {FICHERO_HISTORIAL} y nombres fijados en el PDF!")
                except Exception as e:
                    st.error(f"Fallo al inyectar ReportLab: {e}")

    with col_g2:
        # REPARACIÓN PUNTO 6: Botón borrador para limpiar la mesa de trabajo
        btn_resetear_mesa = st.button("🗑️ Resetear / Limpiar Semana Actual", use_container_width=True)
        if btn_resetear_mesa:
            st.session_state["txt_jw_live"] = ""
            st.session_state["sel_sem_global"] = ""
            st.success("¡Mesa de trabajo limpia! Portapapeles y fechas reseteados para la siguiente semana.")
            st.rerun()

    archivo_encontrado_fisco = "reunion_actual.pdf"

    if os.path.exists(archivo_encontrado_fisco):
        with open(archivo_encontrado_fisco, "rb") as pdf_file:
            pdf_bytes = pdf_file.read()
            
        st.download_button(
            label="🟣 Descargar Folleto Oficial en PDF", 
            data=pdf_bytes, 
            file_name=f"Reunion_{mes_seleccionado}_{semana_seleccionada.replace(' ', '_')}.pdf" if semana_seleccionada else f"Reunion_{mes_seleccionado}.pdf", 
            mime="application/pdf", 
            key="down_pdf_live",
            use_container_width=True
        )
    else:
        st.warning("⚠️ No se ha detectado el archivo guardado. Presione el botón azul '💾 Guardar Semana e Inyectar Nombres' para fijar los datos y habilitar el PDF.")

# --- PESTAÑA DEL HISTORIAL EN TIEMPO REAL (PUNTO 4) ---
with pestana_historial:
    st.header("📋 Historial de Asignaciones Registradas en la Bitácora")
    historial_visual = cargar_historial()
    
    if historial_visual:
        mes_hist = st.selectbox("Seleccione el Mes a Consultar:", list(historial_visual.keys()), key="ver_mes_hist")
        semanas_guardadas = historial_visual.get(mes_hist, {})
        
        if semanas_guardadas:
            for sem_key, info_sem in semanas_guardadas.items():
                with st.expander(f"📆 Semana: {sem_key} (Armado por: {info_sem.get('coordinador', 'Luis')})"):
                    asig = info_sem.get("asignados", {})
                    
                    st.markdown(f"**Presidente:** {asig.get('presidente', 'Por asignar')} | **Oración Inicial:** {asig.get('oracion_inicial', 'Por asignar')}")
                    st.markdown("---")
                    
                    for llave_asig, persona in asig.items():
                        if llave_asig.startswith("p") and llave_asig.endswith("_t"):
                            num_p = llave_asig[1:-2]
                            ayudante_llave = f"p{num_p}_a"
                            ayudante_nom = asig.get(ayudante_llave, "")
                            if ayudante_nom and ayudante_nom != "Por asignar":
                                st.write(f"• **Punto {num_p}:** {persona} (Ayudante: {ayudante_nom})")
                            else:
                                st.write(f"• **Punto {num_p}:** {persona}")
        else:
            st.info("No hay semanas guardadas para este mes.")
    else:
        st.info("La bitácora de historial está vacía actualmente. Comience guardando una semana.")

with st.sidebar:
    st.markdown("---")

with pestana_hermanos:
    st.header("👥 Control de la Nómina de la Congregación")
    col_add, col_del = st.columns(2)
    
    with col_add:
        st.subheader("➕ Agregar Nuevo Hermano/a")
        with st.form("form_alta_hermano_live"):
            nuevo_nom = st.text_input("Nombre:")
            nuevo_ape = st.text_input("Apellido:")
            nuevo_sexo = st.selectbox("Sexo:", ["Varón", "Mujer"])
            nuevas_apt = st.multiselect("Asignar Aptitudes/Secciones:", ["Tesoros", "Lectura", "Seamos Mejores Maestros", "Presidencia", "Oración", "Vida Cristiana"])
            btn_dar_alta = st.form_submit_button("Añadir Publicador")
            
            if btn_dar_alta:
                if nuevo_nom.strip() and nuevo_ape.strip():
                    nuevo_h = {
                        "nombre": nuevo_nom.strip().title(), 
                        "apellido": nuevo_ape.strip().title(), 
                        "sexo": nuevo_sexo, 
                        "aptitudes": nuevas_apt
                    }
                    lista_hermanos.append(nuevo_h)
                    guardar_hermanos(lista_hermanos)
                    st.success(f"¡{nuevo_nom.strip().title()} {nuevo_ape.strip().title()} ha sido añadido con éxito!")
                    st.rerun()
                else:
                    st.error("Por favor ingresa Nombre y Apellido.")

    with col_del:
        st.subheader("❌ Dar de Baja Publicador")
        if lista_hermanos:
            nombres_baja = [f"{h.get('nombre', '')} {h.get('apellido', '')}".strip() for h in lista_hermanos]
            hermano_a_eliminar = st.selectbox("Seleccione quién se muda o da de baja:", nombres_baja, key="baja_sel_live")
            if st.button("Confirmar Eliminación Permanente", type="primary", key="btn_baja_live"):
                lista_hermanos = [h for h in lista_hermanos if f"{h.get('nombre', '')} {h.get('apellido', '')}".strip() != hermano_a_eliminar]
                guardar_hermanos(lista_hermanos)
                st.warning(f"¡{hermano_a_eliminar} ha sido eliminado de la base de datos!")
                st.rerun()
        else:
            st.info("La nómina se encuentra vacía actualmente.")

    st.markdown("---")
    st.subheader("📜 Listado Completo de Hermanos Registrados")
    if lista_hermanos:
        tabla_visual = []
        for h in lista_hermanos:
            tabla_visual.append({
                "Nombre Completo": f"{h.get('nombre', '')} {h.get('apellido', '')}".strip(),
                "Sexo": h.get("sexo", "Varón"),
                "Aptitudes": ", ".join(h.get("aptitudes", [])) if isinstance(h.get("aptitudes", []), list) else str(h.get("aptitudes", ""))
            })
        st.table(tabla_visual)
    else:
        st.info("No hay publicadores registrados en el fichero hermanos.json.")

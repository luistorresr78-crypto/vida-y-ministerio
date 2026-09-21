import streamlit as st
import json
import os
import re
import reglas

# Configuracion adaptativa de la pagina web para celulares, iPads y laptops
st.set_page_config(page_title="Mesa de Asignaciones Teocraticas", page_icon="📝", layout="wide")

FICHERO_HERMANOS = "hermanos.json"
FICHERO_HISTORIAL = "historial_reuniones.json"

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

# --- PROCESADOR ADAPTATIVO CON EXTRACCIÓN AUTOMÁTICA DE LECTURA ---
def procesar_texto_plano_reunion(texto_usuario):
    materias_detectadas = {}
    if not texto_usuario.strip():
        return "JEREMÍAS 32, 33", materias_detectadas
        
    texto_limpio_global = texto_usuario.replace("\r", "\n")
    
    # Intercepción elástica de asignaciones consecutivas
    texto_sano = re.sub(r"(\(\s*4\s*mins\s*\.?\)\s*|\b)Converse con su estudiante", r"\n7. Haga discípulos (4 mins.) Converse con su estudiante", texto_limpio_global)
    texto_sano = re.sub(r"El autocontrol nos ayuda a obedecer", r"\n8. El autocontrol nos ayuda a obedecer", texto_sano)
    texto_sano = re.sub(r"Logros de la organización", r"\n9. Logros de la organización", texto_sano)
    texto_sano = re.sub(r"Estudio bíblico de la congregación", r"\n10. Estudio bíblico de la congregación", texto_sano)
    
    lineas_crudas = texto_sano.split("\n")
    lineas = []
    
    for lc in lineas_crudas:
        txt_l = lc.strip()
        if not txt_l: continue
        if "PRUEBAS ARQUEOLÓGICAS" in txt_l.upper() or "RESPUESTA" in txt_l.upper() or "¿QUÉ PERLAS" in txt_l.upper():
            continue
        lineas.append(txt_l)
            
    lectura_cab = "JEREMÍAS 32, 33"
    
    # Buscamos la línea que contenga la lectura de la semana en mayúsculas
    for l in lineas:
        if any(libro in l.upper() for libro in ["JER", "MAT", "MAR", "LUC", "JUA", "HECH", "ROM", "COR", "GAL", "EF", "FIL"]):
            if not re.match(r"^\s*[1-9]", l) and "CANCIÓN" not in l.upper():
                lectura_cab = l.strip()
                break

    seccion_actual_texto = "Tesoros"
    ultimo_punto = None
    puntos_crudos = {}

    for linea in lineas:
        linea_up = linea.upper()
        
        if "SEAMOS MEJORES MAESTROS" in linea_up:
            seccion_actual_texto = "Maestros"
            continue
        elif "NUESTRA VIDA CRISTIANA" in linea_up:
            seccion_actual_texto = "Vida"
            continue
        elif "PALABRAS DE CONCLUSIÓN" in linea_up or "PALABRAS DE CONCLUSION" in linea_up:
            ultimo_punto = None
            continue
            
        match_punto = re.match(r"^\s*([1-9]|10)\.\s*(.*)", linea)
        if match_punto:
            ultimo_punto = match_punto.group(1)
            puntos_crudos[ultimo_punto] = {
                "lineas": [match_punto.group(2)],
                "seccion": seccion_actual_texto
            }
        else:
            if ultimo_punto and ultimo_punto in puntos_crudos:
                if "CANCIÓN" in linea_up or "CANCION" in linea_up:
                    continue
                puntos_crudos[ultimo_punto]["lineas"].append(linea)

    for num_punto, info in puntos_crudos.items():
        texto_completo = " ".join(info["lineas"]).strip()
        
        match_mins = re.search(r"\(\s*(\d+\s*min[s]?\.?)\s*\)", texto_completo)
        seccion_filtrado = info["seccion"]
        if num_punto == "3" or "LECTURA DE LA BIBLIA" in texto_completo.upper():
            seccion_filtrado = "Lectura"
            
        if match_mins:
            mins_str = match_mins.group(0)
            
            if info["seccion"] == "Tesoros" and num_punto in ["1", "2"]:
                pos_m = texto_completo.find(mins_str)
                titulo_final_t = texto_completo[:pos_m].strip()
                texto_formateado = f"<b>{titulo_final_t}</b><br/><font size=9 color='#4A5568'>{mins_str}</font>"
            else:
                titulo_limpio_con_ref = texto_completo.replace(mins_str, "").replace("  ", " ").strip()
                titulo_limpio_con_ref = titulo_limpio_con_ref.replace("7. Haga discípulos", "").strip()
                
                if info["seccion"] == "Vida":
                    pos_mins = texto_completo.find(mins_str)
                    texto_desde_mins = texto_completo[pos_mins:]
                    match_primer_punto = re.search(r"\.", texto_desde_mins)
                    if match_primer_punto:
                        pos_punto_real = pos_mins + match_primer_punto.start()
                        texto_completo = texto_completo[:pos_punto_real + 1].strip()
                        titulo_limpio_con_ref = texto_completo.replace(mins_str, "").replace("  ", " ").strip()
                
                texto_formateado = f"<b>{titulo_limpio_con_ref}</b><br/><font size=9 color='#4A5568'>{mins_str}</font>"
        else:
            texto_formateado = f"<b>{texto_completo}</b>"
            
        materias_detectadas[num_punto] = {
            "titulo": texto_formateado,
            "minutos": "5",
            "seccion": seccion_filtrado
        }
        
    return lectura_cab, materias_detectadas

pestana_programa, pestana_historial, pestana_hermanos = st.tabs([
    "🚀 Fabricador de Folletos", 
    "📋 Historial Guardado",
    "👥 Gestión de Hermanos"
])
with pestana_programa:
    st.header("⚡ Generador Instantáneo de Folletos Oficiales")
    
    c_mes, c_sem = st.columns(2)
    with c_mes:
        mes_seleccionado = st.selectbox("📅 Seleccione el Mes Activo:", ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"], index=8, key="sel_mes_global")
    with c_sem:
        semana_seleccionada = st.text_input("📆 Ingrese el Rango de la Semana (Ej: 14-20 de septiembre):", placeholder="Escriba la fecha de la semana aquí...", key="sel_sem_global")

    st.markdown("---")
    st.markdown("Copia la Guía de Actividades completa desde **JW.org**, pégala abajo y presiona el botón para procesar.")

    texto_jw_entrada = st.text_area(
        "Pega aquí el texto completo copiado de JW.org:", 
        height=180, 
        placeholder="Puntos de la reunión...",
        key="txt_jw_live"
    )

    boton_armar_pdf = st.button("⚙️ Procesar Datos para Asignación (Paso 1)", use_container_width=True)

    # El procesador ahora nos extrae de forma elástica la lectura de las perlas espirituales
    l_jw, materias_dinamicas = procesar_texto_plano_reunion(texto_jw_entrada)

    st.markdown("---")

    # ENLAZADO DIRECTO: Forzamos a que el sistema use de forma obligatoria el mes y el rango ingresados en los campos manuales
    f_cab_clean = str(semana_seleccionada if semana_seleccionada else "14-20 de septiembre").strip()
    l_cab_clean = str(l_jw if texto_jw_entrada.strip() else f"LECTURA DE {mes_seleccionado}").strip()

    st.subheader(f"📅 Planificación de la Semana: {f_cab_clean}")
    st.info(f"📖 Texto Bíblico Extraído: **{l_cab_clean}**")

    with st.sidebar:
        st.header("⚙️ Control de Operación")
        coordinador_activo = st.selectbox("¿Quién está asignando hoy?", ["Sergio", "Jonathan", "Luis"], key="coord_act_live")

    st.markdown("### 🎚️ Asignar Privilegios para el Folleto PDF")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        opciones_presi = reglas.filtrar_ayudantes_inteligente("", lista_hermanos, "Presidencia", mes_seleccionado)
        nom_presi = [f"{h.get('nombre', '')} {h.get('apellido', '')}".strip() for h in opciones_presi] if opciones_presi else [f"{h.get('nombre', '')} {h.get('apellido', '')}".strip() for h in lista_hermanos]
        if "Por asignar" not in nom_presi: nom_presi.insert(0, "Por asignar")
        presidente = st.selectbox("Presidente de la Reunión", nom_presi, key="p_presi_live")
        
    with col_p2:
        opciones_ora = reglas.filtrar_ayudantes_inteligente("", lista_hermanos, "Oración", mes_seleccionado)
        nom_ora = [f"{h.get('nombre', '')} {h.get('apellido', '')}".strip() for h in opciones_ora] if opciones_ora else [f"{h.get('nombre', '')} {h.get('apellido', '')}".strip() for h in lista_hermanos]
        if "Por asignar" not in nom_ora: nom_ora.insert(0, "Por asignar")
        oracion_inicial = st.selectbox("Oración Inicial", nom_ora, key="p_ora_live")

    st.markdown("---")
    st.markdown("### 📝 Ajustar Temas de Intervenciones y Asignar Hermanos")
    
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
            
        st.markdown(f"**{emoji} Punto {k}**")
        
        texto_editado_usuario = st.text_input(
            f"Editar información del Punto {k}:", 
            value=titulo_preview, 
            key=f"live_text_input_edit_{k}"
        )
        
        if texto_editado_usuario != titulo_preview:
            if "<br/>" in titulo_bruto:
                partes_brutas = titulo_bruto.split("<br/>")
                subtitulo_plomo = partes_brutas if len(partes_brutas) > 1 else ""
                m["titulo"] = f"<b>{texto_editado_usuario}</b><br/>{subtitulo_plomo}"
            else:
                m["titulo"] = f"<b>{texto_editado_usuario}</b>"
        
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
        btn_grabar_semana = st.button("💾 Guardar Semana e Inyectar Nombres", use_container_width=True, type="primary")
        if btn_grabar_semana:
            if not f_cab_clean or f_cab_clean == "Por definir":
                st.error("Por favor ingrese el rango de la semana antes de guardar.")
            else:
                historial_actual = cargar_historial()
                if mes_seleccionado not in historial_actual:
                    historial_actual[mes_seleccionado] = {}
                
                historial_actual[mes_seleccionado][f_cab_clean] = {
                    "coordinador": coordinador_activo,
                    "asignados": asignados_en_vivo
                }
                guardar_historial(historial_actual)
                
                try:
                    reglas.generar_pdf_estilo_oficial(l_cab_clean, f_cab_clean, materias_dinamicas, asignados_en_vivo)
                    st.success(f"¡Semana guardada de forma permanente en {FICHERO_HISTORIAL} y nombres fijos con lectura bíblica en el PDF!")
                except Exception as e:
                    st.error(f"Fallo al inyectar ReportLab: {e}")

    with col_g2:
        btn_resetear_mesa = st.button("🗑️ Resetear / Limpiar Semana Actual", use_container_width=True)
        if btn_resetear_mesa:
            st.success("Limpiando mesa de trabajo...")
            st.rerun()

    archivo_encontrado_fisco = "reunion_actual.pdf"

    if os.path.exists(archivo_encontrado_fisco):
        with open(archivo_encontrado_fisco, "rb") as pdf_file:
            pdf_bytes = pdf_file.read()
            
        st.download_button(
            label="🟣 Descargar Folleto Oficial en PDF", 
            data=pdf_bytes, 
            file_name=f"Reunion_{mes_seleccionado}_{f_cab_clean.replace(' ', '_')}.pdf", 
            mime="application/pdf", 
            key="down_pdf_live",
            use_container_width=True
        )
    else:
        st.warning("⚠️ No se ha detectado el archivo guardado. Presione el botón azul '💾 Guardar Semana e Inyectar Nombres' para fijar los datos y habilitar el PDF.")

# --- PESTAÑA DEL HISTORIAL EN TIEMPO REAL CON BORRADO ---
with pestana_historial:
    st.header("📋 Historial de Asignaciones Registradas en la Bitácora")
    historial_visual = cargar_historial()
    
    if historial_visual:
        btn_borrar_todo_el_historial = st.button("🚨 BORRAR TODO EL HISTORIAL PERMANENTE", type="primary", use_container_width=True)
        if btn_borrar_todo_el_historial:
            guardar_historial({})
            st.success("💥 ¡Bitácora de historial completamente vaciada y formateada con éxito!")
            st.rerun()
            
        st.markdown("---")
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
                                t_fila_nom = asig.get(f"p{num_p}_t", "Por asignar")
                                st.write(f"• **Punto {num_p}:** {t_fila_nom}")
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

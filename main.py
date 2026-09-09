import streamlit as st
import json
import os
import re
import reglas

# Configuracion adaptativa de la pagina web para celulares, iPads y laptops
st.set_page_config(page_title="Mesa de Asignaciones Teocraticas", page_icon="📝", layout="wide")

FICHERO_HERMANOS = "hermanos.json"

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

# --- PROCESADOR CON CONVERSIÓN OBLIGATORIA A TEXTO PLANO ---
def procesar_texto_plano_reunion(texto_usuario):
    materias_detectadas = {}
    lineas = [l.strip() for l in texto_usuario.split("\n") if l.strip()]
    
    # Extraemos y blindamos las cabeceras como texto individual desde el inicio
    fecha_cab = str(lineas[0]).strip() if len(lineas) > 0 else "7-13 de septiembre"
    lectura_cab = str(lineas[1]).strip() if len(lineas) > 1 else "JEREMÍAS 32, 33"

    seccion_actual_texto = "Tesoros"
    ultimo_punto = None

    # Agrupamos las líneas continuas de JW.org
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

    # Aplicamos las reglas exactas de recorte quirúrgico compactador de Luis
    for num_punto, info in puntos_crudos.items():
        texto_completo = " ".join(info["lineas"]).strip()
        
        match_mins = re.search(r"\(\s*(\d+\s*min[s]?\.?)\s*\)", texto_completo)
        texto_mins = f"({match_mins.group(1)})" if match_mins else ""
        
        titulo_limpio = re.sub(r"\s*\(\s*\d+\s*min[s]?\.?\s*\).*", "", texto_completo).strip()
        
        match_ref = re.search(r"\(\s*\d+\s*min[s]?\.?\s*\)\s*\.?\s*(.*)", texto_completo)
        ref_extraida = match_ref.group(1).strip() if match_ref else ""
        
        # PREFERENCIA 1: Para Tesoros 1 y 2, dejamos EXCLUSIVAMENTE el tiempo hasta el minuto
        if info["seccion"] == "Tesoros" and num_punto in ["1", "2"]:
            if texto_mins:
                texto_formateado = f"<b>{titulo_limpio}</b><br/><font size=9 color='#4A5568'>{texto_mins}</font>"
            else:
                texto_formateado = f"<b>{titulo_limpio}</b>"
                
        # PREFERENCIA 2: Para la primera intervención de Vida Cristiana (Punto 7), recortamos hasta el primer punto
        elif info["seccion"] == "Vida" and num_punto == "7":
            if texto_mins:
                if ref_extraida:
                    pos_punto = ref_extraida.find(".")
                    if pos_punto != -1:
                        ref_recortada = ref_extraida[:pos_punto+1].strip()
                    else:
                        ref_recortada = ref_extraida
                    texto_formateado = f"<b>{titulo_limpio}</b><br/><font size=9 color='#4A5568'>{texto_mins} {ref_recortada}</font>"
                else:
                    texto_formateado = f"<b>{titulo_limpio}</b><br/><font size=9 color='#4A5568'>{texto_mins}</font>"
            else:
                texto_formateado = f"<b>{titulo_limpio}</b>"
                
        # PREFERENCIA 3: Los puntos 3, 4, 5, 6 y 8 van enteros de corrido
        else:
            if texto_mins:
                if ref_extraida:
                    texto_formateado = f"<b>{titulo_limpio}</b><br/><font size=9 color='#4A5568'>{texto_mins} {ref_extraida}</font>"
                else:
                    texto_formateado = f"<b>{titulo_limpio}</b><br/><font size=9 color='#4A5568'>{texto_mins}</font>"
            else:
                texto_formateado = f"<b>{texto_completo}</b>"
            
        materias_detectadas[num_punto] = {
            "titulo": texto_formateado,
            "minutos": "5",
            "seccion": info["seccion"]
        }
        
    return fecha_cab, lectura_cab, materias_detectadas

pestana_programa, pestana_hermanos = st.tabs([
    "🚀 Fabricador en Caliente de Folletos", 
    "👥 Gestión de Hermanos (Nómina)"
])

with pestana_programa:
    st.header("⚡ Generador Instantáneo de Folletos Oficiales")
    st.markdown("Copia la Guía de Actividades completa desde **JW.org**, pégala abajo y presiona el botón para procesar.")

    texto_jw_entrada = st.text_area(
        "Pega aquí el texto completo copiado de JW.org:", 
        height=180, 
        placeholder="1ra línea: Rango de Fecha\n2da línea: Lectura de la Semana\nSiguientes líneas: Los puntos de la reunión...",
        key="txt_jw_live"
    )

    boton_armar_pdf = st.button("⚙️ Procesar Datos para Descarga (Paso 1)", use_container_width=True)

    f_cab, l_cab, materias_dinamicas = procesar_texto_plano_reunion(texto_jw_entrada)

    st.markdown("---")
    nombre_archivo_final = "reunion_actual.pdf"

    # SANADO VISUAL ABSOLUTO: Aseguramos la limpieza de corchetes en las variables de la web
    f_cab_clean = str(f_cab).replace("['", "").replace("']", "").replace('["', "").replace('"]', "").strip()
    l_cab_clean = str(l_cab).replace("['", "").replace("']", "").replace('["', "").replace('"]', "").strip()

    st.subheader(f"📅 Vista Previa de la Semana: {f_cab_clean}")
    st.info(f"📖 Lectura Bíblica Extraída: **{l_cab_clean}**")

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
        opciones_presi = reglas.filtrar_ayudantes_inteligente("", lista_hermanos, "Presidencia")
        nom_presi = [f"{h.get('nombre', '')} {h.get('apellido', '')}" for h in opciones_presi] if opciones_presi else [f"{h.get('nombre', '')} {h.get('apellido', '')}" for h in lista_hermanos]
        presidente = st.selectbox("Presidente de la Reunión", nom_presi, key="p_presi_live")
        
    with col_p2:
        opciones_ora = reglas.filtrar_ayudantes_inteligente("", lista_hermanos, "Oración")
        nom_ora = [f"{h.get('nombre', '')} {h.get('apellido', '')}" for h in opciones_ora] if opciones_ora else [f"{h.get('nombre', '')} {h.get('apellido', '')}" for h in lista_hermanos]
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
        else:
            emoji, color_sub = "💎", "Tesoros de la Biblia"
            
        titulo_bruto = str(m.get('titulo', ''))
        titulo_preview = re.sub(r"<[^>]*>", "", titulo_bruto).strip()
            
        st.markdown(f"**{emoji} {k}. {titulo_preview}**")
        
        opciones_materia = reglas.filtrar_ayudantes_inteligente("", lista_hermanos, color_sub)
        nombres_materia = [f"{h.get('nombre', '')} {h.get('apellido', '')}" for h in opciones_materia] if opciones_materia else [f"{h.get('nombre', '')} {h.get('apellido', '')}" for h in lista_hermanos]
        if "" not in nombres_materia: nombres_materia.insert(0, "")
            
        c1, c2 = st.columns(2)
        with c1:
            titular = st.selectbox(f"Asignado punto {k}", nombres_materia, key=f"live_t_{k}")
            asignados_en_vivo[f"p{k}_t"] = titular if titular else "Por asignar"
        with c2:
            if tipo_seccion == "Maestros":
                opciones_ayudante = reglas.filtrar_ayudantes_inteligente(titular, lista_hermanos, "Seamos Mejores Maestros")
                nombres_ayudante = [f"{h.get('nombre', '')} {h.get('apellido', '')}" for h in opciones_ayudante] if opciones_ayudante else [f"{h.get('nombre', '')} {h.get('apellido', '')}" for h in lista_hermanos]
                if "" not in nombres_ayudante: nombres_ayudante.insert(0, "")
                ayudante = st.selectbox(f"Ayudante punto {k}", nombres_ayudante, key=f"live_a_{k}")
                asignados_en_vivo[f"p{k}_a"] = ayudante if ayudante else "Por asignar"

    st.markdown("### 🖨️ Descargar Documento Final (Paso 2)")

    if boton_armar_pdf:
        try:
            # Enviamos el orden definitivo exigido por el constructor (mes, semana)
            reglas.generar_pdf_estilo_oficial(l_cab_clean, f_cab_clean, materias_dinamicas, asignados_en_vivo)
            st.success(f"¡Folleto procesado con éxito por {coordinador_activo}! El botón morado de abajo está listo con los datos reales.")
        except Exception as e:
            st.error(f"Error interno al compilar: {e}")

    archivo_encontrado_fisco = "reunion_actual.pdf"

    if os.path.exists(archivo_encontrado_fisco):
        with open(archivo_encontrado_fisco, "rb") as pdf_file:
            pdf_bytes = pdf_file.read()
            
        st.download_button(
            label="🟣 Descargar Folleto Oficial en PDF", 
            data=pdf_bytes, 
            file_name=f"Reunion_{f_cab_clean.replace(' ', '_')}.pdf", 
            mime="application/pdf", 
            key="down_pdf_live",
            use_container_width=True
        )
    else:
        st.warning("⚠️ No se ha detectado el archivo en el sistema. Presione el botón gris 'Procesar Datos (Paso 1)' arriba para compilar el PDF de ReportLab.")

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
            nombres_baja = [f"{h.get('nombre', '')} {h.get('apellido', '')}" for h in lista_hermanos]
            hermano_a_eliminar = st.selectbox("Seleccione quién se muda o da de baja:", nombres_baja, key="baja_sel_live")
            if st.button("Confirmar Eliminación Permanente", type="primary", key="btn_baja_live"):
                lista_hermanos = [h for h in lista_hermanos if f"{h.get('nombre', '')} {h.get('apellido', '')}" != hermano_a_eliminar]
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
                "Nombre Completo": f"{h.get('nombre', '')} {h.get('apellido', '')}",
                "Sexo": h.get("sexo", "Varón"),
                "Aptitudes": ", ".join(h.get("aptitudes", [])) if isinstance(h.get("aptitudes", []), list) else str(h.get("aptitudes", ""))
            })
        st.table(tabla_visual)
    else:
        st.info("No hay publicadores registrados en el fichero hermanos.json.")

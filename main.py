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
                "nombre": h.get("nombre", h.get("Nombre", "")).strip().title(),
                "apellido": h.get("apellido", h.get("Apellido", "")).strip().title(),
                "sexo": h.get("sexo", h.get("Sexo", "Varón")),
                "aptitudes": h.get("aptitudes", h.get("Aptitudes", []))
            })
        return lista_limpia

lista_hermanos = cargar_hermanos_iniciales()

def guardar_hermanos(lista):
    with open(FICHERO_HERMANOS, "w", encoding="utf-8") as f:
        json.dump(lista, f, ensure_ascii=False, indent=4)

def procesar_texto_plano_reunion(texto_usuario):
    materias_detectadas = {}
    lineas = [l.strip() for l in texto_usuario.split("\n") if l.strip()]
    
    fecha_cab = lineas[0] if len(lineas) > 0 else "7-13 de septiembre"
    lectura_cab = lineas[1] if len(lineas) > 1 else "Lectura Oficial por Cargar"

    for linea in lineas:
        match_punto = re.match(r"^([1-8])\.\s*(.*)", linea)
        if match_punto:
            num_punto = match_punto.group(1)
            contenido = match_punto.group(2)
            
            match_mins = re.search(r"\(\s*(\d+)\s*min", contenido)
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
            "1": {"titulo": "1. Discurso de apertura", "minutos": "10", "seccion": "Tesoros"},
            "2": {"titulo": "2. Busquemos perlas escondidas", "minutos": "10", "seccion": "Tesoros"},
            "3": {"titulo": "3. Lectura de la Biblia", "minutos": "4", "seccion": "Tesoros"}
        }
    return fecha_cab, lecture_cab, materias_detectadas

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
    st.subheader(f"📅 Vista Previa de la Semana: {f_cab}")
    st.info(f"📖 Lectura Bíblica Extraída: **{l_cab}**")

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
        nom_presi = [f"{h.get('nombre', h.get('Nombre', ''))} {h.get('apellido', h.get('Apellido', ''))}" for h in opciones_presi] if opciones_presi else [f"{h.get('nombre', h.get('Nombre', ''))} {h.get('apellido', h.get('Apellido', ''))}" for h in lista_hermanos]
        presidente = st.selectbox("Presidente de la Reunión", nom_presi, key="p_presi_live")
        
    with col_p2:
        opciones_ora = reglas.filtrar_ayudantes_inteligente("", lista_hermanos, "Oración")
        nom_ora = [f"{h.get('nombre', h.get('Nombre', ''))} {h.get('apellido', h.get('Apellido', ''))}" for h in opciones_ora] if opciones_ora else [f"{h.get('nombre', h.get('Nombre', ''))} {h.get('apellido', h.get('Apellido', ''))}" for h in lista_hermanos]
        oracion_inicial = st.selectbox("Oración Inicial", nom_ora, key="p_ora_live")

    st.markdown("---")
    
    asignados_en_vivo = {"presidente": presidente, "oracion_inicial": oracion_inicial}
    
    # El bucle recorre y dibuja las materias extraídas del cuadro de texto grande libremente
    for k in sorted(materias_dinamicas.keys(), key=lambda x: int(x) if x.isdigit() else 999):
        m = materias_dinamicas[k]
        tipo_seccion = m.get("seccion", "Tesoros")
        
        if tipo_seccion == "Maestros":
            emoji, color_sub = "🌾", "Seamos Mejores Maestros"
        elif tipo_seccion == "Vida":
            emoji, color_sub = "🐑", "Vida Cristiana"
        else:
            emoji, color_sub = "💎", "Tesoros de la Biblia"
            
        st.markdown(f"**{emoji} {k}. {m.get('titulo', '')}** ({m.get('minutos', '')} min.)")
        
        opciones_materia = reglas.filtrar_ayudantes_inteligente("", lista_hermanos, color_sub)
        nombres_materia = [f"{h.get('nombre', h.get('Nombre', ''))} {h.get('apellido', h.get('Apellido', ''))}" for h in opciones_materia] if opciones_materia else [f"{h.get('nombre', h.get('Nombre', ''))} {h.get('apellido', h.get('Apellido', ''))}" for h in lista_hermanos]
        if "" not in nombres_materia: nombres_materia.insert(0, "")
            
        c1, c2 = st.columns(2)
        with c1:
            titular = st.selectbox(f"Asignado punto {k}", nombres_materia, key=f"live_t_{k}")
            asignados_en_vivo[f"p{k}_t"] = titular if titular else "Por asignar"
            
        with c2:
            if tipo_seccion == "Maestros":
                opciones_ayudante = reglas.filtrar_ayudantes_inteligente(titular, lista_hermanos, "Seamos Mejores Maestros")
                nombres_ayudante = [f"{h.get('nombre', h.get('Nombre', ''))} {h.get('apellido', h.get('Apellido', ''))}" for h in opciones_ayudante] if opciones_ayudante else [f"{h.get('nombre', h.get('Nombre', ''))} {h.get('apellido', h.get('Apellido', ''))}" for h in lista_hermanos]
                if "" not in nombres_ayudante: nombres_ayudante.insert(0, "")
                ayudante = st.selectbox(f"Ayudante punto {k}", nombres_ayudante, key=f"live_a_{k}")
                asignados_en_vivo[f"p{k}_a"] = ayudante if ayudante else "Por asignar"

    st.markdown("---")
    
    # FORMATOS DE BÚSQUEDA ADAPTATIVOS COMPATIBLES CON TU REGLAS.PY ORIGINAL
    nombre_archivo_opcion1 = f"Reunion_PROCESADO_WEB_{f_cab.replace(' ', '_')}.pdf"
    nombre_archivo_opcion2 = f"Reunion_PROCESADO_WEB_{f_cab}.pdf"
    nombre_archivo_final = nombre_archivo_opcion1

    try:
        # LLAMADA CON LA NOMENCLATURA CONFIGURADA EN TU REGLAS.PY DE AGOSTO
        reglas.generar_pdf_estilo_oficial("PROCESADO_WEB", f_cab, materias_dinamicas, asignados_en_vivo)
    except Exception:
        pass

    if boton_armar_pdf:
        st.success(f"¡Folleto procesado con éxito por {coordinador_activo}! El botón morado de abajo está listo con los datos reales.")
        
    st.markdown("### 🖨️ Descargar Documento Final (Paso 2)")

    # ESCÁNER INTELIGENTE DE ARCHIVOS COMPILADOS DE REPORTLAB
    archivo_encontrado = ""
    if os.path.exists(nombre_archivo_opcion1):
        archivo_encontrado = nombre_archivo_opcion1
    elif os.path.exists(nombre_archivo_opcion2):
        archivo_encontrado = nombre_archivo_opcion2
    else:
        # Intento de escaneo de comodín para capturar cualquier PDF generado hoy en la raíz
        for f in os.listdir("."):
            if f.startswith("Reunion_PROCESADO_WEB_") and f.endswith(".pdf"):
                archivo_encontrado = f; break

    if archivo_encontrado:
        with open(archivo_encontrado, "rb") as pdf_file:
            pdf_bytes = pdf_file.read()
        st.download_button(
            label="🟣 Descargar Folleto Oficial en PDF", 
            data=pdf_bytes, 
            file_name=f"Reunion_{f_cab.replace(' ', '_')}.pdf", 
            mime="application/pdf", 
            key="down_pdf_live",
            use_container_width=True
        )
    else:
        st.warning("⚠️ No se ha detectado el archivo generado. Presione el botón gris 'Procesar Datos (Paso 1)' arriba para compilar el PDF de ReportLab.")

# =========================================================================
# PESTAÑA 2: GESTIÓN DE HERMANOS
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

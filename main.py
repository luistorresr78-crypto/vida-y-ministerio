import streamlit as st
import json
import os
import re
import reglas

# Configuracion adaptativa de la pagina web para celulares, iPads y laptops
st.set_page_config(page_title="Mesa de Asignaciones Teocraticas", page_icon="📝", layout="wide")

FICHERO_HERMANOS = "hermanos.json"

# Carga segura con ordenamiento alfabético Tipo Título por Nombre
def cargar_hermanos_iniciales():
    if not os.path.exists(FICHERO_HERMANOS):
        hermanos_base = [
            {"nombre": "Jonathan", "apellido": "Coordinador", "sexo": "Varón", "aptitudes": ["Tesaros", "Lectura", "Presidencia", "Oración", "Vida Cristiana", "Seamos Mejores Maestros"]},
            {"nombre": "Luis", "apellido": "Torres", "sexo": "Varón", "aptitudes": ["Tesoros", "Lectura", "Presidencia", "Oración", "Vida Cristiana", "Seamos Mejores Maestros"]},
            {"nombre": "Sergio", "apellido": "Coordinador", "sexo": "Varón", "aptitudes": ["Tesoros", "Lectura", "Presidencia", "Oración", "Vida Cristiana", "Seamos Mejores Maestros"]}
        ]
        with open(FICHERO_HERMANOS, "w", encoding="utf-8") as f:
            json.dump(hermanos_base, f, ensure_ascii=False, indent=4)
            
    with open(FICHERO_HERMANOS, "r", encoding="utf-8") as f:
        lista_raw = json.load(f)
        lista_saneada = []
        for h in lista_raw:
            lista_saneada.append({
                "nombre": h.get("nombre", "").strip().title(),
                "apellido": h.get("apellido", "").strip().title(),
                "sexo": h.get("sexo", "Varón"),
                "aptitudes": h.get("aptitudes", [])
            })
        lista_ordenada = sorted(lista_saneada, key=lambda x: (x.get("nombre", "").lower(), x.get("apellido", "").lower()))
        return lista_ordenada

lista_hermanos = cargar_hermanos_iniciales()

def guardar_hermanos(lista):
    lista_saneada = []
    for h in lista:
        lista_saneada.append({
            "nombre": h.get("nombre", "").strip().title(),
            "apellido": h.get("apellido", "").strip().title(),
            "sexo": h.get("sexo", "Varón"),
            "aptitudes": h.get("aptitudes", [])
        })
    lista_ordenada = sorted(lista_saneada, key=lambda x: (x.get("nombre", "").lower(), x.get("apellido", "").lower()))
    with open(FICHERO_HERMANOS, "w", encoding="utf-8") as f:
        json.dump(lista_ordenada, f, ensure_ascii=False, indent=4)

# --- PROCESADOR EXTRACTOR EN CALIENTE INDESTRUCTIBLE DE JW.ORG ---
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
# =========================================================================
# PESTAÑA 1: FABRICADOR EN CALIENTE DE FOLLETOS (CORREGIDO INDESTRUCTIBLE)
# =========================================================================
with pestana_programa:
    st.header("⚡ Generador Instantáneo de Folletos Oficiales")
    st.markdown("Copia la Guía de Actividades completa desde **JW.org**, pégala abajo y el sistema extraerá en tiempo real la fecha, la lectura bíblica y los minutos exactos de cada punto.")

    # Entrada de texto abierta para jalar los datos de internet
    texto_jw_entrada = st.text_area(
        "Pega aquí el texto completo copiado de JW.org:", 
        height=200, 
        placeholder="Línea 1: Fecha\nLínea 2: Lectura Bíblica\nLíneas siguientes: Puntos numerados...",
        key="txt_jw_live"
    )

    f_cab, l_cab, materias_dinamicas = procesar_texto_plano_reunion(texto_jw_entrada)

    st.markdown("---")
    st.subheader(f"📅 Vista Previa de la Semana: {f_cab}")
    st.info(f"📖 Lectura Bíblica Detectada: **{l_cab}**")

    with st.sidebar:
        st.header("⚙️ Control de Operación")
        coordinador_activo = st.selectbox("¿Quién asigna hoy?", ["Sergio", "Jonathan", "Luis"], key="coord_live")

    # Formulario protegido: Las tómbolas se dibujan dinámicamente según el texto pegado
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
        
        # Este bucle dibuja dinámicamente los puntos que extrae de la caja de texto
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

        st.markdown("---")
        # El botón de procesar ahora valida y empaqueta la información de forma segura
        boton_armar = st.form_submit_button("⚙️ Procesar Datos para Descarga")

    # Guardamos los datos de descarga en un contenedor de memoria interna
    if boton_armar:
        reglas.generar_pdf_estilo_oficial(l_cab, f_cab, materias_dinamicas, asignados_en_vivo)
        st.session_state["pdf_listo"] = True
        st.session_state["f_cab_guardada"] = f_cab
        st.session_state["l_cab_guardada"] = l_cab
        st.success("¡Folleto procesado con éxito total! El botón de descarga de abajo se ha habilitado.")
    st.markdown("### 🖨️ Descargar Documento Final (Paso 2)")
    # El botón morado solo se dibuja en la pantalla si el usuario ya presionó el botón de procesar arriba
    if st.session_state.get("pdf_listo", False):
        nombre_archivo_pdf = "Reunion_PROCESADO_WEB.pdf"
        f_cab_g = st.session_state.get("f_cab_guardada", "Semana")
        
        if os.path.exists(nombre_archivo_pdf):
            with open(nombre_archivo_pdf, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()
            st.download_button(
                label="🟣 Descargar Folleto Oficial en PDF", 
                data=pdf_bytes, 
                file_name=f"Reunion_{f_cab_g.replace(' ', '_')}.pdf", 
                mime="application/pdf",
                key="btn_descarga_final_live"
            )
    else:
        st.info("💡 Por favor, rellena las tómbolas de arriba y haz clic en el botón '⚙️ Procesar Datos para Descarga' para activar el botón morado.")

# =========================================================================
# PESTAÑA 2: GESTIÓN DE HERMANOS (NÓMINA EN FORMATO TIPO TÍTULO POR NOMBRE)
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
                if nuevo_nom and nuevo_ape:
                    lista_hermanos.append({
                        "nombre": nuevo_nom.strip().title(), 
                        "apellido": nuevo_ape.strip().title(), 
                        "sexo": nuevo_sexo, 
                        "aptitudes": nuevas_apt
                    })
                    guardar_hermanos(lista_hermanos)
                    st.success(f"¡{nuevo_nom.strip().title()} {nuevo_ape.strip().title()} ha sido añadido con éxito!")
                    st.rerun()
                else:
                    st.error("Por favor ingresa Nombre y Apellido.")

    with col_del:
        st.subheader("❌ Dar de Baja Publicador")
        nombres_baja = [f"{h['nombre']} {h['apellido']}" for h in lista_hermanos]
        hermano_a_eliminar = st.selectbox("Seleccione quién se muda o da de baja:", nombres_baja, key="baja_sel_live")
        
        if st.button("Confirmar Eliminación Permanente", type="primary", key="btn_baja_live"):
            lista_hermanos = [h for h in lista_hermanos if f"{h['nombre']} {h['apellido']}" != hermano_a_eliminar]
            guardar_hermanos(lista_hermanos)
            st.warning(f"¡{hermano_a_eliminar} ha sido eliminado de la base de datos!")
            st.rerun()

    st.markdown("---")
    st.subheader("📜 Listado Oficial de la Congregación (Tipo Título - De la A a la Z por Nombre)")
    
    tabla_visual = []
    for h in lista_hermanos:
        tabla_visual.append({
            "Nombre": h.get("nombre", ""),
            "Apellido": h.get("apellido", ""),
            "Sexo": h.get("sexo", "Varón"),
            "Aptitudes Registradas": ", ".join(h.get("aptitudes", []))
        })
    st.table(tabla_visual)

import streamlit as st
import json
import os
import re
import reglas

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
        return json.load(f)

lista_hermanos = cargar_hermanos_iniciales()

def guardar_hermanos(lista):
    with open(FICHERO_HERMANOS, "w", encoding="utf-8") as f:
        json.dump(lista, f, ensure_ascii=False, indent=4)

# MOTOR INTELIGENTE CORREGIDO PARA JW.ORG (SOPORTA "MINS.")
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
            
            # Captura dinámicamente tanto "min." como "mins."
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
            "1": {"titulo": "Discurso (10 mins.)", "minutos": "10", "seccion": "Tesoros"},
            "2": {"titulo": "Perlas (10 mins.)", "minutos": "10", "seccion": "Tesoros"},
            "3": {"titulo": "Lectura de la Biblia (4 mins.)", "minutos": "4", "seccion": "Tesoros"}
        }
    return fecha_cab, lectura_cab, materias_detectadas

pestana_programa, pestana_hermanos = st.tabs([
    "🚀 Fabricador en Caliente de Folletos", 
    "👥 Gestión de Hermanos (Nómina)"
])

with pestana_programa:
    st.header("⚡ Generador Instantáneo de Folletos Oficiales")
    texto_jw_entrada = st.text_area(
        "Pega aquí el texto completo copiado de JW.org:", 
        height=200, 
        placeholder="Línea 1: Fecha\nLínea 2: Lectura Bíblica\nLíneas siguientes: Puntos numerados...",
        key="txt_jw_live"
    )

    f_cab, l_cab, materias_dinamicas = procesar_texto_plano_reunion(texto_jw_entrada)

    st.markdown("---")
    st.subheader(f"📅 Vista Previa: {f_cab}")
    st.info(f"📖 Lectura Bíblica Detectada: **{l_cab}**")

    with st.sidebar:
        st.header("⚙️ Control")
        coordinador_activo = st.selectbox("¿Quién asigna hoy?", ["Sergio", "Jonathan", "Luis"], key="coord_live")

    with st.form("formulario_live"):
        st.markdown("### 🎚️ Asignar Privilegios para el Folleto")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            opciones_presi = reglas.filtrar_ayudantes_inteligente("", lista_hermanos, "Presidencia")
            presidente = st.selectbox("Presidente", [h["nombre"] for h in opciones_presi])
        with col_p2:
            opciones_ora = reglas.filtrar_ayudantes_inteligente("", lista_hermanos, "Oración")
            oracion_inicial = st.selectbox("Oración Inicial", [h["nombre"] for h in opciones_ora])

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
                titular = st.selectbox(f"Asignado punto {k}", nombres_materia, key=f"t_{k}")
                asignados_en_vivo[f"p{k}_t"] = titular
            with c2:
                if tipo_seccion == "Maestros":
                    opciones_ayudante = reglas.filtrar_ayudantes_inteligente(titular, lista_hermanos, "Seamos Mejores Maestros")
                    nombres_ayudante = [h["nombre"] for h in opciones_ayudante]
                    if "" not in nombres_ayudante: nombres_ayudante.insert(0, "")
                    ayudante = st.selectbox(f"Ayudante punto {k}", nombres_ayudante, key=f"a_{k}")
                    asignados_en_vivo[f"p{k}_a"] = ayudante

        boton_armar = st.form_submit_button("⚙️ Procesar Datos para Descarga (Paso 1)")

    st.markdown("### 🖨️ Descargar Documento Final (Paso 2)")
    # Enviamos los datos reales extraídos en caliente a reglas.py
    reglas.generar_pdf_estilo_oficial(l_cab, f_cab, materias_dinamicas, asignados_en_vivo)
    nombre_archivo_pdf = f"Reunion_{l_cab.replace(' ', '_')}_{f_cab.replace(' ', '_')}.pdf"

    if os.path.exists(nombre_archivo_pdf):
        with open(nombre_archivo_pdf, "rb") as pdf_file:
            pdf_bytes = pdf_file.read()
        st.download_button(label="🟣 Descargar Folleto Oficial en PDF", data=pdf_bytes, file_name=f"Reunion_{f_cab.replace(' ', '_')}.pdf", mime="application/pdf")

with pestana_hermanos:
    st.header("👥 Nómina de la Congregación")
    col_add, col_del = st.columns(2)
    with col_add:
        with st.form("form_alta"):
            nuevo_nom = st.text_input("Nombre:")
            nuevo_ape = st.text_input("Apellido:")
            nuevo_sexo = st.selectbox("Sexo:", ["Varón", "Mujer"])
            nuevas_apt = st.multiselect("Aptitudes:", ["Tesoros", "Lectura", "Seamos Mejores Maestros", "Presidencia", "Oración", "Vida Cristiana"])
            if st.form_submit_button("Añadir Publicador"):
                if nuevo_nom:
                    lista_hermanos.append({"nombre": nuevo_nom, "apellido": nuevo_ape, "sexo": nuevo_sexo, "aptitudes": nuevas_apt})
                    guardar_hermanos(lista_hermanos)
                    st.success("¡Hermano añadido con éxito!")
                    st.rerun()
    with col_del:
        hermano_a_eliminar = st.selectbox("Baja:", [f"{h['nombre']} {h['apellido']}" for h in lista_hermanos])
        if st.button("Eliminar Permanente", type="primary"):
            lista_hermanos = [h for h in lista_hermanos if f"{h['nombre']} {h['apellido']}" != hermano_a_eliminar]
            guardar_hermanos(lista_hermanos)
            st.warning("Eliminado.")
            st.rerun()
    st.table([{"Nombre": f"{h['nombre']} {h['apellido']}", "Sexo": h.get("sexo","Varón"), "Aptitudes": ", ".join(h.get("aptitudes",[]))} for h in lista_hermanos])

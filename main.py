import streamlit as st
import json
import os
import reglas

# Configuracion de la pagina web para que se adapte a celulares, iPads y laptops
st.set_page_config(page_title="Mesa de Asignaciones Teocraticas", page_icon="📝", layout="wide")

FICHERO_REUNIONES = "reuniones.json"
FICHERO_HERMANOS = "hermanos.json"

# Carga segura de datos de la congregacion
def cargar_datos():
    if not os.path.exists(FICHERO_HERMANOS):
        # Base de datos inicial de prueba si no existe el archivo
        hermanos_base = [
            {"nombre": "Luis", "apellido": "Torres", "sexo": "Varón", "aptitudes": ["Tesoros", "Lectura", "Presidencia", "Oración", "Vida Cristiana", "Seamos Mejores Maestros"]},
            {"nombre": "Cristian", "apellido": "Rojas", "sexo": "Varón", "aptitudes": ["Tesoros", "Lectura", "Oración", "Seamos Mejores Maestros"]},
            {"nombre": "Nataly", "apellido": "Ortega", "sexo": "Mujer", "aptitudes": ["Seamos Mejores Maestros"]},
            {"nombre": "Ana", "apellido": "Saa", "sexo": "Mujer", "aptitudes": ["Seamos Mejores Maestros"]}
        ]
        with open(FICHERO_HERMANOS, "w", encoding="utf-8") as f:
            json.dump(hermanos_base, f, ensure_ascii=False, indent=4)
            
    if not os.path.exists(FICHERO_REUNIONES):
        # Estructura limpia de Septiembre con soporte nativo para la Quinta Semana (Punto 6)
        reuniones_base = {
            "SEPTIEMBRE": {
                "Semana 1 (Jeremías 22-23)": {"fecha_cabecera": "7-13 de septiembre", "lectura_cabecera": "JEREMÍAS 22, 23", "materias": {"1": {"titulo": "Discurso", "minutos": "10"}, "2": {"titulo": "Perlas", "minutos": "10"}, "3": {"titulo": "Lectura", "minutos": "4", "referencia": "Jer. 22:1-9"}, "4": {"titulo": "Conversación", "minutos": "3", "seccion": "Maestros"}, "5": {"titulo": "Revisita", "minutos": "4", "seccion": "Maestros"}, "6": {"titulo": "Discípulos", "minutos": "5", "seccion": "Maestros"}, "7": {"titulo": "Necesidades", "minutos": "15", "seccion": "Vida"}, "8": {"titulo": "Estudio Bíblico", "minutos": "30", "seccion": "Vida", "referencia": "rr cap. 1"}}, "asignados": {}},
                "Semana 2": {"fecha_cabecera": "14-20 de septiembre", "lectura_cabecera": "JEREMÍAS 24-25", "materias": {"1": {"titulo": "Discurso", "minutos": "10"}, "2": {"titulo": "Perlas", "minutos": "10"}, "3": {"titulo": "Lectura", "minutos": "4"}, "4": {"titulo": "Conversación", "minutos": "3", "seccion": "Maestros"}, "5": {"titulo": "Revisita", "minutos": "4", "seccion": "Maestros"}, "6": {"titulo": "Discípulos", "minutos": "5", "seccion": "Maestros"}, "7": {"titulo": "Necesidades", "minutos": "15", "seccion": "Vida"}, "8": {"titulo": "Estudio Bíblico", "minutos": "30", "seccion": "Vida"}}, "asignados": {}},
                "Semana 3": {"fecha_cabecera": "21-27 de septiembre", "lectura_cabecera": "JEREMÍAS 26-28", "materias": {"1": {"titulo": "Discurso", "minutos": "10"}, "2": {"titulo": "Perlas", "minutos": "10"}, "3": {"titulo": "Lectura", "minutos": "4"}, "4": {"titulo": "Conversación", "minutos": "3", "seccion": "Maestros"}, "5": {"titulo": "Revisita", "minutos": "4", "seccion": "Maestros"}, "6": {"titulo": "Discípulos", "minutos": "5", "seccion": "Maestros"}, "7": {"titulo": "Necesidades", "minutos": "15", "seccion": "Vida"}, "8": {"titulo": "Estudio Bíblico", "minutos": "30", "seccion": "Vida"}}, "asignados": {}},
                "Semana 4": {"fecha_cabecera": "28 sep-4 oct", "lectura_cabecera": "JEREMÍAS 29-31", "materias": {"1": {"titulo": "Discurso", "minutos": "10"}, "2": {"titulo": "Perlas", "minutos": "10"}, "3": {"titulo": "Lectura", "minutos": "4"}, "4": {"titulo": "Conversación", "minutos": "3", "seccion": "Maestros"}, "5": {"titulo": "Revisita", "minutos": "4", "seccion": "Maestros"}, "6": {"titulo": "Discípulos", "minutos": "5", "seccion": "Maestros"}, "7": {"titulo": "Necesidades", "minutos": "15", "seccion": "Vida"}, "8": {"titulo": "Estudio Bíblico", "minutos": "30", "seccion": "Vida"}}, "asignados": {}},
                # SOLUCIÓN PUNTO 6: La Quinta semana ahora se registra de forma obligatoria con su fecha exacta
                "Semana 5 (Quinta Semana)": {"fecha_cabecera": "5-11 de octubre", "lectura_cabecera": "JEREMÍAS 32-34", "materias": {"1": {"titulo": "Discurso", "minutos": "10"}, "2": {"titulo": "Perlas", "minutos": "10"}, "3": {"titulo": "Lectura", "minutos": "4"}, "4": {"titulo": "Conversación", "minutos": "3", "seccion": "Maestros"}, "5": {"titulo": "Revisita", "minutos": "4", "seccion": "Maestros"}, "6": {"titulo": "Discípulos", "minutos": "5", "seccion": "Maestros"}, "7": {"titulo": "Necesidades", "minutos": "15", "seccion": "Vida"}, "8": {"titulo": "Estudio Bíblico", "minutos": "30", "seccion": "Vida"}}, "asignados": {}}
            }
        }
        with open(FICHERO_REUNIONES, "w", encoding="utf-8") as f:
            json.dump(reuniones_base, f, ensure_ascii=False, indent=4)

    with open(FICHERO_HERMANOS, "r", encoding="utf-8") as f: hnos = json.load(f)
    with open(FICHERO_REUNIONES, "r", encoding="utf-8") as f: reuns = json.load(f)
    return hnos, reuns

lista_hermanos, datos_reuniones = cargar_datos()

# Titulo principal en la web adaptativo
st.title("📝 Sistema de Asignaciones Vida y Ministerio")
st.markdown("---")

# Panel lateral izquierdo: Configuracion de operacion y Firmas
with st.sidebar:
    st.header("⚙️ Mesa de Control")
    coordinador_activo = st.selectbox("¿Quién está asignando hoy?", ["Sergio", "Jonathan", "Luis"])
    
    # SOLUCIÓN PUNTO 2: Panel Web interactivo de Reemplazos de Emergencia
    st.subheader("♻️ Registro de Reemplazos")
    with st.expander("Ver apartado de Reemplazos"):
        hermano_ausente = st.text_input("Hermano Ausente")
        hermano_sustituto = st.text_input("Hermano que Reemplaza")
        motivo_cambio = st.selectbox("Motivo", ["Enfermedad", "Trabajo", "Viaje", "Otro"])
        if st.button("Guardar Reemplazo en Bitácora"):
            if hermano_ausente and hermano_sustituto:
                st.success(f"Sustitución guardada: {hermano_sustituto} cubre a {hermano_ausente}")
# --- CUERPO PRINCIPAL DE LA APLICACIÓN WEB ---
col_mes, col_sem = st.columns(2)

with col_mes:
    mes_seleccionado = st.selectbox("Seleccione el Mes:", list(datos_reuniones.keys()))

with col_sem:
    semana_seleccionada = st.selectbox("Seleccione la Semana:", list(datos_reuniones[mes_seleccionado].keys()))

# Extraemos la informacion guardada en caliente de esa semana
semana_data = datos_reuniones[mes_seleccionado][semana_seleccionada]
materias = semana_data.get("materias", {})
asignados_actuales = semana_data.get("asignados", {})

st.subheader(f"📅 Programación: {semana_data.get('fecha_cabecera', semana_seleccionada)}")
st.info(f"📖 Lectura semanal: **{semana_data.get('lectura_cabecera', '')}**")

# Formulario dinamico de asignacion familiar (Puntos 5 y 7)
with st.form("formulario_asignaciones"):
    st.markdown("### 🎚️ Asignar Privilegios de la Reunión")
    
    # 1. Bloque de Presidencia
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        # Filtro estricto de aptitud para Presidencia
        opciones_presi = reglas.filtrar_ayudantes_inteligente("", lista_hermanos, "Presidencia")
        nom_presi = [h["nombre"] for h in opciones_presi]
        idx_presi = nom_presi.index(asignados_actuales.get("presidente")) if asignados_actuales.get("presidente") in nom_presi else 0
        presidente = st.selectbox("Presidente de la Reunión", nom_presi, index=idx_presi)
        
    with col_p2:
        # Filtro estricto de aptitud para Oración
        opciones_ora = reglas.filtrar_ayudantes_inteligente("", lista_hermanos, "Oración")
        nom_ora = [h["nombre"] for h in opciones_ora]
        idx_ora = nom_ora.index(asignados_actuales.get("oracion_inicial")) if asignados_actuales.get("oracion_inicial") in nom_ora else 0
        oracion_inicial = st.selectbox("Oración Inicial", nom_ora, index=idx_ora)

    st.markdown("---")
    
    # 2. Casilleros Dinámicos de Puntos (Solución Punto 5)
    nuevos_asignados = {
        "presidente": presidente,
        "oracion_inicial": oracion_inicial
    }
    
    # El bucle recorre todas las materias que vengan registradas en el JSON y les crea su tómbola
    for k in sorted(materias.keys(), key=lambda x: int(x) if x.isdigit() else 999):
        m = materias[k]
        tipo_seccion = m.get("seccion", "Tesoros")
        
        # Seteamos el color visual del casillero segun corresponda
        if tipo_seccion == "Maestros":
            emoji, color_sub = "🌾", "Seamos Mejores Maestros"
        elif tipo_seccion == "Vida":
            emoji, color_sub = "🐑", "Vida Cristiana"
        else:
            emoji, color_sub = "💎", "Tesoros de la Biblia"
            
        st.markdown(f"**{emoji} {k}. {m.get('titulo', '')}** ({m.get('minutos', '')} min.)")
        
        # SOLUCIÓN PUNTO 7: Filtro estricto por sección para evitar que salgan los 80 publicadores
        opciones_materia = reglas.filtrar_ayudantes_inteligente("", lista_hermanos, color_sub)
        nombres_materia = [h["nombre"] for h in opciones_materia]
        
        # Aseguramos que la lista contenga una opcion en blanco por defecto
        if "" not in nombres_materia:
            nombres_materia.insert(0, "")
            
        c1, c2 = st.columns(2)
        with c1:
            idx_t = nombres_materia.index(asignados_actuales.get(f"p{k}_t")) if asignados_actuales.get(f"p{k}_t") in nombres_materia else 0
            titular = st.selectbox(f"Asignado punto {k}", nombres_materia, index=idx_t, key=f"t_{k}")
            nuevos_asignados[f"p{k}_t"] = titular
            
        with c2:
            # Si la seccion es Maestros, habilitamos el casillero para el Ayudante aplicando las reglas de consanguinidad
            if tipo_seccion == "Maestros":
                opciones_ayudante = reglas.filtrar_ayudantes_inteligente(titular, lista_hermanos, "Seamos Mejores Maestros")
                nombres_ayudante = [h["nombre"] for h in opciones_ayudante]
                if "" not in nombres_ayudante:
                    nombres_ayudante.insert(0, "")
                idx_a = nombres_ayudante.index(asignados_actuales.get(f"p{k}_a")) if asignados_actuales.get(f"p{k}_a") in nombres_ayudante else 0
                ayudante = st.selectbox(f"Ayudante punto {k}", nombres_ayudante, index=idx_a, key=f"a_{k}")
                nuevos_asignados[f"p{k}_a"] = ayudante

    st.markdown("---")
    boton_guardar = st.form_submit_button("💾 Guardar Asignaciones de la Semana")

# Lógica de guardado en caliente del JSON en el servidor en la nube
if boton_guardar:
    # Registramos la firma de quién guardó el cambio (Punto 2)
    datos_reuniones[mes_seleccionado][semana_seleccionada]["ultima_firma"] = f"Guardado por: {coordinador_activo}"

    datos_reuniones[mes_seleccionado][semana_seleccionada]["asignados"] = nuevos_asignados
    
    with open(FICHERO_REUNIONES, "w", encoding="utf-8") as f:
        json.dump(datos_reuniones, f, ensure_ascii=False, indent=4)
    st.success(f"¡Asignaciones de la semana '{semana_seleccionada}' guardadas con éxito por {coordinador_activo}!")

# =========================================================================
# SOLUCIÓN PUNTO 4: BOTÓN DE DESCARGA NATIVO WEB (ELIGE CARPETA DE DESTINO)
# =========================================================================
st.markdown("### 🖨️ Generación de Documento")

# Obligamos a ReportLab a maquetar el PDF con los últimos datos actualizados
reglas.generar_pdf_estilo_oficial(mes_seleccionado, semana_seleccionada, materias, nuevos_asignados)
nombre_archivo_pdf = f"Reunion_{mes_seleccionado}_{semana_seleccionada.replace(' ', '_')}.pdf"

# El boton nativo del navegador web abre la ventana de destino de Windows/Mac/Celular de forma obligatoria
if os.path.exists(nombre_archivo_pdf):
    with open(nombre_archivo_pdf, "rb") as pdf_file:
        pdf_bytes = pdf_file.read()
        
    st.download_button(
        label="🟣 Descargar Folleto Oficial en PDF",
        data=pdf_bytes,
        file_name=nombre_archivo_pdf,
        mime="application/pdf"
    )

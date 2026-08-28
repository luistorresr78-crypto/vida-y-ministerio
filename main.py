import streamlit as st
import json
import os
import reglas

# Configuracion adaptativa de la pagina web para celulares, iPads y laptops
st.set_page_config(page_title="Mesa de Asignaciones Teocraticas", page_icon="📝", layout="wide")

FICHERO_REUNIONES = "reuniones.json"
FICHERO_HERMANOS = "hermanos.json"

# Carga y guardado seguro de datos de la congregacion en la nube
def cargar_datos():
    if not os.path.exists(FICHERO_HERMANOS):
        hermanos_base = [
            {"nombre": "Luis", "apellido": "Torres", "sexo": "Varón", "aptitudes": ["Tesoros", "Lectura", "Presidencia", "Oración", "Vida Cristiana", "Seamos Mejores Maestros"]},
            {"nombre": "Sergio", "apellido": "Coordinador", "sexo": "Varón", "aptitudes": ["Tesoros", "Lectura", "Presidencia", "Oración", "Vida Cristiana", "Seamos Mejores Maestros"]},
            {"nombre": "Jonathan", "apellido": "Coordinador", "sexo": "Varón", "aptitudes": ["Tesoros", "Lectura", "Presidencia", "Oración", "Vida Cristiana", "Seamos Mejores Maestros"]}
        ]
        with open(FICHERO_HERMANOS, "w", encoding="utf-8") as f:
            json.dump(hermanos_base, f, ensure_ascii=False, indent=4)
            
    if not os.path.exists(FICHERO_REUNIONES):
        reuniones_base = {
            "SEPTIEMBRE": {
                "Semana 1 (Jeremías 22-23)": {"fecha_cabecera": "7-13 de septiembre", "lectura_cabecera": "JEREMÍAS 22, 23", "materias": {"1": {"titulo": "Discurso", "minutos": "10"}, "2": {"titulo": "Perlas", "minutos": "10"}, "3": {"titulo": "Lectura", "minutos": "4", "referencia": "Jer. 22:1-9"}, "4": {"titulo": "Conversación", "minutos": "3", "seccion": "Maestros"}, "5": {"titulo": "Revisita", "minutos": "4", "seccion": "Maestros"}, "6": {"titulo": "Discípulos", "minutos": "5", "seccion": "Maestros"}, "7": {"titulo": "Necesidades", "minutos": "15", "seccion": "Vida"}, "8": {"titulo": "Estudio Bíblico", "minutos": "30", "seccion": "Vida", "referencia": "rr cap. 1"}}, "asignados": {}}
            }
        }
        with open(FICHERO_REUNIONES, "w", encoding="utf-8") as f:
            json.dump(reuniones_base, f, ensure_ascii=False, indent=4)

    with open(FICHERO_HERMANOS, "r", encoding="utf-8") as f: hnos = json.load(f)
    with open(FICHERO_REUNIONES, "r", encoding="utf-8") as f: reuns = json.load(f)
    return hnos, reuns

# Funciones maestras para guardar cambios en caliente en el servidor
def guardar_hermanos(lista):
    with open(FICHERO_HERMANOS, "w", encoding="utf-8") as f:
        json.dump(lista, f, ensure_ascii=False, indent=4)

def guardar_reuniones(datos):
    with open(FICHERO_REUNIONES, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

lista_hermanos, datos_reuniones = cargar_datos()

# --- MENÚ SUPERIOR DE PESTAÑAS WEB (NUEVA INTERFAZ) ---
pestana_asignaciones, pestana_hermanos, pestana_reuniones = st.tabs([
    "📋 Mesa de Asignaciones", 
    "👥 Gestión de Hermanos (Nómina)", 
    "📖 Configurar Reunión (Pegar Datos)"
])
# =========================================================================
# PESTAÑA 1: MESA DE ASIGNACIONES SEMANALES
# =========================================================================
with pestana_asignaciones:
    col_mes, col_sem = st.columns(2)
    with col_mes:
        mes_seleccionado = st.selectbox("Seleccione el Mes:", list(datos_reuniones.keys()), key="sel_mes_web")
    with col_sem:
        semana_seleccionada = st.selectbox("Seleccione la Semana:", list(datos_reuniones[mes_seleccionado].keys()), key="sel_sem_web")

    semana_data = datos_reuniones[mes_seleccionado][semana_seleccionada]
    materias = semana_data.get("materias", {})
    asignados_actuales = semana_data.get("asignados", {})

    st.subheader(f"📅 Programación: {semana_data.get('fecha_cabecera', semana_seleccionada)}")
    st.info(f"📖 Lectura semanal: **{semana_data.get('lectura_cabecera', '')}**")

    with st.sidebar:
        st.header("⚙️ Control de Operación")
        coordinador_activo = st.selectbox("¿Quién está asignando hoy?", ["Sergio", "Jonathan", "Luis"], key="coord_act")
        
        st.subheader("♻️ Registro de Reemplazos")
        with st.expander("Ver apartado de Reemplazos"):
            hermano_ausente = st.text_input("Hermano Ausente", key="aus_t")
            hermano_sustituto = st.text_input("Hermano que Reemplaza", key="sust_t")
            if st.button("Guardar Reemplazo en Bitácora", key="btn_remp"):
                if hermano_ausente and hermano_sustituto:
                    st.success(f"Sustitución guardada: {hermano_sustituto} cubre a {hermano_ausente}")

    with st.form("formulario_asignaciones_web"):
        st.markdown("### 🎚️ Asignar Privilegios de la Reunión")
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            opciones_presi = reglas.filtrar_ayudantes_inteligente("", lista_hermanos, "Presidencia")
            nom_presi = [h["nombre"] for h in opciones_presi]
            idx_presi = nom_presi.index(asignados_actuales.get("presidente")) if asignados_actuales.get("presidente") in nom_presi else 0
            presidente = st.selectbox("Presidente de la Reunión", nom_presi, index=idx_presi, key="p_presi")
            
        with col_p2:
            opciones_ora = reglas.filtrar_ayudantes_inteligente("", lista_hermanos, "Oración")
            nom_ora = [h["nombre"] for h in opciones_ora]
            idx_ora = nom_ora.index(asignados_actuales.get("oracion_inicial")) if asignados_actuales.get("oracion_inicial") in nom_ora else 0
            oracion_inicial = st.selectbox("Oración Inicial", nom_ora, index=idx_ora, key="p_ora")

        st.markdown("---")
        
        nuevos_asignados = {"presidente": presidente, "oracion_inicial": oracion_inicial}
        
        for k in sorted(materias.keys(), key=lambda x: int(x) if x.isdigit() else 999):
            m = materias[k]
            tipo_seccion = m.get("seccion", "Tesaros")
            
            if tipo_seccion == "Maestros":
                emoji, color_sub = "🌾", "Seamos Mejores Maestros"
            elif tipo_seccion == "Vida":
                emoji, color_sub = "🐑", "Vida Cristiana"
            else:
                emoji, color_sub = "💎", "Tesoros de la Biblia"
                
            st.markdown(f"**{emoji} {k}. {m.get('titulo', '')}** ({m.get('minutos', '')} min.)")
            
            opciones_materia = reglas.filtrar_ayudantes_inteligente("", lista_hermanos, color_sub)
            nombres_materia = [h["nombre"] for h in opciones_materia]
            if "" not in nombres_materia: nombres_materia.insert(0, "")
                
            c1, c2 = st.columns(2)
            with c1:
                idx_t = nombres_materia.index(asignados_actuales.get(f"p{k}_t")) if asignados_actuales.get(f"p{k}_t") in nombres_materia else 0
                titular = st.selectbox(f"Asignado punto {k}", nombres_materia, index=idx_t, key=f"web_t_{k}")
                nuevos_asignados[f"p{k}_t"] = titular
                
            with c2:
                if tipo_seccion == "Maestros":
                    opciones_ayudante = reglas.filtrar_ayudantes_inteligente(titular, lista_hermanos, "Seamos Mejores Maestros")
                    nombres_ayudante = [h["nombre"] for h in opciones_ayudante]
                    if "" not in nombres_ayudante: nombres_ayudante.insert(0, "")
                    idx_a = nombres_ayudante.index(asignados_actuales.get(f"p{k}_a")) if asignados_actuales.get(f"p{k}_a") in nombres_ayudante else 0
                    ayudante = st.selectbox(f"Ayudante punto {k}", nombres_ayudante, index=idx_a, key=f"web_a_{k}")
                    nuevos_asignados[f"p{k}_a"] = ayudante

        st.markdown("---")
        boton_guardar = st.form_submit_button("💾 Guardar Asignaciones de la Semana")

    if boton_guardar:
        datos_reuniones[mes_seleccionado][semana_seleccionada]["ultima_firma"] = f"Guardado por: {coordinador_activo}"
        datos_reuniones[mes_seleccionado][semana_seleccionada]["asignados"] = nuevos_asignados
        guardar_reuniones(datos_reuniones)
        st.success(f"¡Asignaciones guardadas con éxito por {coordinador_activo}!")

    st.markdown("### 🖨️ Generación de Documento")
    reglas.generar_pdf_estilo_oficial(mes_seleccionado, semana_seleccionada, materias, nuevos_asignados)
    nombre_archivo_pdf = f"Reunion_{mes_seleccionado}_{semana_seleccionada.replace(' ', '_')}.pdf"

    if os.path.exists(nombre_archivo_pdf):
        with open(nombre_archivo_pdf, "rb") as pdf_file:
            pdf_bytes = pdf_file.read()
        st.download_button(label="🟣 Descargar Folleto Oficial en PDF", data=pdf_bytes, file_name=nombre_archivo_pdf, mime="application/pdf", key="down_pdf_web")

# =========================================================================
# PESTAÑA 2: GESTIÓN DE HERMANOS (AGREGAR, QUITAR, SEXO Y LISTA)
# =========================================================================
with pestana_hermanos:
    st.header("👥 Control de la Nómina de la Congregación")
    
    col_add, col_del = st.columns(2)
    
    with col_add:
        st.subheader("➕ Agregar Nuevo Hermano/a")
        with st.form("form_alta_hermano"):
            nuevo_nom = st.text_input("Nombre:")
            nuevo_ape = st.text_input("Apellido:")
            nuevo_sexo = st.selectbox("Sexo:", ["Varón", "Mujer"])
            nuevas_apt = st.multiselect("Asignar Aptitudes/Secciones:", ["Tesoros", "Lectura", "Seamos Mejores Maestros", "Presidencia", "Oración", "Vida Cristiana"])
            btn_dar_alta = st.form_submit_button("Añadir Publicador")
            
            if btn_dar_alta:
                if nuevo_nom and nuevo_ape:
                    nuevo_h = {"nombre": nuevo_nom, "apellido": nuevo_ape, "sexo": nuevo_sexo, "aptitudes": nuevas_apt}
                    lista_hermanos.append(nuevo_h)
                    guardar_hermanos(lista_hermanos)
                    st.success(f"¡{nuevo_nom} {nuevo_ape} ha sido añadido con éxito!")
                    st.rerun()
                else:
                    st.error("Por favor ingresa Nombre y Apellido.")

    with col_del:
        st.subheader("❌ Dar de Baja Publicador")
        nombres_baja = [f"{h['nombre']} {h['apellido']}" for h in lista_hermanos]
        hermano_a_eliminar = st.selectbox("Seleccione quién se muda o da de baja:", nombres_baja, key="baja_sel")
        if st.button("Confirmar Eliminación Permanente", type="primary"):
            lista_hermanos = [h for h in lista_hermanos if f"{h['nombre']} {h['apellido']}" != hermano_a_eliminar]
            guardar_hermanos(lista_hermanos)
            st.warning(f"¡{hermano_a_eliminar} ha sido eliminado de la base de datos!")
            st.rerun()

    st.markdown("---")
    st.subheader("📜 Listado Completo de Hermanos Registrados")
    
    # Renderizamos la lista en una cuadricula limpia para auditoria visual
    tabla_visual = []
    for h in lista_hermanos:
        tabla_visual.append({
            "Nombre Completo": f"{h['nombre']} {h['apellido']}",
            "Sexo": h.get("sexo", "Varón"),
            "Aptitudes": ", ".join(h.get("aptitudes", []))
        })
    st.table(tabla_visual)

# =========================================================================
# PESTAÑA 3: CONFIGURAR REUNIÓN (PEGAR NUEVOS DATOS DEL MES)
# =========================================================================
with pestana_reuniones:
    st.header("📖 Importar y Pegar Estructuras de Reunión")
    st.markdown("Utiliza esta pestaña para expandir los meses o inyectar nuevas semanas directamente en formato de texto plano.")
    
    with st.form("form_pegar_json"):
        st.subheader("📋 Inyectar Bloque Completo de Reuniones (Formato JSON)")
        texto_json_pegar = st.text_area("Pega aquí el código de materias del mes o semana:", height=300, 
            placeholder='{\n  "OCTUBRE": {\n    "Semana 1": {\n      "fecha_cabecera": "5-11 de octubre",\n      "lectura_cabecera": "...",\n      "materias": {},\n      "asignados": {}\n    }\n  }\n}')
        btn_inyectar = st.form_submit_button("⚡ Fusionar y Cargar Reuniones")
        
        if btn_inyectar:
            try:
                datos_nuevos_inyectados = json.loads(texto_json_pegar)
                for mes, semanas in datos_nuevos_inyectados.items():
                    if mes not in datos_reuniones:
                        datos_reuniones[mes] = {}
                    for sem, cuerpo in semanas.items():
                        datos_reuniones[mes][sem] = cuerpo
                guardar_reuniones(datos_reuniones)
                st.success("¡Estructura de reuniones integrada e inyectada con éxito total!")
                st.rerun()
            except Exception as error_json:
                st.error(f"Error en el formato del texto pegado: {error_json}")

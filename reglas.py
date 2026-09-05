import json
import os
import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors

FICHERO_REUNIONES = "reuniones.json"
FICHERO_HERMANOS = "hermanos.json"

def obtener_nombre_coordinador():
    return "Luis"

def limpiar_nombre_asignado(nombre_crudo):
    """Función auxiliar para limpiar nombres con formatos complejos como 
    'Nombre -> [Firma]' o 'Nombre (⚠️ REPETIDO)' evitando caídas por tipos de datos."""
    if not nombre_crudo or not isinstance(nombre_crudo, str):
        return ""
    # Remueve texto sobrante dividiendo de forma segura en formato de cadena
    if "->" in nombre_crudo:
        nombre_crudo = nombre_crudo.split("->")[0]
    if "(" in nombre_crudo:
        nombre_crudo = nombre_crudo.split("(")[0]
    return nombre_crudo.strip()

def calcular_participaciones_mes(mes_activo):
    conteo = {}
    if not os.path.exists(FICHERO_REUNIONES): 
        return conteo
    try:
        with open(FICHERO_REUNIONES, "r", encoding="utf-8") as f:
            datos = json.load(f)
        semanas_mes = datos.get(mes_activo, {})
        for semana in semanas_mes.values():
            for hermano in semana.get("asignados", {}).values():
                if hermano and isinstance(hermano, str):
                    nombre_limpio = limpiar_nombre_asignado(hermano)
                    if nombre_limpio:
                        conteo[nombre_limpio] = conteo.get(nombre_limpio, 0) + 1
    except Exception as e:
        print(f"Error al calcular participaciones del mes: {e}")
    return conteo

def filtrar_ayudantes_inteligente(hermano_titular, lista_hermanos, aptitud_filtro, mes_activo="SEPTIEMBRE"):
    mapeo_aptitudes = {
        "Tesoros": "Tesoros", "Lectura": "Lectura",
        "Seamos Mejores Maestros": "Seamos Mejores Maestros",
        "Presidencia": "Presidencia", "Oración": "Oración",
        "Vida Cristiana": "Vida Cristiana"
    }
    aptit_f = aptitud_filtro.replace("Tesoros de la Biblia", "Tesoros").replace("Vida Cristiana", "Vida Cristiana")
    aptitud_real = mapeo_aptitudes.get(aptit_f, aptit_f)
    
    historial_mes = calcular_participaciones_mes(mes_activo)
    candidatos = []
    
    if not hermano_titular:
        for h in lista_hermanos:
            apts_h = [str(a).lower() for a in h.get("aptitudes", [])] if isinstance(h.get("aptitudes", []), list) else str(h.get("aptitudes", "")).lower()
            if aptitud_real.lower() in apts_h or ("maestros" in aptitud_real.lower() and "maestros" in str(apts_h)):
                candidatos.append(h)
    else:
        titular_limpio = limpiar_nombre_asignado(hermano_titular)
        sexo_tit = "Varón"
        apellido_tit = titular_limpio.split(" ")[-1] if " " in titular_limpio else ""
        for h in lista_hermanos:
            if f"{h.get('nombre', '')} {h.get('apellido', '')}" == titular_limpio:
                sexo_tit = h.get("sexo", "Varón")
        
        for h in lista_hermanos:
            nombre_h = f"{h.get('nombre', '')} {h.get('apellido', '')}"
            if nombre_h == titular_limpio: 
                continue
            
            apts_h = [str(a).lower() for a in h.get("aptitudes", [])] if isinstance(h.get("aptitudes", []), list) else str(h.get("aptitudes", "")).lower()
            if "seamos mejores maestros" in apts_h or "maestros" in str(apts_h):
                if sexo_tit == "Mujer" and h.get("sexo") == "Mujer":
                    candidatos.append(h)
                elif sexo_tit == "Varón":
                    if h.get("sexo") == "Varón" or (h.get("sexo") == "Mujer" and h.get("apellido", "").lower() == apellido_tit.lower()):
                        candidatos.append(h)
                        
    lista_ordenada = []
    for h in candidatos:
        nombre_h = f"{h.get('nombre', '')} {h.get('apellido', '')}"
        v = historial_mes.get(nombre_h, 0)
        etiqueta = nombre_h if v == 0 else (f"{nombre_h} (1 asignación)" if v == 1 else f"{nombre_h} (⚠️ REPETIDO x{v})")
        lista_ordenada.append({"h": h, "etiqueta": etiqueta, "v": v})
        
    lista_ordenada.sort(key=lambda x: x["v"])
    
    hermanos_listos = []
    for idx, item in enumerate(lista_ordenada):
        h_copia = dict(item["h"])
        h_copia["nombre"] = f"{item['etiqueta']} -> [Firma]" if idx == 0 else item["etiqueta"]
        h_copia["apellido"] = ""
        hermanos_listos.append(h_copia)
        
    return hermanos_listos
# =========================================================================
# PARTE 2: GENERACIÓN DE REPORTE PDF (ESTILO OFICIAL COMPACTO)
# =========================================================================

def generar_pdf_estilo_oficial(mes_activo, semana_act, materias, asignados):
    nombre_pdf = "reunion_actual.pdf"
    
    # Configuración de página optimizada con márgenes reducidos
    doc = SimpleDocTemplate(
        nombre_pdf, pagesize=letter,
        rightMargin=24, leftMargin=24, topMargin=24, bottomMargin=24
    )
    
    # --- Paleta de Colores y Estilos Tipográficos Oficiales ---
    est_fecha = ParagraphStyle('EF', fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor("#2D3748"))
    est_lectura = ParagraphStyle('EL', fontName='Helvetica-Bold', fontSize=11, textColor=colors.HexColor("#1A365D"))
    est_letra_blank = ParagraphStyle('ELB', fontName='Helvetica-Bold', fontSize=10, textColor=colors.white, alignment=0)
    
    # Títulos de materias según sección oficial
    est_t_tesoros = ParagraphStyle('ETT', fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor("#026A7A"), leading=13)
    est_t_maestros = ParagraphStyle('ETM', fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor("#A16B00"), leading=13)
    est_t_vida = ParagraphStyle('ETV', fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor("#991B1B"), leading=13)
    
    # Formato cursiva/negrita para los nombres asignados (igual que la imagen)
    est_hnos = ParagraphStyle('TH', fontName='Helvetica-BoldOblique', fontSize=9, textColor=colors.HexColor("#1A202C"), alignment=1)
    est_cab_tit = ParagraphStyle('ECT', fontName='Helvetica', fontSize=10, textColor=colors.HexColor("#4A5568"))

    elementos = []
    
    # --- 1. CABECERA PRINCIPAL ---
    texto_fecha = str(semana_act).strip("['\"]")
    texto_lectura = str(mes_activo).strip("['\"]")
    
    cab_izq = [
        Paragraph(f"<b>{texto_fecha}</b>", est_fecha),
        Paragraph(f"<b>{texto_lectura}</b>", est_lectura)
    ]
    
    presi = asignados.get("presidente") or ""
    # Caja interna para el recuadro gris del presidente
    t_presi_box = Table([[Paragraph(f"{presi}", est_hnos)]], colWidths=[160], rowHeights=[18])
    t_presi_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F0F4F8")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))

    cab_der = [[Paragraph("<b>Presidente</b>", est_cab_tit), t_presi_box]]
    t_presi = Table(cab_der, colWidths=[90, 160])
    t_presi.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    
    t_principal = Table([[cab_izq, t_presi]], colWidths=[290, 250])
    t_principal.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10)
    ]))
    elementos.append(t_principal)
    
    # --- 2. FILA HORIZONTAL: CANCIÓN DE INICIO ---
    ora_ini = asignados.get("oracion_inicial") or ""
    t_ora_box = Table([[Paragraph(f"{ora_ini}", est_hnos)]], colWidths=[125], rowHeights=[18])
    t_ora_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F0F4F8")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))

    datos_cancion_1 = [
        Paragraph("♫ <b>Canción 161</b> y oración", est_cab_tit),
        Paragraph("<b>Palabras de Introducción</b>", est_cab_tit),
        t_ora_box
    ]
    t_c1 = Table([datos_cancion_1], colWidths=[290, 125, 125])
    t_c1.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,-1), 1, colors.HexColor("#2D3748")),
        ('LINEBELOW', (0,0), (-1,-1), 1, colors.HexColor("#2D3748")),
        ('PADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    elementos.append(t_c1)
    elementos.append(Spacer(1, 10))
    
    # --- CONFIGURACIÓN DE SECCIONES INTELIGENTES ---
    secciones_mapeadas = {
        "Tesoros": {"titulo": "  TESOROS DE LA BIBLIA", "color": "#3A7885", "estilo_t": est_t_tesoros},
        "Maestros": {"titulo": "  SEAMOS MEJORES MAESTROS", "color": "#D08F00", "estilo_t": est_t_maestros},
        "Vida": {"titulo": "  NUESTRA VIDA CRISTIANA", "color": "#B32415", "estilo_t": est_t_vida}
    }
    
    seccion_actual = ""
    
    # --- 3. BUCLE DE INTERPRETACIÓN DE MATERIAS ---
    for k in sorted(materias.keys(), key=lambda x: int(x) if x.isdigit() else 999):
        m = materias[k]
        sec_materia = m.get("seccion", "Tesoros")
        
        if sec_materia != seccion_actual:
            seccion_actual = sec_materia
            conf = secciones_mapeadas.get(seccion_actual, secciones_mapeadas["Tesoros"])
            
            # Canción intermedia antes de la sección Vida Cristiana
            if seccion_actual == "Vida":
                datos_cancion_2 = [Paragraph("♫ <b>Canción 121</b>", est_cab_tit), Paragraph("", est_hnos), Paragraph("", est_hnos)]
                t_c2 = Table([datos_cancion_2], colWidths=[290, 125, 125])
                t_c2.setStyle(TableStyle([
                    ('LINEABOVE', (0,0), (-1,-1), 1, colors.HexColor("#718096")),
                    ('LINEBELOW', (0,0), (-1,-1), 1, colors.HexColor("#718096")),
                    ('PADDING', (0,0), (-1,-1), 4)
                ]))
                elementos.append(t_c2)
                elementos.append(Spacer(1, 8))
                
            # Barra horizontal de la sección a color completo
            t_tit = Table([[Paragraph(f"<b>{conf['titulo']}</b>", est_letra_blank)]], colWidths=[540], rowHeights=[20])
            t_tit.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(conf["color"])),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4)
            ]))
            t_tit.hAlign = 'LEFT'
            elementos.append(t_tit)
            elementos.append(Spacer(1, 6))
            
        titular = asignados.get(f"p{k}_t") or ""
        ayudante = asignados.get(f"p{k}_a") or ""
        
        # Limpieza de textos largos o descripciones secundarias
        texto_original = m.get('titulo', '')
        texto_limpio = texto_original.replace(" — ", "<br/><font size=8.5 color='#4A5568'>").replace(" —", "<br/><font size=8.5 color='#4A5568'")
        if "<br/>" in texto_limpio:
            texto_limpio += "</font>"
            
        conf_sec = secciones_mapeadas.get(seccion_actual, secciones_mapeadas["Tesoros"])
        
        # Contenedor dinámico con fondo suave para el titular de la asignación
        t_titular_box = ""
        if titular:
            t_titular_box = Table([[Paragraph(f"{titular}", est_hnos)]], colWidths=[125], rowHeights=[18])
            t_titular_box.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EBF8FA" if seccion_actual == "Tesoros" else ("#FFFDF5" if seccion_actual == "Maestros" else "#FFF5F5"))),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ]))

        # Contenedor dinámico con fondo suave para el ayudante (Estudiantes)
        t_ayudante_box = ""
        if ayudante:
            t_ayudante_box = Table([[Paragraph(f"{ayudante}", est_hnos)]], colWidths=[125], rowHeights=[18])
            t_ayudante_box.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFFDF5")),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ]))

        # Maquetación alineada de 3 columnas
        fila_materia = [
            Paragraph(f"{k}. {texto_limpio}", conf_sec["estilo_t"]),
            t_titular_box,
            t_ayudante_box
        ]
        
        t_fila = Table([fila_materia], colWidths=[290, 125, 125])
        t_fila.setStyle(TableStyle([
            ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
            ('PADDING', (0,0), (-1,-1), 5),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (1,0), (-1,-1), 'CENTER')
        ]))
        t_fila.hAlign = 'LEFT'
        elementos.append(t_fila)
        elementos.append(Spacer(1, 4))
        
    # --- 4. CIERRE INFERIOR DE LA REUNIÓN ---
    elementos.append(Spacer(1, 6))
    datos_conclusion = [
        Paragraph("<b>Palabras de conclusión (3 mins.)</b>", est_cab_tit),
        Paragraph("♫ <b>Canción 28</b> y oración", est_cab_tit),
        Paragraph("", est_hnos)
    ]
    t_c_fin = Table([datos_conclusion], colWidths=[290, 125, 125])
    t_c_fin.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,-1), 1, colors.HexColor("#2D3748")),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    elementos.append(t_c_fin)
    
    # Compilación final del documento
    doc.build(elementos)
    
    # Duplicación opcional para servidor web/espejo local
    nombre_espejo = f"Reunion_PROCESADO_WEB_{texto_fecha.replace(' ', '_')}.pdf"
    try:
        with open(nombre_pdf, "rb") as f_orig, open(nombre_espejo, "wb") as f_dest:
            f_dest.write(f_orig.read())
    except: 
        pass

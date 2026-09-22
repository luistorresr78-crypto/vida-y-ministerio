import json
import os
import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors

FICHERO_REUNIONES = "reuniones.json"
FICHERO_HERMANOS = "hermanos.json"

def calcular_participaciones_mes(mes_activo):
    conteo = {}
    if not os.path.exists(FICHERO_REUNIONES): return conteo
    try:
        with open(FICHERO_REUNIONES, "r", encoding="utf-8") as f:
            datos = json.load(f)
        semanas_mes = datos.get(mes_activo, {})
        for semana in semanas_mes.values():
            for hermano in semana.get("asignados", {}).values():
                if hermano and isinstance(hermano, str) and hermano != "Por asignar":
                    conteo[hermano] = conteo.get(hermano, 0) + 1
    except: pass
    return conteo

def filtrar_ayudantes_inteligente(hermano_titular, lista_hermanos, aptitud_filtro, mes_detectado="SEPTIEMBRE"):
    historial_mes = calcular_participaciones_mes(mes_detectado)
    aptitud_real = str(aptitud_filtro).strip()
    
    candidatos = []
    if not hermano_titular:
        for h in lista_hermanos:
            apts_h = [str(a).lower().strip() for a in h.get("aptitudes", [])]
            if aptitud_real.lower() in apts_h:
                candidatos.append(h)
    else:
        titular_limpio = hermano_titular.strip()
        sexo_tit = "Varón"
        apellido_tit = titular_limpio.split(" ")[-1] if " " in titular_limpio else ""
        for h in lista_hermanos:
            if f"{h.get('nombre', '')} {h.get('apellido', '')}" == titular_limpio:
                sexo_tit = h.get("sexo", "Varón")
        
        for h in lista_hermanos:
            nombre_h = f"{h.get('nombre', '')} {h.get('apellido', '')}"
            if nombre_h == titular_limpio: continue
            
            apts_h = [str(a).lower().strip() for a in h.get("aptitudes", [])]
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
        lista_ordenada.append({"h": h, "v": v, "nombre_original": nombre_h})
        
    lista_ordenada.sort(key=lambda x: x["v"])
    
    hermanos_listos = []
    for item in lista_ordenada:
        h_copia = dict(item["h"])
        h_copia["nombre"] = item["nombre_original"]
        h_copia["apellido"] = ""
        hermanos_listos.append(h_copia)
        
    return hermanos_listos
def generar_pdf_estilo_oficial(mes_activo, semana_act, materias, asignados):
    nombre_pdf = "reunion_actual.pdf"
    
    doc = SimpleDocTemplate(
        nombre_pdf, pagesize=letter,
        rightMargin=24, leftMargin=24, topMargin=24, bottomMargin=24
    )
    
    # --- Paleta y Estilos Tipográficos Oficiales ---
    est_fecha = ParagraphStyle('EF', fontName='Helvetica-Bold', fontSize=12, leading=14, textColor=colors.HexColor("#2D3748"))
    est_lectura = ParagraphStyle('EL', fontName='Helvetica-Bold', fontSize=11, leading=13, textColor=colors.HexColor("#1A365D"))
    est_letra_blank = ParagraphStyle('ELB', fontName='Helvetica-Bold', fontSize=10, textColor=colors.white, alignment=0)
    
    est_t_tesoros = ParagraphStyle('ETT', fontName='Helvetica', fontSize=10, textColor=colors.HexColor("#3A7885"), leading=12)
    est_t_maestros = ParagraphStyle('ETM', fontName='Helvetica', fontSize=10, textColor=colors.HexColor("#D08F00"), leading=12)
    est_t_vida = ParagraphStyle('ETV', fontName='Helvetica', fontSize=10, textColor=colors.HexColor("#B32415"), leading=12)
    
    est_hnos = ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=9, textColor=colors.HexColor("#2D3748"))
    est_cab_tit = ParagraphStyle('ECT', fontName='Helvetica', fontSize=9, textColor=colors.HexColor("#4A5568"))

    elementos = []
    
    # --- 1. CABECERA PRINCIPAL ---
    texto_fecha = str(semana_act).replace("['", "").replace("']", "").replace('["', "").replace('"]', "").strip()
    texto_lectura = str(mes_activo).replace("['", "").replace("']", "").replace('["', "").replace('"]', "").strip()
    
    cab_izq = [
        Paragraph(f"<b>{texto_fecha}</b>", est_fecha),
        Paragraph(f"<b>{texto_lectura}</b>", est_lectura)
    ]
    
    presi = str(asignados.get("presidente", "Por asignar")).strip()
    cab_der = [[Paragraph("Presidente", est_cab_tit), Paragraph(f"{presi}", est_hnos)]]
    t_presi = Table(cab_der, colWidths=[100, 120])
    t_presi.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LINEBELOW', (1,0), (1,0), 0.75, colors.HexColor("#4A5568")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2)
    ]))
    
    t_principal = Table([[cab_izq, t_presi]], colWidths=[320, 220])
    t_principal.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6)
    ]))
    elementos.append(t_principal)
    
    # --- 2. FILA HORIZONTAL: CANCIÓN DE INICIO DINÁMICA ---
    ora_ini = str(asignados.get("oracion_inicial", "Por asignar")).strip()
    c_ini = str(asignados.get("c_apertura", "1")).strip()
    datos_cancion_1 = [
        Paragraph(f"■ <b>Canción {c_ini}</b> y oración", est_cab_tit),
        Paragraph("", est_cab_tit),
        Paragraph(f"{ora_ini}", est_hnos)
    ]
    t_c1 = Table([datos_cancion_1], colWidths=[320, 110, 110])
    t_c1.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,-1), 1, colors.HexColor("#1A365D")),
        ('LINEBELOW', (0,0), (-1,-1), 1, colors.HexColor("#1A365D")),
        ('PADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    elementos.append(t_c1)
    elementos.append(Spacer(1, 6))

    secciones_mapeadas = {
        "Tesoros": {"titulo": "TESOROS DE LA BIBLIA", "color": "#3A7885", "estilo_t": est_t_tesoros},
        "Maestros": {"titulo": "SEAMOS MEJORES MAESTROS", "color": "#D08F00", "estilo_t": est_t_maestros},
        "Vida": {"titulo": "NUESTRA VIDA CRISTIANA", "color": "#B32415", "estilo_t": est_t_vida}
    }
    
    seccion_actual = ""
    
    # --- 3. BUCLE PRINCIPAL ---
    for k in sorted(materias.keys(), key=lambda x: int(x) if x.isdigit() else 999):
        m = materias[k]
        sec_materia = m.get("seccion", "Tesoros")
        
        if sec_materia == "Lectura":
            sec_materia = "Tesoros"
        
        if sec_materia != seccion_actual:
            seccion_actual = sec_materia
            conf = secciones_mapeadas.get(seccion_actual, secciones_mapeadas["Tesoros"])
            
            t_tit = Table([[Paragraph(f"<b>{conf['titulo']}</b>", est_letra_blank)]], colWidths=[540])
            t_tit.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(conf["color"])),
                ('PADDING', (0,0), (-1,-1), 5),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6)
            ]))
            t_tit.hAlign = 'LEFT'
            elementos.append(t_tit)
            elementos.append(Spacer(1, 4))
            
            # Inyección de la Canción intermedia dinámica
            if seccion_actual == "Vida":
                c_int = str(asignados.get("c_intermedia", "121")).strip()
                datos_cancion_2 = [Paragraph(f"■ <b>Canción {c_int}</b>", est_cab_tit), Paragraph("", est_hnos), Paragraph("", est_hnos)]
                t_c2 = Table([datos_cancion_2], colWidths=[320, 110, 110])
                t_c2.setStyle(TableStyle([
                    ('LINEABOVE', (0,0), (-1,-1), 0.5, colors.HexColor("#718096")),
                    ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#718096")),
                    ('PADDING', (0,0), (-1,-1), 4),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
                ]))
                elementos.append(t_c2)
                elementos.append(Spacer(1, 8))
            else:
                elementos.append(Spacer(1, 4))
        
        titular = str(asignados.get(f"p{k}_t", "Por asignar")).strip()
        ayudante = str(asignados.get(f"p{k}_a", "")).strip()
        
        if titular == "None": titular = "Por asignar"
        if ayudante == "None" or ayudante == "Por asignar": ayudante = ""
        
        texto_html_final = str(m.get('titulo', ''))
        if not texto_html_final.startswith(f"{k}."):
            texto_html_final = f"{k}. {texto_html_final}"
        
        conf_sec = secciones_mapeadas.get(sec_materia, secciones_mapeadas["Tesoros"])
        
        fila_materia = [
            Paragraph(texto_html_final, conf_sec["estilo_t"]),
            Paragraph(f"{titular}", est_hnos),
            Paragraph(f"{ayudante}", est_hnos)
        ]
        
        t_fila = Table([fila_materia], colWidths=[320, 110, 110])
        t_fila.setStyle(TableStyle([
            ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
            ('PADDING', (0,0), (-1,-1), 6),
            ('VALIGN', (0,0), (-1,-1), 'TOP')
        ]))
        t_fila.hAlign = 'LEFT'
        elementos.append(t_fila)
        elementos.append(Spacer(1, 4))
        
    # --- 4. CIERRE INFERIOR CON CANCIÓN FINAL DINÁMICA ---
    elementos.append(Spacer(1, 4))
    c_fin = str(asignados.get("c_conclusion", "28")).strip()
    datos_conclusion = [
        Paragraph("Palabras de conclusión (3 mins.)", est_cab_tit),
        Paragraph(f"■ <b>Canción {c_fin}</b> y oración", est_cab_tit),
        Paragraph("", est_hnos)
    ]
    t_c_fin = Table([datos_conclusion], colWidths=[320, 110, 110])
    t_c_fin.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,-1), 1, colors.HexColor("#1A365D")),
        ('LINEBELOW', (0,0), (-1,-1), 1, colors.HexColor("#1A365D")),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    elementos.append(t_c_fin)
    
    doc.build(elementos)

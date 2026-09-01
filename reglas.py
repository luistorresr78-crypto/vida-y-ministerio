from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
import os

FICHERO_HERMANOS = "hermanos.json"

def filtrar_ayudantes_inteligente(hermano_titular, lista_hermanos, aptitud_filtro):
    filtro_real = "Tesoros" if "Tesoros" in aptitud_filtro else aptitud_filtro
    candidatos = [h for h in lista_hermanos if filtro_real in h.get("aptitudes", [])]
    
    if hermano_titular and aptitud_filtro == "Seamos Mejores Maestros":
        titular_limpio = hermano_titular.strip()
        sexo_tit = next((h["sexo"] for h in lista_hermanos if f"{h['nombre']} {h['apellido']}" == titular_limpio), "Varón")
        apellido_tit = titular_limpio.split(" ")[-1] if " " in titular_limpio else ""

        candidatos_validos = []
        for h in candidatos:
            nombre_h = f"{h['nombre']} {h['apellido']}"
            if nombre_h == titular_limpio: continue
            if sexo_tit == "Mujer" and h["sexo"] == "Mujer": candidatos_validos.append(h)
            elif sexo_tit == "Varón":
                if h["sexo"] == "Varón" or (h["sexo"] == "Mujer" and h["apellido"].lower() == apellido_tit.lower()):
                    candidatos_validos.append(h)
        candidatos = candidatos_validos

    lista_listas = []
    for h in candidatos:
        lista_listas.append({"nombre": f"{h['nombre']} {h['apellido']}"})
    return lista_listas

def generar_pdf_estilo_oficial(lectura_cabecera, fecha_cabecera, materias, asignados):
    # Forzamos un nombre único y limpio compatible con la descarga directa
    nombre_pdf = "Reunion_PROCESADO_WEB.pdf"
    doc = SimpleDocTemplate(nombre_pdf, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=45, bottomMargin=45)
    
    est_fecha = ParagraphStyle('EF', fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor("#4A5568"))
    est_lectura = ParagraphStyle('EL', fontName='Helvetica-Bold', fontSize=11, textColor=colors.HexColor("#1A365D"))
    est_letra_blanca = ParagraphStyle('ELB', fontName='Helvetica-Bold', fontSize=10, textColor=colors.white, alignment=0)
    
    est_blu = ParagraphStyle('TB', fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor("#3A7885"))
    est_ora = ParagraphStyle('TO', fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor("#D08F00"))
    est_red = ParagraphStyle('TR', fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor("#B32415"))
    
    est_hnos = ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor("#2D3748"))
    est_cab_tit = ParagraphStyle('ECT', fontName='Helvetica', fontSize=10, textColor=colors.HexColor("#4A5568"))
    
    elementos = []
    
    cab_izq = [
        Paragraph(f"{fecha_cabecera}", est_fecha),
        Paragraph(f"{lectura_cabecera}", est_lectura)
    ]
    
    presi = asignados.get("presidente") or "Por asignar"
    cab_der = [[Paragraph("<b>Presidente</b>", est_cab_tit), Paragraph(f"{presi}", est_hnos)]]
    t_presi = Table(cab_der, colWidths=[90, 160])
    t_presi.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('LINEBELOW', (1,0), (1,0), 0.5, colors.black)]))
    
    t_principal = Table([[cab_izq, t_presi]], colWidths=[290, 250])
    t_principal.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    elementos.append(t_principal)
    elementos.append(Spacer(1, 15))
    
    ora_ini = asignados.get("oracion_inicial") or "Por asignar"
    datos_cancion_1 = [
        [Paragraph("🎵 <b>Canción 40</b> y oración", est_cab_tit), Paragraph("<b>Palabras de Introducción</b>", est_cab_tit), Paragraph(f"{ora_ini}", est_hnos)]
    ]
    t_c1 = Table(datos_cancion_1, colWidths=[180, 180, 180])
    t_c1.setStyle(TableStyle([('LINEABOVE', (0,0), (-1,-1), 1, colors.black), ('LINEBELOW', (0,0), (-1,-1), 1, colors.black), ('PADDING', (0,0), (-1,-1), 6), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    elementos.append(t_c1)
    elementos.append(Spacer(1, 20))
    
    # === SECCIÓN 1: TESOROS DE LA BIBLIA ===
    t_tit_tesoros = Table([[Paragraph("<b>TESOROS DE LA BIBLIA</b>", est_letra_blanca)]], colWidths=[540])
    t_tit_tesoros.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#3A7885")), ('PADDING', (0,0), (-1,-1), 6)]))
    t_tit_tesoros.hAlign = 'LEFT'
    elementos.append(t_tit_tesoros)
    elementos.append(Spacer(1, 10))
    
    filas_t = []
    for k in sorted(materias.keys(), key=lambda x: int(x) if x.isdigit() else 999):
        if k in ["1", "2", "3"]:
            m = materias[k]
            txt_punto = f"<b>{k}. {m.get('titulo','')}</b>"
            titular = asignados.get(f"p{k}_t") or ""
            filas_t.append([Paragraph(txt_punto, est_blu), Paragraph(titular, est_hnos), ""])
    if filas_t:
        t_filas_t = Table(filas_t, colWidths=[340, 200, 0])
        t_filas_t.setStyle(TableStyle([('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")), ('PADDING', (0,0), (-1,-1), 10), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
        elementos.append(t_filas_t)
    elementos.append(Spacer(1, 25))
    
    # === SECCIÓN 2: SEAMOS MEJORES MAESTROS ===
    t_tit_maestros = Table([[Paragraph("<b>SEAMOS MEJORES MAESTROS</b>", est_letra_blanca)]], colWidths=[540])
    t_tit_maestros.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#D08F00")), ('PADDING', (0,0), (-1,-1), 6)]))
    t_tit_maestros.hAlign = 'LEFT'
    elementos.append(t_tit_maestros)
    elementos.append(Spacer(1, 10))
    
    filas_m = []
    for k in sorted(materias.keys(), key=lambda x: int(x) if x.isdigit() else 999):
        if m_obj := materias.get(k):
            if k in ["4", "5", "6", "7"] and m_obj.get("seccion") == "Maestros":
                txt_punto = f"<b>{k}. {m_obj.get('titulo','')}</b>"
                titular = asignados.get(f"p{k}_t") or ""
                ayudante = asignados.get(f"p{k}_a") or ""
                filas_m.append([Paragraph(txt_punto, est_ora), Paragraph(titular, est_hnos), Paragraph(ayudante, est_hnos)])
    if filas_m:
        t_filas_m = Table(filas_m, colWidths=[340, 100, 100])
        t_filas_m.setStyle(TableStyle([('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")), ('PADDING', (0,0), (-1,-1), 10), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
        elementos.append(t_filas_m)
    elementos.append(Spacer(1, 25))
    
    # === SECCIÓN 3: NUESTRA VIDA CRISTIANA ===
    t_tit_vida = Table([[Paragraph("<b>NUESTRA VIDA CRISTIANA</b>", est_letra_blanca)]], colWidths=[540])
    t_tit_vida.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#B32415")), ('PADDING', (0,0), (-1,-1), 6)]))
    t_tit_vida.hAlign = 'LEFT'
    elementos.append(t_tit_vida)
    elementos.append(Spacer(1, 10))
    
    t_c2 = Table([[Paragraph("🎵 <b>Canción 103</b>", est_cab_tit)]], colWidths=[540])
    t_c2.setStyle(TableStyle([('LINEBELOW', (0,0), (-1,-1), 0.5, colors.black), ('PADDING', (0,0), (-1,-1), 6)]))
    elementos.append(t_c2)
    
    filas_v = []
    for k in sorted(materias.keys(), key=lambda x: int(x) if x.isdigit() else 999):
        if m_obj := materias.get(k):
            if k.isdigit() and int(k) >= 7 and m_obj.get("seccion") == "Vida":
                txt_punto = f"<b>{k}. {m_obj.get('titulo','')}</b>"
                titular = asignados.get(f"p{k}_t") or ""
                filas_v.append([Paragraph(txt_punto, est_red), Paragraph(titular, est_hnos), ""])
    if filas_v:
        t_filas_v = Table(filas_v, colWidths=[340, 200, 0])
        t_filas_v.setStyle(TableStyle([('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")), ('PADDING', (0,0), (-1,-1), 10), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
        elementos.append(t_filas_v)
    elementos.append(Spacer(1, 20))
    
    t_c3 = Table([[Paragraph("Palabras de conclusión (3 mins.)", est_cab_tit), Paragraph("🎵 <b>Canción 60</b> y oración", est_cab_tit), Paragraph("", est_hnos)]], colWidths=[180, 180, 180])
    t_c3.setStyle(TableStyle([('LINEABOVE', (0,0), (-1,-1), 1, colors.black), ('LINEBELOW', (0,0), (-1,-1), 1, colors.black), ('PADDING', (0,0), (-1,-1), 6), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    elementos.append(t_c3)
    
    doc.build(elementos)

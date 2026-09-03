import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def filtrar_ayudantes_inteligente(hermano_titular, lista_hermanos, aptitud_filtro):
    # Función de compatibilidad local idéntica al 28 de agosto
    candidatos = []
    for h in lista_hermanos:
        apts = [str(a).lower() for a in h.get("aptitudes", [])]
        if aptit_filtro := aptitud_filtro.lower():
            if "tesoros" in aptit_filtro and "tesoros" in apts: candidatos.append(h)
            elif "maestros" in aptit_filtro and "seamos mejores maestros" in apts: candidatos.append(h)
            elif "vida" in aptit_filtro and "vida cristiana" in apts: candidatos.append(h)
            elif "presidencia" in aptit_filtro and "presidencia" in apts: candidatos.append(h)
            elif "oración" in aptit_filtro and "oración" in apts: candidatos.append(h)
    return candidatos

def generar_pdf_estilo_oficial(modo, fecha_semana, materias, asignados):
    # Forzamos por sistema un nombre plano controlado e indestructible en la raíz
    nombre_pdf = "reunion_actual.pdf"
    
    # Configuramos el lienzo de ReportLab en tamaño Carta (Letter)
    doc = SimpleDocTemplate(
        nombre_pdf, 
        pagesize=letter,
        rightMargin=36, leftMargin=36, 
        topMargin=36, bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    # Definición de la paleta teocrática limpia original de agosto
    estilo_titulo = ParagraphStyle(
        'EstiloTitulo', parent=styles['Heading1'],
        fontName='Helvetica-Bold', fontSize=16, textColor=colors.HexColor('#1A365D'),
        alignment=1, spaceAfter=8
    )
    
    estilo_sub = ParagraphStyle(
        'EstiloSub', parent=styles['Normal'],
        fontName='Helvetica', fontSize=11, textColor=colors.HexColor('#4A5568'),
        alignment=1, spaceAfter=15
    )
    
    estilo_texto = ParagraphStyle(
        'EstiloTexto', parent=styles['Normal'],
        fontName='Helvetica', fontSize=10, textColor=colors.black,
        leading=13
    )

    story = []
    
    # 1. Título y Rango de Fecha oficial
    story.append(Paragraph(f"<b>PROGRAMA DE LA REUNIÓN</b>", estilo_titulo))
    story.append(Paragraph(f"📅 Semana: {str(fecha_semana).strip()}", estilo_sub))
    story.append(Spacer(1, 10))
    
    # 2. Mesa Principal de introducción
    presi_nom = asignados.get("presidente", "Por asignar")
    ora_nom = asignados.get("oracion_inicial", "Por asignar")
    
    tabla_intro_data = [
        [Paragraph(f"<b>Presidente:</b> {presi_nom}", estilo_texto), 
         Paragraph(f"<b>Oración Inicial:</b> {ora_nom}", estilo_texto)]
    ]
    t_intro = Table(tabla_intro_data, colWidths=[270, 270])
    t_intro.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EDF2F7')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LINEBELOW', (0,0), (-1,-1), 1.5, colors.HexColor('#CBD5E0')),
    ]))
    story.append(t_intro)
    story.append(Spacer(1, 15))
    
    # 3. Dibujo de la Cuadrícula Oficial del Programa
    tabla_programa_data = [[
        Paragraph("<b>Punto de la Reunión / Materia</b>", estilo_texto), 
        Paragraph("<b>Asignado (Titular / Ayudante)</b>", estilo_texto)
    ]]
    
    for k in sorted(materias.keys(), key=lambda x: int(x) if x.isdigit() else 999):
        m = materias[k]
        tipo_sec = m.get("seccion", "Tesoros")
        
        # Color del riel según la sección teocrática exacta de agosto
        color_fila = '#EBF8FF' if tipo_sec == "Tesoros" else ('#F0FFF4' if tipo_sec == "Maestros" else '#FFFAF0')
        
        titular_punto = asignados.get(f"p{k}_t", "Por asignar")
        ayudante_punto = asignados.get(f"p{k}_a", "")
        
        nombre_completo_asignado = f"{titular_punto}"
        if ayudante_punto and ayudante_punto != "Por asignar":
            nombre_completo_asignado += f" / <b>Ayudante:</b> {ayudante_punto}"
            
        tabla_programa_data.append([
            Paragraph(f"<b>{k}.</b> {m.get('titulo', '')} ({m.get('minutos', '')} min.)", estilo_texto),
            Paragraph(nombre_completo_asignado, estilo_texto)
        ])
    
    # Construcción visual de la tabla final
    t_prog = Table(tabla_programa_data, colWidths=[330, 210])
    estilos_tabla = [
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2B6CB0')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('PADDING', (0,0), (-1,-1), 6),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
    ]
    
    # Coloreamos las filas una a una en base a su sección original de agosto
    for i in range(1, len(tabla_programa_data)):
        k_key = sorted(materias.keys(), key=lambda x: int(x) if x.isdigit() else 999)[i-1]
        tipo_s = materias[k_key].get("seccion", "Tesoros")
        c_bg = '#EBF8FF' if tipo_s == "Tesoros" else ('#F0FFF4' if tipo_s == "Maestros" else '#FFFAF0')
        estilos_tabla.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor(c_bg)))
        
    t_prog.setStyle(TableStyle(estilos_tabla))
    story.append(t_prog)
    
    # 4. Compilación física del documento en el disco duro
    doc.build(story)
    
    # Duplicamos el archivo con el nombre redundante tradicional por si main.py lo busca allí
    nombre_tradicional = f"Reunion_PROCESADO_WEB_{str(fecha_semana).replace(' ', '_')}.pdf"
    try:
        with open(nombre_pdf, "rb") as f_origen, open(nombre_tradicional, "wb") as f_destino:
            f_destino.write(f_origen.read())
    except Exception:
        pass

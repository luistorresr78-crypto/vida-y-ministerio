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

def calcular_participaciones_mes(mes_activo):
    conteo = {}
    if not os.path.exists(FICHERO_REUNIONES): return conteo
    try:
        with open(FICHERO_REUNIONES, "r", encoding="utf-8") as f:
            datos = json.load(f)
        semanas_mes = datos.get(mes_activo, {})
        for semana in semanas_mes.values():
            for hermano in semana.get("asignados", {}).values():
                if hermano and isinstance(hermano, str):
                    nombre_limpio = hermano.split(" ->")[0].split("(")[0].strip()
                    conteo[nombre_limpio] = conteo.get(nombre_limpio, 0) + 1
    except: pass
    return conteo

def filtrar_ayudantes_inteligente(hermano_titular, lista_hermanos, aptitud_filtro):
    mapeo_aptitudes = {
        "Tesoros": "Tesoros", "Lectura": "Lectura",
        "Seamos Mejores Maestros": "Seamos Mejores Maestros",
        "Presidencia": "Presidencia", "Oración": "Oración",
        "Vida Cristiana": "Vida Cristiana"
    }
    aptit_f = aptitud_filtro.replace("Tesoros de la Biblia", "Tesoros").replace("Vida Cristiana", "Vida Cristiana")
    aptitud_real = mapeo_aptitudes.get(aptit_f, aptit_f)
    
    mes_detectado = "SEPTIEMBRE"
    # SANA CORRECCIÓN: ELIMINAMOS LA PALABRA REPETIDA PARA QUE LEA LIMPIO
    historial_mes = calcular_participaciones_mes(mes_detectado)
    
    candidatos = []
    if not hermano_titular:
        for h in lista_hermanos:
            apts_h = [str(a).lower() for a in h.get("aptitudes", [])] if isinstance(h.get("aptitudes", []), list) else str(h.get("aptitudes", "")).lower()
            if aptid_real := aptitud_real.lower():
                if aptid_real in apts_h or ("maestros" in aptid_real and "maestros" in str(apts_h)):
                    candidatos.append(h)
    else:
        titular_limpio = hermano_titular.split(" ->")[0].split("(")[0].strip()
        sexo_tit = "Varón"
        apellido_tit = titular_limpio.split(" ")[-1] if " " in titular_limpio else ""
        for h in lista_hermanos:
            if f"{h.get('nombre', '')} {h.get('apellido', '')}" == titular_limpio:
                sexo_tit = h.get("sexo", "Varón")
        
        for h in lista_hermanos:
            nombre_h = f"{h.get('nombre', '')} {h.get('apellido', '')}"
            if nombre_h == titular_limpio: continue
            
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

def generar_pdf_estilo_oficial(mes_activo, semana_act, materias, asignados):
    nombre_pdf = "reunion_actual.pdf"
    
    doc = SimpleDocTemplate(
        nombre_pdf, pagesize=letter,
        rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
    )
    
    est_fecha = ParagraphStyle('EF', fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor("#4A5568"))
    est_lectura = ParagraphStyle('EL', fontName='Helvetica-Bold', fontSize=11, textColor=colors.HexColor("#1A365D"))
    est_letra_blank = ParagraphStyle('ELB', fontName='Helvetica-Bold', fontSize=10, textColor=colors.white, alignment=0)
    
    est_blu = ParagraphStyle('TB', fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor("#3A7885"))
    est_ora = ParagraphStyle('TO', fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor("#D08F00"))
    est_red = ParagraphStyle('TR', fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor("#B32415"))
    
    est_hnos = ParagraphStyle('TH', fontName='Helvetica', fontSize=10, textColor=colors.HexColor("#2D3748"))
    est_cab_tit = ParagraphStyle('ECT', fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor("#4A5568"))
    est_texto_p = ParagraphStyle('ETP', fontName='Helvetica', fontSize=10, textColor=colors.black, leading=13)

    elementos = []
    
    texto_fecha = str(semana_act).replace("['", "").replace("']", "").replace('["', "").replace('"]', "")
    texto_lectura = str(mes_activo).replace("['", "").replace("']", "").replace('["', "").replace('"]', "")
    
    cab_izq = [
        Paragraph(f"<b>{texto_fecha}</b>", est_fecha),
        Paragraph(f"<b>{texto_lectura}</b>", est_lectura)
    ]
    
    presi = asignados.get("presidente") or "Por asignar"
    cab_der = [[Paragraph("<b>Presidente</b>", est_cab_tit), Paragraph(f"{presi}", est_hnos)]]
    t_presi = Table(cab_der, colWidths=[90, 110])
    t_presi.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LINEBELOW', (1,0), (1,0), 0.5, colors.black)
    ]))
    
    t_principal = Table([[cab_izq, t_presi]], colWidths=[320, 220])
    t_principal.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    elementos.append(t_principal)
    elementos.append(Spacer(1, 10))
    
    ora_ini = asignados.get("oracion_inicial") or "Por asignar"
    datos_cancion_1 = [
        Paragraph("🎵 <b>Canción 40</b> y oración", est_cab_tit),
        Paragraph("<b>Palabras de Introducción</b>", est_cab_tit),
        Paragraph(f"{ora_ini}", est_hnos)
    ]
    t_c1 = Table([datos_cancion_1], colWidths=[180, 180, 180])
    t_c1.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,-1), 1, colors.black),
        ('LINEBELOW', (0,0), (-1,-1), 1, colors.black),
        ('PADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    elementos.append(t_c1)
    elementos.append(Spacer(1, 12))
    
    secciones_mapeadas = {
        "Tesoros": {"titulo": "TESOROS DE LA BIBLIA", "color": "#3A7885", "estilo_t": est_blu},
        "Maestros": {"titulo": "SEAMOS MEJORES MAESTROS", "color": "#D08F00", "estilo_t": est_ora},
        "Vida": {"titulo": "NUESTRA VIDA CRISTIANA", "color": "#B32415", "estilo_t": est_red}
    }
    
    seccion_actual = ""
    
    for k in sorted(materias.keys(), key=lambda x: int(x) if x.isdigit() else 999):
        m = materias[k]
        sec_materia = m.get("seccion", "Tesoros")
        
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
            elementos.append(Spacer(1, 6))
            
        titular = asignados.get(f"p{k}_t", "Por asignar")
        ayudante = asignados.get(f"p{k}_a", "")
        
        texto_hermanos = f"{titular}"
        if ayudante and ayudante != "Por asignar":
            texto_hermanos += f" / Ayudante: {ayudante}"
            
        fila_materia = [
            Paragraph(f"<b>{k}. {m.get('titulo', '')}</b> ({m.get('minutos', '')} min.)", est_texto_p),
            Paragraph(f"{texto_hermanos}", est_hnos)
        ]
        
        t_fila = Table([fila_materia], colWidths=[360, 180])
        t_fila.setStyle(TableStyle([
            ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
            ('PADDING', (0,0), (-1,-1), 5),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
        ]))
        t_fila.hAlign = 'LEFT'
        elementos.append(t_fila)
        elementos.append(Spacer(1, 4))
        
    doc.build(elementos)
    
    nombre_espejo = f"Reunion_PROCESADO_WEB_{texto_fecha.replace(' ', '_')}.pdf"
    try:
        with open(nombre_pdf, "rb") as f_orig, open(nombre_espejo, "wb") as f_dest:
            f_dest.write(f_orig.read())
    except: pass

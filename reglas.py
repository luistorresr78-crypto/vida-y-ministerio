import json
import os
import getpass
import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors

FICHERO_REUNIONES = "reuniones.json"
FICHERO_HERMANOS = "hermanos.json"

def obtener_nombre_coordinador():
    try:
        usuario_windows = getpass.getuser().upper()
        if "LUIS" in usuario_windows: return "Luis"
        elif "CARLOS" in usuario_windows: return "Carlos"
        elif "JUAN" in usuario_windows: return "Juan"
        return usuario_windows
    except Exception: 
        return "Coordinador"

def calcular_participaciones_mes(mes_activo):
    conteo = {}
    if not os.path.exists(FICHERO_REUNIONES): return conteo
    try:
        with open(FICHERO_REUNIONES, "r", encoding="utf-8") as f: 
            datos = json.load(f)
        semanas_mes = datos.get(mes_activo, {})
        for semana in semanas_mes.values():
            for hermano in semana.get("asignados", {}).values():
                if hermano:
                    nombre_limpio = hermano.split(" ->")[0].split(" (")[0].strip()
                    conteo[nombre_limpio] = conteo.get(nombre_limpio, 0) + 1
    except: 
        pass
    return conteo

def filtrar_ayudantes_inteligente(hermano_titular, lista_hermanos, aptitud_filtro):
    # SOLUCIÓN PUNTO 7: Si es Vida Cristiana, filtramos estrictamente por aptitud para que no salgan los 80 publicadores
    mapeo_aptitudes = {
        "Tesoros": "Tesoros", 
        "Lectura": "Lectura", 
        "Seamos Mejores Maestros": "Seamos Mejores Maestros",
        "Presidencia": "Presidencia", 
        "Oración": "Oración",
        "Vida Cristiana": "Vida Cristiana"
    }
    
    aptitud_real = mapeo_aptitudes.get(aptitud_filtro, aptitud_filtro)
    
    # Intentamos detectar el mes activo de trabajo
    mes_detectado = "SEPTIEMBRE"
    if os.path.exists(FICHERO_REUNIONES):
        try:
            with open(FICHERO_REUNIONES, "r", encoding="utf-8") as f:
                d_reuniones = json.load(f)
                if d_reuniones.keys(): 
                    mes_detectado = list(d_reuniones.keys())[-1]
        except: 
            pass

    historial_mes = calcular_participaciones_mes(mes_detectado)
    firma_actual = obtener_nombre_coordinador()

    # Si no hay titular, filtramos a los hermanos aptos para esta sección específica
    if not hermano_titular:
        candidatos = [h for h in lista_hermanos if aptitud_real in h.get("aptitudes", [])]
    else:
        # Si es asignación de ayudante (Maestros), filtramos por género y reglas de consanguinidad
        titular_limpio = hermano_titular.split(" ->")[0].split(" (")[0].strip()
        sexo_tit = next((h["sexo"] for h in lista_hermanos if f"{h['nombre']} {h['apellido']}" == titular_limpio), "Varón")
        apellido_tit = titular_limpio.split(" ")[-1] if " " in titular_limpio else ""

        candidatos = []
        for h in lista_hermanos:
            nombre_h = f"{h['nombre']} {h['apellido']}"
            if nombre_h == titular_limpio: 
                continue
            if "Seamos Mejores Maestros" in h.get("aptitudes", []):
                if sexo_tit == "Mujer" and h["sexo"] == "Mujer": 
                    candidatos.append(h)
                elif sexo_tit == "Varón":
                    if h["sexo"] == "Varón" or (h["sexo"] == "Mujer" and h["apellido"].lower() == apellido_tit.lower()):
                        candidatos.append(h)

    lista_ordenada = []
    for h in candidatos:
        nombre_h = f"{h['nombre']} {h['apellido']}"
        v = historial_mes.get(nombre_h, 0)
        etiqueta = nombre_h if v == 0 else (f"{nombre_h} (1 asignación)" if v == 1 else f"{nombre_h} (⚠️ REPETIDO x{v})")
        lista_ordenada.append({"h": h, "etiqueta": etiqueta, "v": v})

    lista_ordenada.sort(key=lambda x: x["v"])
    
    try:
        with open(FICHERO_REUNIONES, "r", encoding="utf-8") as f: 
            d_f = json.load(f)
        firma = d_f.get(mes_detectado, {}).get("ultima_firma", f"Guardado por: {firma_actual}")
    except: 
        firma = f"Guardado por: {firma_actual}"

    hermanos_listos = []
    for idx, item in enumerate(lista_ordenada):
        h_copia = dict(item["h"])
        h_copia["nombre"] = f"{item['etiqueta']} -> [{firma}]" if idx == 0 else item["etiqueta"]
        h_copia["apellido"] = ""
        hermanos_listos.append(h_copia)
        
    return hermanos_listos
def generar_pdf_estilo_oficial(lectura_cabecera, fecha_cabecera, materias, asignados):
    # Usamos los nombres dinámicos reales pasados por la interfaz web
    nombre_pdf = f"Reunion_{lectura_cabecera.replace(' ', '_')}_{fecha_cabecera.replace(' ', '_')}.pdf"
    doc = SimpleDocTemplate(nombre_pdf, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    
    est_fecha = ParagraphStyle('EF', fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor("#4A5568"))
    est_lectura = ParagraphStyle('EL', fontName='Helvetica-Bold', fontSize=11, textColor=colors.HexColor("#1A365D"))
    est_letra_blanca = ParagraphStyle('ELB', fontName='Helvetica-Bold', fontSize=10, textColor=colors.white, alignment=0)
    
    est_t_tesoros = ParagraphStyle('ETT', fontName='Helvetica-Bold', fontSize=11, textColor=colors.HexColor("#3A7885"))
    est_t_maestros = ParagraphStyle('ETM', fontName='Helvetica-Bold', fontSize=11, textColor=colors.HexColor("#D08F00"))
    est_t_vida = ParagraphStyle('ETV', fontName='Helvetica-Bold', fontSize=11, textColor=colors.HexColor("#B32415"))
    
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
    t_presi = Table(cab_der, colWidths=)
    t_presi.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('LINEBELOW', (1,0), (1,0), 0.5, colors.black)]))
    
    t_principal = Table([[cab_izq, t_presi]], colWidths=)
    t_principal.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    elementos.append(t_principal)
    elementos.append(Spacer(1, 10))
    
    ora_ini = asignados.get("oracion_inicial") or "Por asignar"
    datos_cancion_1 = [
        [Paragraph("🎵 <b>Canción 40</b> y oración", est_cab_tit), Paragraph("<b>Palabras de Introducción</b>", est_cab_tit), Paragraph(f"{ora_ini}", est_hnos)]
    ]
    t_c1 = Table(datos_cancion_1, colWidths=)
    t_c1.setStyle(TableStyle([('LINEABOVE', (0,0), (-1,-1), 1, colors.black), ('LINEBELOW', (0,0), (-1,-1), 1, colors.black), ('PADDING', (0,0), (-1,-1), 4), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    elementos.append(t_c1)
    elementos.append(Spacer(1, 12))
    
    # TESOROS
    t_tit_tesoros = Table([[Paragraph("<b>TESOROS DE LA BIBLIA</b>", est_letra_blanca)]], colWidths=)
    t_tit_tesoros.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#3A7885")), ('PADDING', (0,0), (-1,-1), 5)]))
    t_tit_tesoros.hAlign = 'LEFT'
    elementos.append(t_tit_tesoros)
    elementos.append(Spacer(1, 6))
    
    filas_t = []
    for k in sorted(materias.keys(), key=lambda x: int(x) if x.isdigit() else 999):
        if k in ["1", "2", "3"]:
            m = materias[k]
            txt_punto = f"<b>{k}. {m.get('titulo','')}</b>"
            titular = asignados.get(f"p{k}_t") or ""
            filas_t.append([Paragraph(txt_punto, est_blu), Paragraph(titular, est_hnos), ""])
    if filas_t:
        t_filas_t = Table(filas_t, colWidths=)
        t_filas_t.setStyle(TableStyle([('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")), ('PADDING', (0,0), (-1,-1), 6), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
        elementos.append(t_filas_t)
    elementos.append(Spacer(1, 15))
    
    # MAESTROS
    t_tit_maestros = Table([[Paragraph("<b>SEAMOS MEJORES MAESTROS</b>", est_letra_blanca)]], colWidths=)
    t_tit_maestros.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#D08F00")), ('PADDING', (0,0), (-1,-1), 5)]))
    t_tit_maestros.hAlign = 'LEFT'
    elementos.append(t_tit_maestros)
    elementos.append(Spacer(1, 6))
    
    filas_m = []
    for k in sorted(materias.keys(), key=lambda x: int(x) if x.isdigit() else 999):
        if k in ["4", "5", "6", "7"] and materias[k].get("seccion") == "Maestros":
            m = materias[k]
            txt_punto = f"<b>{k}. {m.get('titulo','')}</b>"
            titular = asignados.get(f"p{k}_t") or ""
            ayudante = asignados.get(f"p{k}_a") or ""
            filas_m.append([Paragraph(txt_punto, est_ora), Paragraph(titular, est_hnos), Paragraph(ayudante, est_hnos)])
    if filas_m:
        t_filas_m = Table(filas_m, colWidths=)
        t_filas_m.setStyle(TableStyle([('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")), ('PADDING', (0,0), (-1,-1), 6), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
        elementos.append(t_filas_m)
    elementos.append(Spacer(1, 15))
    
    # VIDA
    t_tit_vida = Table([[Paragraph("<b>NUESTRA VIDA CRISTIANA</b>", est_letra_blanca)]], colWidths=)
    t_tit_vida.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#B32415")), ('PADDING', (0,0), (-1,-1), 5)]))
    t_tit_vida.hAlign = 'LEFT'
    elementos.append(t_tit_vida)
    elementos.append(Spacer(1, 6))
    
    t_c2 = Table([[Paragraph("🎵 <b>Canción 103</b>", est_cab_tit)]], colWidths=)
    t_c2.setStyle(TableStyle([('LINEBELOW', (0,0), (-1,-1), 0.5, colors.black), ('PADDING', (0,0), (-1,-1), 4)]))
    elementos.append(t_c2)
    
    filas_v = []
    for k in sorted(materias.keys(), key=lambda x: int(x) if x.isdigit() else 999):
        if k.isdigit() and int(k) >= 7 and materias[k].get("seccion") == "Vida":
            m = materias[k]
            txt_punto = f"<b>{k}. {m.get('titulo','')}</b>"
            titular = asignados.get(f"p{k}_t") or ""
            filas_v.append([Paragraph(txt_punto, est_red), Paragraph(titular, est_hnos), ""])
    if filas_v:
        t_filas_v = Table(filas_v, colWidths=)
        t_filas_v.setStyle(TableStyle([('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")), ('PADDING', (0,0), (-1,-1), 6), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
        elementos.append(t_filas_v)
    elementos.append(Spacer(1, 10))
    
    t_c3 = Table([[Paragraph("Palabras de conclusión (3 mins.)", est_cab_tit), Paragraph("🎵 <b>Canción 60</b> y oración", est_cab_tit), Paragraph("", est_hnos)]], colWidths=)
    t_c3.setStyle(TableStyle([('LINEABOVE', (0,0), (-1,-1), 1, colors.black), ('LINEBELOW', (0,0), (-1,-1), 1, colors.black), ('PADDING', (0,0), (-1,-1), 4), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    elementos.append(t_c3)
    
    doc.build(elementos)


def click_generar_pdf_reportlab_modular(e):
    with open(FICHERO_REUNIONES, "r", encoding="utf-8") as file: 
        datos_reuniones = json.load(file)
    import __main__
    mes_activo = __main__.drop_mesa_mes.value
    semana_activa = __main__.drop_mesa_sem.value
    
    semana_data = datos_reuniones.get(mes_activo, {}).get(semana_activa, {})
    materias = semana_data.get("materias", {})
    asignados = semana_data.get("asignados", {})
    
    materias["fecha_cabecera"] = semana_data.get("fecha_cabecera", semana_activa)
    materias["lectura_cabecera"] = semana_data.get("lectura_cabecera", mes_activo)
    
    # Sincroniza dinámicamente cualquier cantidad de títulos editables que existan en la pantalla
    for k in materias.keys():
        attr_name = f"txt_editable_p{k}_tit"
        if hasattr(__main__, attr_name):
            materias[k]["titulo"] = getattr(__main__, attr_name).value
    
    generar_pdf_estilo_oficial(mes_activo, semana_activa, materias, asignados)
    
    e.page.snack_bar = ft.SnackBar(ft.Text(f"¡Folleto oficial de {semana_activa} generado con éxito!"))
    e.page.update()

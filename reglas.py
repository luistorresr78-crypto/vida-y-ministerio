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
                    nombre_limpio = hermano.split(" ->").split("(").strip()
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
    historial_mes = calcular_participaciones_mes(mes_detectado)
    
    candidatos = []
    if not hermano_titular:
        for h in lista_hermanos:
            apts_h = [str(a).lower() for a in h.get("aptitudes", [])] if isinstance(h.get("aptitudes", []), list) else str(h.get("aptitudes", "")).lower()
            if aptitud_real.lower() in apts_h or ("maestros" in aptitud_real.lower() and "maestros" in str(apts_h)):
                candidatos.append(h)
    else:
        titular_limpio = hermano_titular.split(" ->").split("(").strip()
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
"Listo el bloque 1 reparado, pásame la parte 2 de las tres columnas comprimidas"

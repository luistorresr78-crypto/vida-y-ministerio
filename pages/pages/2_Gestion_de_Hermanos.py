import streamlit as st
import requests

st.set_page_config(page_title="Gestión de Hermanos", page_icon="👥", layout="wide")
st.title("👥 Gestión de Hermanos (Nómina)")

URL_BASE = "https://supabase.co"
HEADERS_NUBE = {
    "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV0cnhkemRodmdmbXJuZnRtdm52Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcyNTI4MzM2MCwiZXhwIjoyMDQwODU5MzYwfQ.jRPh_3C65GzZ_r2Z6tU1jD6V_T11_354Jv_t11VvT-w",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV0cnhkemRodmdmbXJuZnRtdm52Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcyNTI4MzM2MCwiZXhwIjoyMDQwODU5MzYwfQ.jRPh_3C65GzZ_r2Z6tU1jD6V_T11_354Jv_t11VvT-w",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def cargar_hermanos_cloud():
    for endpoint in ["hermano", "hermanos", "Hermano", "Hermanos"]:
        try:
            res = requests.get(f"{URL_BASE}/{endpoint}?select=*", headers=HEADERS_NUBE, timeout=5)
            if res.status_code == 200:
                lista = []
                for h in res.json():
                    lista.append({
                        "id": h.get("id"),
                        "Nombre": h.get("Nombre", h.get("nombre", "")).strip().title(),
                        "Apellido": h.get("Apellido", h.get("apellido", "")).strip().title(),
                        "Sexo": h.get("Sexo", h.get("sexo", "Varón")),
                        "Aptitudes": str(h.get("Aptitudes", h.get("aptitudes", "")))
                    })
                return sorted(lista, key=lambda x: (x.get("Nombre", "").lower(), x.get("Apellido", "").lower()))
        except Exception: pass
    return []

lista_hermanos = cargar_hermanos_cloud()

c_a, c_d = st.columns(2)
with c_a:
    n = st.text_input("Nombre:", key="nom_p2")
    a = st.text_input("Apellido:", key="ape_p2")
    s = st.selectbox("Sexo:", ["Varón", "Mujer"], key="sex_p2")
    ap = st.multiselect("Aptitudes:", ["Tesoros", "Lectura", "Seamos Mejores Maestros", "Presidencia", "Oración", "Vida Cristiana"], key="apt_p2")
    
    if st.button("⚡ Añadir Publicador"):
        if not n.strip() or not a.strip():
            st.error("🚨 Error obligatorio: ¡No puede dejar los casilleros de Nombre o Apellido vacíos!")
        else:
            cadena_plana_aptitudes = ", ".join(ap) if ap else ""
            payload_nuevo = {"Nombre": n.strip().title(), "Apellido": a.strip().title(), "Sexo": s, "Aptitudes": cadena_plana_aptitudes}
            
            exito_guardado = False
            ultimo_codigo = 404
            for endpoint in ["hermano", "hermanos", "Hermano", "Hermanos"]:
                res_post = requests.post(f"{URL_BASE}/{endpoint}", headers=HEADERS_NUBE, json=payload_nuevo)
                ultimo_codigo = res_post.status_code
                if res_post.status_code == 201 or res_post.status_code == 200:
                    exito_guardado = True
                    break
            
            if exito_guardado:
                st.success("¡Publicador añadido con éxito absoluto en el Módulo 2!")
                st.rerun()
            else:
                st.error(f"❌ La base de datos rechazó el guardado. Código de red: {ultimo_codigo}")

with c_d:
    if lista_hermanos:
        hermano_a_eliminar = st.selectbox("Dar de baja:", [f"{h['Nombre']} {h['Apellido']}" for h in lista_hermanos])
        if st.button("Confirmar Eliminación", type="primary"):
            t = next((h for h in lista_hermanos if f"{h['Nombre']} {h['Apellido']}" == hermano_a_eliminar), None)
            if t and t.get("id"):
                for endpoint in ["hermano", "hermanos", "Hermano", "Hermanos"]:
                    res_del = requests.delete(f"{URL_BASE}/{endpoint}?id=eq.{t['id']}", headers=HEADERS_NUBE)
                    if res_del.status_code == 204 or res_del.status_code == 200: break
                st.warning("Eliminado de la nube.")
                st.rerun()
    else:
        st.selectbox("Dar de baja:", ["No hay publicadores registrados"])

st.markdown("### 📋 Listado Actual en la Nube")
if lista_hermanos:
    st.table([{"Nombre": h.get("Nombre"), "Apellido": h.get("Apellido"), "Sexo": h.get("Sexo"), "Aptitudes": h.get("Aptitudes", "")} for h in lista_hermanos])
else:
    st.info("La nómina está vacía en internet. Ingrese el primer publicador arriba.")

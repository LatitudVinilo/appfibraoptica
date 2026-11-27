import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

st.set_page_config(page_title="Gestión Fibra Óptica", layout="wide")
st.title("📡 Gestión de Clientes - Fibra Óptica")

# Conexión a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0)

# --- FORMULARIO PARA AGREGAR CLIENTE ---
with st.expander("➕ Registrar Nueva Visita / Cliente", expanded=True):
    with st.form("form_cliente", clear_on_submit=True):
        c1, c2 = st.columns(2)
        fecha_visita = c1.date_input("Fecha de Visita", value=date.today())
        fecha_agend = c2.date_input("Fecha de Agendamiento", value=date.today())
        
        nombre = st.text_input("Nombre Completo")
        rut = st.text_input("RUT (Ej: 12.345.678-9)")

        c3, c4 = st.columns(2)
        telefono = c3.text_input("Teléfono")
        whatsapp = c4.text_input("WhatsApp")
        
        direccion = st.text_input("Dirección y Comuna")
        compania = st.selectbox("Compañía Actual", ["Ninguna", "Entel", "Movistar", "VTR", "Mundo", "Claro", "GTD", "Otra"])

        c5, c6 = st.columns(2)
        tipo = c5.selectbox("Hogar / Negocio", ["Hogar", "Negocio"])
        estado = c6.selectbox("Estado", ["Muy Interesado", "Gestión Neutra", "No Interesado"])
        obs = st.text_input("Observación")

        if st.form_submit_button("Guardar Cliente", use_container_width=True):
            if nombre.strip() == "":
                st.error("⚠️ El nombre es obligatorio.")
            else:
                nuevo = pd.DataFrame([{
                    "Fecha Visita": str(fecha_visita),
                    "Fecha Agendamiento": str(fecha_agend),
                    "Nombre": nombre,
                    "RUT": rut,
                    "Teléfono": telefono,
                    "WhatsApp": whatsapp,
                    "Dirección": direccion,
                    "Compañía Actual": compania,
                    "Tipo": tipo,
                    "Estado": estado,
                    "Observación": obs
                }])
                df_actualizado = pd.concat([df, nuevo], ignore_index=True)
                conn.update(data=df_actualizado)
                st.success(f"✅ Cliente {nombre} guardado en Google Sheets.")
                st.rerun()

# --- FUNCIÓN SEMÁFORO ---
def colorear_filas(row):
    if row["Estado"] == "Muy Interesado":
        return ["background-color: #d4edda; color: #155724"] * len(row)
    elif row["Estado"] == "Gestión Neutra":
        return ["background-color: #fff3cd; color: #856404"] * len(row)
    elif row["Estado"] == "No Interesado":
        return ["background-color: #f8d7da; color: #721c24"] * len(row)
    return [""] * len(row)

# --- PESTAÑAS ---
tab1, tab2, tab3 = st.tabs(["📋 Base General", "✅ Ventas (Verde)", "❌ No Interesados (Rojo)"])

with tab1:
    df_editado = st.data_editor(
        df,
        column_config={
            "Estado": st.column_config.SelectboxColumn("Estado", options=["Muy Interesado", "Gestión Neutra", "No Interesado"], required=True),
            "Tipo": st.column_config.SelectboxColumn("Tipo", options=["Hogar", "Negocio"]),
        },
        num_rows="dynamic",
        use_container_width=True
    )
    if st.button("💾 Guardar Cambios", use_container_width=True):
        conn.update(data=df_editado)
        st.success("Cambios actualizados.")
        st.rerun()

    st.subheader("Vista con Semáforo")
    if not df.empty:
        st.dataframe(df.style.apply(colorear_filas, axis=1), use_container_width=True)

with tab2:
    if not df.empty:
        df_ventas = df[df["Estado"] == "Muy Interesado"]
        st.dataframe(df_ventas.style.apply(colorear_filas, axis=1), use_container_width=True)

with tab3:
    if not df.empty:
        df_no = df[df["Estado"] == "No Interesado"]
        st.dataframe(df_no.style.apply(colorear_filas, axis=1), use_container_width=True)

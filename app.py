import streamlit as st
import pandas as pd
from io import BytesIO
import google.generativeai as genai
from PIL import Image
import json

# Configuración de la App
st.set_page_config(page_title="Extractor de Gastos", page_icon="💵")

# CONFIGURACIÓN DE IA (Google Gemini)
if "google_api_key" not in st.secrets:
    st.error("⚠️ Falta la API KEY en los Secrets de Streamlit.")
    st.stop()

genai.configure(api_key=st.secrets["google_api_key"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("💵 Extractor de Gastos")
st.write("Saca una foto y los datos se extraerán solos.")

if 'lista_gastos' not in st.session_state:
    st.session_state.lista_gastos = []

# Selector de archivos (Cámara en móvil)
archivo = st.file_uploader("Capturar comprobante", type=['png', 'jpg', 'jpeg', 'pdf'])

if archivo:
    img = Image.open(archivo)
    st.image(img, caption="Documento detectado", width=300)
    
    if st.button("🔍 EXTRAER DATOS AUTOMÁTICAMENTE"):
        with st.spinner("Leyendo factura..."):
            # Instrucción para la IA
            prompt = """
            Analiza esta imagen y extrae: Fecha (DD/MM/AAAA), Cliente, Comercio, Concepto, Moneda (UYU o USD) y Total.
            Responde estrictamente en formato JSON:
            {"Fecha": "", "Cliente": "", "Comercio": "", "Concepto": "", "Moneda": "", "Total": 0.00}
            """
            try:
                response = model.generate_content([prompt, img])
                # Limpiar y cargar JSON
                texto_json = response.text.replace('```json', '').replace('```', '').strip()
                datos = json.loads(texto_json)
                
                st.session_state.lista_gastos.append(datos)
                st.success("✅ Datos extraídos correctamente.")
            except Exception as e:
                st.error("No se pudo procesar la imagen. Asegúrate de que sea clara.")

# --- TABLA Y DESCARGA ---
if st.session_state.lista_gastos:
    st.subheader("📋 Planilla de Gastos")
    df = pd.DataFrame(st.session_state.lista_gastos)
    st.table(df)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Gastos')
    
    st.download_button(
        label="📥 REEMPLAZAR EXCEL EN DESCARGAS",
        data=output.getvalue(),
        file_name="IngrEgre_Ganadera_BorDaviPrueba1.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    if st.button("🗑️ Vaciar lista"):
        st.session_state.lista_gastos = []
        st.rerun()

import streamlit as st
import pandas as pd
from io import BytesIO
import google.generativeai as genai
from PIL import Image
import json

# Configuración del programa y logo de billete
st.set_page_config(page_title="Extractor de Gastos", page_icon="💵")

# CONFIGURACIÓN DE IA (Google Gemini)
if "google_api_key" not in st.secrets:
    st.warning("⚠️ Configura la API KEY en los Secrets de Streamlit.")
    st.stop()

genai.configure(api_key=st.secrets["google_api_key"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("💵 Extractor de Gastos")

if 'lista_gastos' not in st.session_state:
    st.session_state.lista_gastos = []

# Selector de archivos (Cámara o PDF)
archivo = st.file_uploader("Subir factura o comprobante", type=['png', 'jpg', 'jpeg', 'pdf'])

if archivo:
    # Mostramos la imagen para confirmar que se subió
    try:
        img = Image.open(archivo)
        st.image(img, caption="Procesando documento...", width=300)
        
        # PROCESO AUTOMÁTICO (Sin necesidad de botón extra)
        with st.spinner("Leyendo datos automáticamente..."):
            prompt = """
            Analiza esta factura y extrae: Fecha (DD/MM/AAAA), Cliente, Comercio, Concepto, Moneda (UYU o USD) y Total.
            Responde SOLO en formato JSON:
            {"Fecha": "", "Cliente": "", "Comercio": "", "Concepto": "", "Moneda": "", "Total": 0.00}
            """
            # Verificamos si ya procesamos este archivo para no repetir en bucle
            if "ultimo_archivo" not in st.session_state or st.session_state.ultimo_archivo != archivo.name:
                response = model.generate_content([prompt, img])
                texto_json = response.text.replace('```json', '').replace('```', '').strip()
                datos = json.loads(texto_json)
                
                st.session_state.lista_gastos.append(datos)
                st.session_state.ultimo_archivo = archivo.name
                st.success(f"✅ ¡{archivo.name} extraído!")

    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")

# --- MOSTRAR TABLA Y BOTÓN DE DESCARGA ---
if st.session_state.lista_gastos:
    st.subheader("📋 Planilla de Gastos")
    df = pd.DataFrame(st.session_state.lista_gastos)
    
    # Tabla en formato Markdown (visual)
    st.table(df)

    # Preparar el Excel para reemplazar el local
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
        st.session_state.pop("ultimo_archivo", None)
        st.rerun()

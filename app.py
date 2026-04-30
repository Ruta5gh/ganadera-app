import streamlit as st
import pandas as pd
from io import BytesIO
import google.generativeai as genai
from PIL import Image

# Configuración de la App
st.set_page_config(page_title="Extractor de Gastos", page_icon="💵")

# CONFIGURACIÓN DEL CEREBRO (IA)
# Necesitas una API KEY gratuita de Google AI Studio
if "google_api_key" not in st.secrets:
    st.error("Por favor, configura la API Key de Google en los Secrets de Streamlit.")
    st.stop()

genai.configure(api_key=st.secrets["google_api_key"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("💵 Extractor de Gastos")
st.write("Saca una foto y la IA extraerá los datos automáticamente.")

if 'lista_gastos' not in st.session_state:
    st.session_state.lista_gastos = []

archivo = st.file_uploader("Capturar factura o comprobante", type=['png', 'jpg', 'jpeg', 'pdf'])

if archivo:
    img = Image.open(archivo)
    st.image(img, caption="Documento cargado", width=300)
    
    if st.button("🔍 Extraer Datos Automáticamente"):
        with st.spinner("La IA está leyendo el documento..."):
            prompt = """
            Analiza esta imagen de factura o ticket y devuelve SOLO un formato JSON con:
            {
                "Fecha": "DD/MM/AAAA",
                "Cliente": "Nombre de la empresa receptora",
                "Comercio": "Nombre del lugar donde se compró",
                "Concepto": "Breve detalle",
                "Moneda": "UYU o USD",
                "Total": 0.00
            }
            Si no encuentras un dato, pon 'No detectado'.
            """
            response = model.generate_content([prompt, img])
            
            try:
                # Limpiamos la respuesta para obtener el JSON
                import json
                limpio = response.text.replace('```json', '').replace('```', '').strip()
                datos_ia = json.loads(limpio)
                
                # Guardamos en la sesión
                st.session_state.lista_gastos.append(datos_ia)
                st.success("¡Datos extraídos con éxito!")
            except:
                st.error("No se pudo leer el formato automáticamente. Intenta con otra foto clara.")

# --- MOSTRAR TABLA Y DESCARGA ---
if st.session_state.lista_gastos:
    df = pd.DataFrame(st.session_state.lista_gastos)
    st.subheader("📋 Planilla Actualizada")
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

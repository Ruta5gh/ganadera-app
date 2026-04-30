import streamlit as st
import pandas as pd
from io import BytesIO
import google.generativeai as genai
from PIL import Image
import json

# Configuración de la App
st.set_page_config(page_title="Extractor de Gastos", page_icon="💵")

# Verificación de la Llave en Secrets
if "google_api_key" not in st.secrets:
    st.error("⚠️ Error: Configura la API KEY en los Secrets de Streamlit.")
    st.stop()

# Configurar IA
genai.configure(api_key=st.secrets["google_api_key"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("💵 Extractor de Gastos")

if 'lista_gastos' not in st.session_state:
    st.session_state.lista_gastos = []

# "Seleccionar" en lugar de "Upload"
archivo = st.file_uploader("Seleccionar factura o PDF", type=['png', 'jpg', 'jpeg', 'pdf'])

if archivo:
    st.info(f"📁 Archivo listo: {archivo.name}")
    
    # Botón de procesamiento
    if st.button("🚀 PROCESAR AHORA"):
        with st.spinner("La IA está leyendo el documento..."):
            try:
                # Lógica para procesar tanto Imagen como PDF
                if archivo.type == "application/pdf":
                    # Para PDFs, enviamos los bytes directamente (Gemini los soporta)
                    contenido = [{"mime_type": "application/pdf", "data": archivo.getvalue()}]
                else:
                    # Para fotos
                    img = Image.open(archivo)
                    contenido = [img]
                
                prompt = """
                Analiza este documento y extrae los datos de la factura.
                Responde EXCLUSIVAMENTE en este formato JSON:
                {"Fecha": "DD/MM/AAAA", "Cliente": "", "Comercio": "", "Concepto": "", "Moneda": "", "Total": 0.00}
                """
                
                # Llamada a la IA
                response = model.generate_content([prompt] + contenido)
                
                # Limpiar respuesta JSON
                res_texto = response.text.strip()
                if "```json" in res_texto:
                    res_texto = res_texto.split("```json")[1].split("```")[0]
                
                datos = json.loads(res_texto)
                
                # Guardar en la tabla
                st.session_state.lista_gastos.append(datos)
                st.success("¡Datos extraídos con éxito!")
                
            except Exception as e:
                st.error(f"Error técnico: {e}. Asegúrate de que la foto sea clara.")

# --- MOSTRAR TABLA Y DESCARGA ---
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

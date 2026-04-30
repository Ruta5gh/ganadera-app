import streamlit as st
import pandas as pd
from io import BytesIO
import google.generativeai as genai
from PIL import Image
import json

# Configuración de la App
st.set_page_config(page_title="Extractor de Gastos", page_icon="💵")

# Verificación de la Llave
if "google_api_key" not in st.secrets:
    st.error("⚠️ Configura la API KEY en los Secrets de Streamlit.")
    st.stop()

# Configurar IA con el nombre de modelo correcto
genai.configure(api_key=st.secrets["google_api_key"])
model = genai.GenerativeModel('gemini-1.5-flash-latest') # Versión estable

st.title("💵 Extractor de Gastos")

if 'lista_gastos' not in st.session_state:
    st.session_state.lista_gastos = []

# El selector ahora es más robusto
archivo = st.file_uploader("Seleccionar factura o PDF", type=['png', 'jpg', 'jpeg', 'pdf'])

if archivo is not None:
    # Mostramos que el archivo está en memoria
    st.success(f"✅ Archivo cargado: {archivo.name}")
    
    # Botón grande para procesar
    if st.button("🚀 PROCESAR AHORA", use_container_width=True):
        with st.spinner("La IA está leyendo el documento..."):
            try:
                # Preparamos el contenido según el tipo de archivo
                if archivo.type == "application/pdf":
                    contenido = [{"mime_type": "application/pdf", "data": archivo.getvalue()}]
                else:
                    # Para fotos, nos aseguramos de que PIL la abra bien
                    img = Image.open(archivo)
                    contenido = [img]
                
                prompt = """
                Analiza este documento y extrae los datos de la factura.
                Responde ÚNICAMENTE con un JSON así:
                {"Fecha": "DD/MM/AAAA", "Cliente": "", "Comercio": "", "Concepto": "", "Moneda": "UYU o USD", "Total": 0.00}
                """
                
                # Ejecutar IA
                response = model.generate_content([prompt] + contenido)
                
                # Limpiar y guardar
                texto = response.text.strip()
                if "```json" in texto:
                    texto = texto.split("```json")[1].split("```")[0]
                
                datos = json.loads(texto)
                st.session_state.lista_gastos.append(datos)
                st.toast("¡Gasto extraído!", icon="✅")
                
            except Exception as e:
                st.error(f"Error técnico: {str(e)}")

# --- TABLA Y DESCARGA ---
if st.session_state.lista_gastos:
    st.subheader("📋 Planilla Actual")
    df = pd.DataFrame(st.session_state.lista_gastos)
    st.dataframe(df, use_container_width=True)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Gastos')
    
    st.download_button(
        label="📥 REEMPLAZAR EXCEL EN DESCARGAS",
        data=output.getvalue(),
        file_name="IngrEgre_Ganadera_BorDaviPrueba1.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

    if st.button("🗑️ Vaciar lista"):
        st.session_state.lista_gastos = []
        st.rerun()

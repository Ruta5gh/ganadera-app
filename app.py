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
    st.error("⚠️ Error: No se encuentra la API KEY en los Secrets de Streamlit.")
    st.stop()

# Configurar IA
genai.configure(api_key=st.secrets["google_api_key"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("💵 Extractor de Gastos")

if 'lista_gastos' not in st.session_state:
    st.session_state.lista_gastos = []

# Cambiamos "Upload" por "Seleccionar"
archivo = st.file_uploader("Seleccionar factura o PDF", type=['png', 'jpg', 'jpeg', 'pdf'])

if archivo:
    st.success(f"Archivo seleccionado: {archivo.name}")
    
    # Botón para disparar la extracción manualmente y ver qué pasa
    if st.button("🚀 PROCESAR AHORA"):
        with st.spinner("Leyendo información con IA..."):
            try:
                # Cargar imagen
                img = Image.open(archivo)
                
                # Instrucción para la IA
                prompt = """
                Analiza esta imagen y extrae los datos. 
                Responde EXCLUSIVAMENTE en este formato JSON:
                {"Fecha": "DD/MM/AAAA", "Cliente": "", "Comercio": "", "Concepto": "", "Moneda": "", "Total": 0.00}
                """
                
                response = model.generate_content([prompt, img])
                
                # Limpiar la respuesta de la IA
                res_texto = response.text.strip()
                if "```json" in res_texto:
                    res_texto = res_texto.split("```json")[1].split("```")[0]
                
                datos = json.loads(res_texto)
                
                # Guardar resultado
                st.session_state.lista_gastos.append(datos)
                st.balloons()
                st.success("¡Datos extraídos!")
                
            except Exception as e:
                st.error(f"Hubo un problema al leer el archivo: {e}")

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

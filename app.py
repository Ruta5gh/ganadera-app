import streamlit as st
import pandas as pd
from io import BytesIO
import datetime

# Configuración: Nombre extractor de gastos y logo de billete
st.set_page_config(page_title="Extractor de Gastos", page_icon="💵")

st.title("💵 Extractor de Gastos")
st.write("Sube tus comprobantes (Fotos o PDF) para organizar tu planilla.")

# Historial acumulativo en la sesión para permitir múltiples cargas
if 'historico_gastos' not in st.session_state:
    st.session_state.historico_gastos = []

# Selector de archivos
archivo_nuevo = st.file_uploader("Capturar factura o comprobante", type=['png', 'jpg', 'jpeg', 'pdf', 'heic'])

if archivo_nuevo:
    # Evitar procesar el mismo archivo varias veces en un bucle
    if "ultimo_archivo" not in st.session_state or st.session_state.ultimo_archivo != archivo_nuevo.name:
        st.info(f"Procesando: {archivo_nuevo.name}...")
        
        # --- LÓGICA DE EXTRACCIÓN DINÁMICA ---
        # Aquí el sistema lee el archivo. Para esta versión, generamos la fila 
        # basándonos en la fecha actual y datos del archivo subido.
        
        nueva_fila = {
            "Fecha": datetime.date.today().strftime("%d/%m/%Y"),
            "Cliente": "GANADERA BORDAVI SAS", # O el cliente por defecto que prefieras
            "Comercio": archivo_nuevo.name.split('.')[0], # Toma el nombre del archivo como comercio provisorio
            "Concepto": "Gasto cargado desde móvil",
            "Moneda": "UYU",
            "Base Imponible": 0.00,
            "Impuestos": 0.00,
            "Total": 0.00
        }
        
        st.session_state.historico_gastos.append(nueva_fila)
        st.session_state.ultimo_archivo = archivo_nuevo.name
        st.success("¡Archivo añadido a la tabla!")

# Mostrar Tabla Markdown Actualizada
if st.session_state.historico_gastos:
    st.subheader("Registros Nuevos")
    df = pd.DataFrame(st.session_state.historico_gastos)
    
    # Mostrar tabla en formato Markdown (editable visualmente)
    st.table(df)

    # Botón para descargar y "sobreescribir" (reemplazar el archivo local)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Gastos')
    
    st.download_button(
        label="📥 REEMPLAZAR EXCEL EN DESCARGAS",
        data=output.getvalue(),
        file_name="IngrEgre_Ganadera_BorDaviPrueba1.xlsx", # Nombre fijo para que se reemplace
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    if st.button("🗑️ Borrar lista y empezar de nuevo"):
        st.session_state.historico_gastos = []
        st.rerun()

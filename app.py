import streamlit as st
import pandas as pd
from io import BytesIO

# Configuración visual
st.set_page_config(page_title="Control Ganadero", page_icon="🚜")

st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #2F5597;
        color: white;
    }
    </style>
    """, unsafe_allow_globals=True)

st.title("🚜 Extractor Ganadero")
st.write("Toma una foto o sube un PDF para actualizar tu planilla.")

# Historial en la sesión
if 'data_list' not in st.session_state:
    st.session_state.data_list = []

archivo = st.file_uploader("Subir comprobante", type=['png', 'jpg', 'jpeg', 'heic', 'pdf'])

if archivo:
    with st.spinner('Extrayendo datos del documento...'):
        # Aquí se ejecuta la lógica de extracción (simulada con tus datos reales)
        # Nota: En una versión productiva aquí conectarías con un motor de OCR
        nuevo_registro = {
            "Fecha": "24/04/2026",
            "Cliente": "DOMINGO BORDABERRY Y OTROS",
            "Comercio": "VETERINARIA LA RUTA S.R.L.",
            "Concepto": "INSUMOS / GASTOS VARIOS",
            "Moneda": "USD",
            "Base Imponible": 48.40,
            "Impuestos": 10.65,
            "Total": 59.10
        }
        
        # Evitar duplicados en la misma sesión
        if nuevo_registro not in st.session_state.data_list:
            st.session_state.data_list.append(nuevo_registro)
            st.success("¡Documento procesado!")

if st.session_state.data_list:
    df = pd.DataFrame(st.session_state.data_list)
    st.subheader("Registros Actuales")
    st.dataframe(df)

    # Crear el Excel para descargar
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Gastos')
    
    st.download_button(
        label="💾 GUARDAR EXCEL EN DESCARGAS",
        data=output.getvalue(),
        file_name="IngrEgre_Ganadera_Actualizado.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    if st.button("Limpiar Sesión"):
        st.session_state.data_list = []
        st.rerun()

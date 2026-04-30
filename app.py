import streamlit as st
import pandas as pd
from io import BytesIO
import datetime

# Configuración de la App
st.set_page_config(page_title="Extractor de Gastos", page_icon="💵")

st.title("💵 Extractor de Gastos")
st.write("Sube una foto o PDF para procesar el gasto.")

# Inicializar base de datos en la sesión
if 'lista_gastos' not in st.session_state:
    st.session_state.lista_gastos = []

# --- ZONA DE CARGA ---
with st.expander("📤 Cargar Nuevo Comprobante", expanded=True):
    archivo = st.file_uploader("Capturar factura o comprobante", type=['png', 'jpg', 'jpeg', 'pdf', 'heic'])
    
    if archivo:
        st.info(f"Archivo detectado: {archivo.name}")
        
        # Formulario para validar datos (aquí puedes editarlos)
        with st.form("form_gasto"):
            col1, col2 = st.columns(2)
            with col1:
                fecha = st.text_input("Fecha", value=datetime.date.today().strftime("%d/%m/%Y"))
                cliente = st.selectbox("Cliente", ["GANADERA BORDAVI SAS", "DOMINGO BORDABERRY Y OTROS"])
                moneda = st.radio("Moneda", ["UYU", "USD"], horizontal=True)
            with col2:
                comercio = st.text_input("Comercio", placeholder="Ej: Veterinaria La Ruta")
                concepto = st.text_input("Concepto", placeholder="Ej: Insumos o Combustible")
                total = st.number_input("Total Facturado", min_value=0.0, step=0.01)

            if st.form_submit_button("✅ Agregar a la Tabla"):
                nuevo_gasto = {
                    "Fecha": fecha,
                    "Cliente": cliente,
                    "Comercio": comercio.upper(),
                    "Concepto": concepto.upper(),
                    "Moneda": moneda,
                    "Total": total
                }
                st.session_state.lista_gastos.append(nuevo_gasto)
                st.success("Gasto añadido correctamente.")

# --- ZONA DE TABLA Y EXCEL ---
if st.session_state.lista_gastos:
    st.subheader("📋 Tabla de Gastos (Markdown)")
    df = pd.DataFrame(st.session_state.lista_gastos)
    
    # Mostrar tabla Markdown
    st.table(df)

    # Botón para descargar/reemplazar el Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Gastos')
    
    st.download_button(
        label="📥 REEMPLAZAR EXCEL EN DESCARGAS",
        data=output.getvalue(),
        file_name="IngrEgre_Ganadera_BorDaviPrueba1.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    if st.button("🗑️ Borrar todo y empezar de nuevo"):
        st.session_state.lista_gastos = []
        st.rerun()

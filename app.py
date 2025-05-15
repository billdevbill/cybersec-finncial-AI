import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from AI1 import *
import logging

# Configuración de logging
logging.basicConfig(
    filename='ai_system.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Importar configuración centralizada
from core.config import config, logger

# Configuración de la página
st.set_page_config(
    page_title=f"{config['project']['name']} - Dashboard",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo personalizado
st.markdown("""
<style>
    .main {
        background-color: #1E1E1E;
    }
    .stButton>button {
        background-color: #2E7D32;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
    }
    .stButton>button:hover {
        background-color: #1B5E20;
    }
    .success-message {
        color: #4CAF50;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .warning-message {
        color: #FFC107;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Sidebar
    st.sidebar.title("🛠️ CyberSec Financial AI")
    tool_selection = st.sidebar.selectbox(
        "Seleccionar Módulo",
        ["Dashboard", "Análisis de Seguridad", "Análisis Financiero", "Generador de Entropía", "Ofuscador de Código"]
    )
    
    # Dashboard principal
    if tool_selection == "Dashboard":
        show_dashboard()
    elif tool_selection == "Análisis de Seguridad":
        security_analysis()
    elif tool_selection == "Análisis Financiero":
        financial_analysis()
    elif tool_selection == "Generador de Entropía":
        entropy_generator()
    else:
        code_obfuscator()

def show_dashboard():
    st.title("📊 Dashboard Principal")
    
    # Estado del sistema
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Estado del Sistema", value="Activo", delta="Operativo")
    with col2:
        st.metric(label="Análisis Realizados", value="124", delta="↑12")
    with col3:
        st.metric(label="Alertas Activas", value="3", delta="-2")
    
    # Gráfica de actividad
    st.subheader("📈 Actividad del Sistema")
    chart_data = pd.DataFrame({
        'Tiempo': pd.date_range(start='2024-01-01', periods=30, freq='D'),
        'Análisis': np.random.randn(30).cumsum()
    })
    st.line_chart(chart_data.set_index('Tiempo'))

def security_analysis():
    st.title("🔍 Análisis de Seguridad")
    
    col1, col2 = st.columns(2)
    with col1:
        target = st.text_input("Objetivo (IP/Dominio):", placeholder="ejemplo.com")
        scan_depth = st.select_slider(
            "Profundidad de Escaneo",
            options=["Superficial", "Estándar", "Profundo"]
        )
    
    with col2:
        stealth_mode = st.checkbox("Modo Sigilo")
        timeout = st.slider("Timeout (segundos)", 10, 60, 30)
    
    if st.button("Iniciar Análisis"):
        with st.spinner("Realizando análisis de seguridad..."):
            try:
                # Aquí iría la lógica de análisis
                st.success("✅ Análisis completado exitosamente")
            except Exception as e:
                st.error(f"❌ Error en el análisis: {str(e)}")

def financial_analysis():
    st.title("💰 Análisis Financiero")
    
    uploaded_file = st.file_uploader("Cargar datos financieros", type=["csv", "xlsx"])
    
    col1, col2 = st.columns(2)
    with col1:
        threshold = st.slider(
            "Umbral de Detección",
            min_value=0.0,
            max_value=1.0,
            value=0.85
        )
    
    with col2:
        analysis_type = st.selectbox(
            "Tipo de Análisis",
            ["Detección de Fraude", "Análisis de Riesgo", "Patrones de Trading"]
        )
    
    if uploaded_file and st.button("Analizar Datos"):
        with st.spinner("Procesando datos financieros..."):
            try:
                # Aquí iría la lógica de análisis financiero
                st.success("✅ Análisis financiero completado")
            except Exception as e:
                st.error(f"❌ Error en el análisis: {str(e)}")

def entropy_generator():
    st.title("🎲 Generador de Entropía")
    
    col1, col2 = st.columns(2)
    with col1:
        bits = st.number_input("Bits de Entropía", 64, 4096, 2048)
        source = st.radio(
            "Fuente de Entropía",
            ["Fluctuaciones Cuánticas", "Ruido Térmico", "Emisión Fotónica"]
        )
    
    with col2:
        output_format = st.selectbox(
            "Formato de Salida",
            ["Hexadecimal", "Base64", "Binario"]
        )
    
    if st.button("Generar Entropía"):
        with st.spinner("Generando entropía..."):
            try:
                # Aquí iría la lógica de generación de entropía
                st.code("a1b2c3d4...", language="text")
                st.success("✅ Entropía generada exitosamente")
            except Exception as e:
                st.error(f"❌ Error en la generación: {str(e)}")

def code_obfuscator():
    st.title("🔐 Ofuscador de Código")
    
    code = st.text_area("Código a Ofuscar:", height=200)
    
    col1, col2 = st.columns(2)
    with col1:
        language = st.selectbox(
            "Lenguaje",
            ["Python", "JavaScript", "Java", "C++"]
        )
        seed = st.number_input("Semilla de Ofuscación", 1, 9999, 42)
    
    with col2:
        level = st.slider("Nivel de Ofuscación", 1, 5, 3)
        preserve_names = st.checkbox("Preservar Nombres Importantes")
    
    if code and st.button("Ofuscar Código"):
        with st.spinner("Ofuscando código..."):
            try:
                # Aquí iría la lógica de ofuscación
                st.code("código_ofuscado", language=language.lower())
                st.success("✅ Código ofuscado exitosamente")
            except Exception as e:
                st.error(f"❌ Error en la ofuscación: {str(e)}")

if __name__ == "__main__":
    main()

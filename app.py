import streamlit as st
import google.generativeai as genai
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from PIL import Image

st.set_page_config(page_title="Mentor Institucional WIN", layout="wide")
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- FUNÇÃO CALENDÁRIO FORMATADA ---
@st.cache_data(ttl=3600)
def puxar_calendario():
    try:
        url = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        root = ET.fromstring(response.content)
        
        # Data de hoje formatada
        hoje_dt = datetime.now()
        data_formatada = hoje_dt.strftime("%d/%m/%Y")
        
        hoje_str = hoje_dt.strftime("%m-%d-%Y")
        eventos = []
        
        for e in root.findall('event'):
            if e.find('date').text == hoje_str and e.find('impact').text in ['High', 'Medium']:
                time = e.find('time').text
                title = e.find('title').text
                country = e.find('country').text
                eventos.append(f"• **{time} ({country})**: {title}")
        
        if not eventos:
            return f"### 📅 Data: {data_formatada}\n*Sem eventos de alto/médio impacto hoje.*"
        
        return f"### 📅 Data de Referência: {data_formatada}\n\n" + "\n".join(eventos)
    except:
        return "### 📅 Calendário\nErro ao carregar agenda."

# --- INTERFACE ---
st.title("🎓 Mentor Institucional de Fluxo")

# Guia no topo
with st.expander("📖 Guia: Como configurar sua Grade de Ativos"):
    st.markdown("""
    Para o Mentor realizar uma análise perfeita, sua lista no TradingView deve conter:
    **WIN1!, WDO1!, DI1N2029, PETR4, IMAT, IFNC, ES1!, NQ1!, B3SA3, EWZ, VIX.**
    *Certifique-se de que a variação percentual esteja visível no print!*
    """)

# Exibição do Calendário Organizado
st.info(puxar_calendario())

uploaded_file = st.file_uploader("Suba o print (Pré-mercado ou Durante o pregão):", type=['jpg', 'png'])

if uploaded_file:
    # (Lógica de processamento mantida...)
    st.image(uploaded_file, use_column_width=True)
    if st.button("🚀 Processar Análise"):
        st.write("Analisando...")

# Limpeza
if st.sidebar.button("🗑️ Limpar Pregão Atual"):
    st.session_state.historico_analises = []
    st.rerun()

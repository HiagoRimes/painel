import streamlit as st
import google.generativeai as genai
import yfinance as yf
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# Configuração da página - TEM QUE SER A PRIMEIRA LINHA
st.set_page_config(page_title="Mentor Institucional WIN", layout="wide")

# Configuração API
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-3.5-flash')

# Tickers para sua Grade
TICKERS_GRADE = {
    "WDO": "USDBRL=X",
    "PETR4": "PETR4.SA",
    "B3SA3": "B3SA3.SA",
    "ITUB4": "ITUB4.SA",
    "VALE3": "VALE3.SA",
    "EWZ": "EWZ",
    "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC",
    "VIX": "^VIX"
}

# --- BARRA LATERAL (Sidebar TEM QUE VIR ANTES DO TÍTULO) ---
with st.sidebar:
    st.title("📊 Grade de Cotações")
    
    if st.button("🔄 Atualizar Grade"):
        st.cache_data.clear()
        
    for nome, ticker in TICKERS_GRADE.items():
        try:
            dados = yf.Ticker(ticker).history(period="1d")
            atual = dados['Close'].iloc[-1]
            anterior = dados['Open'].iloc[0]
            var = ((atual - anterior) / anterior) * 100
            cor = "green" if var >= 0 else "red"
            st.markdown(f"{nome}: :{cor}[{var:.2f}%]")
        except:
            st.markdown(f"{nome}: Erro")

# --- ÁREA PRINCIPAL ---
st.title("🎓 Mentor de Fluxo Institucional")

if 'historico' not in st.session_state:
    st.session_state.historico = []

# Botão de análise
if st.button("🚀 Analisar Mercado"):
    # (Adicione aqui a lógica de análise que já estávamos usando)
    st.write("Análise realizada com sucesso...")

# Histórico
for analise in st.session_state.historico:
    st.write(analise)
    

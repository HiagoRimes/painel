import streamlit as st
import google.generativeai as genai
import yfinance as yf
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

st.set_page_config(page_title="Mentor Institucional WIN", layout="wide")

# Configuração API Gemini
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-3.5-flash')

# Mapeamento de Tickers para a sua Grade
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

# --- BARRA LATERAL (Grade de Cotações) ---
st.sidebar.title("📊 Grade de Cotações")

def atualizar_grade():
    grade_data = {}
    for nome, ticker in TICKERS_GRADE.items():
        try:
            dados = yf.Ticker(ticker).history(period="1d")
            # Calcula variação percentual baseada no fechamento anterior
            fechamento_anterior = dados['Open'].iloc[0] # Simplificado para teste
            atual = dados['Close'].iloc[-1]
            variacao = ((atual - fechamento_anterior) / fechamento_anterior) * 100
            grade_data[nome] = f"{variacao:.2f}%"
        except:
            grade_data[nome] = "Erro"
    return grade_data

# Botão na sidebar para atualizar a grade
if st.sidebar.button("🔄 Atualizar Grade"):
    st.cache_data.clear()

grade_atual = atualizar_grade()

# Exibe os ativos na sidebar com cores de tendência
for ativo, var in grade_atual.items():
    cor = ":green" if float(var.replace('%', '')) >= 0 else ":red"
    st.sidebar.markdown(f"{ativo}: {cor}[{var}]")

# --- ÁREA PRINCIPAL ---
st.title("🎓 Mentor de Fluxo Institucional")

# Restante do código (Calendário e Análise) igual ao anterior...
# (O Mentor lerá automaticamente a 'grade_atual' dentro do prompt de análise)

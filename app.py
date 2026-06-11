import streamlit as st
import google.generativeai as genai
import yfinance as yf
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

st.set_page_config(page_title="Mentor Institucional WIN", layout="wide")

# Inicializa memória
if 'historico_analises' not in st.session_state:
    st.session_state.historico_analises = []

# Configuração do Gemini
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-3.5-flash')

# 1. Calendário Econômico (Forex Factory)
@st.cache_data(ttl=3600)
def puxar_calendario():
    try:
        url = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        root = ET.fromstring(response.content)
        hoje = datetime.now().strftime("%m-%d-%Y")
        eventos = [f"• **{e.find('time').text} ({e.find('country').text})**: {e.find('title').text}" 
                   for e in root.findall('event') if e.find('date').text == hoje and e.find('impact').text in ['High', 'Medium']]
        return "\n".join(eventos) if eventos else "Sem eventos de impacto."
    except: return "Erro ao carregar calendário."

# 2. Dados de Mercado (YFinance - A solução para sua deficiência de dados)
def puxar_dados_mercado():
    # Símbolos no Yahoo Finance (WDO e DI geralmente exigem corretora, focamos nos motores externos)
    tickers = {
        "DXY": "DX-Y.NYB", 
        "PETR4": "PETR4.SA", 
        "VALE3": "VALE3.SA", 
        "VIX": "^VIX",
        "S&P500": "^GSPC"
    }
    dados_formatados = "DADOS DE MERCADO:\n"
    for nome, ticker in tickers.items():
        try:
            data = yf.Ticker(ticker).history(period="1d")
            preco = data['Close'].iloc[-1]
            dados_formatados += f"{nome}: {preco:.2f}\n"
        except:
            dados_formatados += f"{nome}: Indisponível\n"
    return dados_formatados

# Interface
st.title("🎓 Mentor Institucional (Dados Reais)")

if st.button("🔄 Analisar Mercado AGORA"):
    with st.spinner("Buscando dados globais e fluxo..."):
        agenda = puxar_calendario()
        mercado = puxar_dados_mercado()
        
        prompt = f"""
        Analise o ativo WIN.
        CALENDÁRIO: {agenda}
        MERCADO AGORA: {mercado}
        
        Você deve identificar:
        1. Divergências entre DXY e o mercado brasileiro.
        2. Se a Vale e Petrobras estão puxando o índice ou pressionando para baixo.
        3. A leitura de risco do VIX.
        """
        
        resposta = model.generate_content(prompt).text
        st.session_state.historico_analises.append(resposta)
        st.markdown(resposta)

# Exibe histórico
for analise in st.session_state.historico_analises:
    st.divider()
    st.write(analise)
        

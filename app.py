import streamlit as st
import google.generativeai as genai
import yfinance as yf
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Mentor Institucional WIN", layout="wide")

# Configuração API (Secrets)
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-3.5-flash')

# Tickers configurados para bater com o TradingView (Referência de abertura)
TICKERS_GRADE = {
    "WIN": "^BVSP",      # Proxy IBOV
    "WDO": "USDBRL=X",   # Dólar Comercial
    "PETR4": "PETR4.SA",
    "B3SA3": "B3SA3.SA",
    "ITUB4": "ITUB4.SA",
    "VALE3": "VALE3.SA",
    "EWZ": "EWZ",
    "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC",
    "VIX": "^VIX"
}

# --- BARRA LATERAL: Grade de Cotações ---
with st.sidebar:
    st.title("📊 Grade de Cotações")
    if st.button("🔄 Atualizar Grade"):
        st.cache_data.clear()
        
    for nome, ticker in TICKERS_GRADE.items():
        try:
            # Puxa o dado do dia com precisão de 1 minuto
            dados = yf.Ticker(ticker).history(period="1d", interval="1m")
            if not dados.empty:
                abertura = dados['Open'].iloc[0]
                atual = dados['Close'].iloc[-1]
                var = ((atual - abertura) / abertura) * 100
                cor = "green" if var >= 0 else "red"
                st.markdown(f"{nome}: :{cor}[{var:.2f}%]")
            else:
                st.markdown(f"{nome}: Aguardando...")
        except:
            st.markdown(f"{nome}: Erro")

# --- LÓGICA DE DADOS (CALENDÁRIO + CARTEIRA) ---
@st.cache_data(ttl=3600)
def puxar_calendario():
    try:
        url = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        root = ET.fromstring(response.content)
        hoje = datetime.now().strftime("%m-%d-%Y")
        eventos = [f"• **{e.find('time').text} ({e.find('country').text})**: {e.find('title').text}" 
                   for e in root.findall('event') if e.find('date').text == hoje and e.find('impact').text in ['High', 'Medium']]
        return "\n".join(eventos) if eventos else "Sem eventos de alto impacto."
    except: return "Erro ao carregar calendário."

# --- ÁREA PRINCIPAL ---
st.title("🎓 Mentor de Fluxo Institucional")

if 'historico' not in st.session_state:
    st.session_state.historico = []

# Botão de Análise de Fluxo
if st.button("🚀 Analisar Mercado (IA)"):
    with st.spinner("Analisando fluxo e correlações..."):
        agenda = puxar_calendario()
        # Captura os dados da grade para passar ao Gemini
        prompt = f"""
        Você é um mentor institucional. Analise o fluxo do WIN baseado nestes dados:
        CALENDÁRIO: {agenda}
        GRADE DE MOTORES: {TICKERS_GRADE}
        
        Siga o protocolo:
        1. Avalie a variação dos ativos na grade.
        2. Identifique divergências entre o S&P/NASDAQ e o IBOV.
        3. Determine a direção do fluxo e o ponto de atenção atual.
        """
        resposta = model.generate_content(prompt).text
        st.session_state.historico.append(resposta)
        st.markdown("### 📊 Parecer")
        st.write(resposta)

# Histórico Lateral
if st.session_state.historico:
    with st.sidebar.expander("📜 Histórico de Leituras"):
        for analise in st.session_state.historico:
            st.write(analise)
            st.divider()
    

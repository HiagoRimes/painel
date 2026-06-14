import streamlit as st
import google.generativeai as genai
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from PIL import Image
# Configuração da Página
st.set_page_config(page_title="Mentor Institucional WIN", layout="wide")
# --- TRAVA DE SEGURANÇA ---
SENHA_ACESSO = "aprender" 
def check_password():
    password = st.text_input("🔑 Digite a senha para liberar seu estudo:", type="password")
    if password == SENHA_ACESSO:
        return True
    elif password != "":
        st.error("Senha incorreta. Tente novamente.")
        return False
    else:
        return False
# --- CONFIGURAÇÃO API ---
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
def get_model():
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    prioridade = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro']
    for p in prioridade:
        if p in models: return genai.GenerativeModel(p)
    return genai.GenerativeModel(models[0])
model = get_model()
# --- LÓGICA PRINCIPAL ---
if check_password():
    
    # Gerenciamento de Memória
    if 'historico_data' not in st.session_state: st.session_state.historico_data = datetime.now().date()
    if 'historico_analises' not in st.session_state: st.session_state.historico_analises = []
    if st.session_state.historico_data != datetime.now().date():
        st.session_state.historico_analises = []
        st.session_state.historico_data = datetime.now().date()
    
    PROMPT_SISTEMA = """
    Você é um Estrategista de Mesa de Operações e um Mestre em Educação Financeira. 
    Sua missão é realizar a leitura institucional do WIN, priorizando o aprendizado do usuário.
    Protocolo: (Contexto, Motores, Carteira, Fluxo, Estado Final, Modo Professor Didático).
    REGRAS: WIN é consequência. Fluxo real sempre vence.
    HISTÓRICO DO PREGÃO: {historico}
    """
    
    @st.cache_data(ttl=3600)
    def puxar_calendario():
        try:
            url = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            root = ET.fromstring(response.content)
            hoje_dt = datetime.now()
            eventos = [f"• {e.find('time').text} ({e.find('country').text}): {e.find('title').text}" 
                       for e in root.findall('event') if e.find('date').text == hoje_dt.strftime("%m-%d-%Y") and e.find('impact').text in ['High', 'Medium']]
            return f"### 📅 Agenda: {hoje_dt.strftime('%d/%m/%Y')}\n\n" + "\n".join(eventos) if eventos else "Sem eventos."
        except: return "### 📅 Calendário indisponível."
    
    st.title("🎓 Mentor Institucional de Fluxo")
    
    with st.expander("📖 Guia: Como configurar sua Grade de Ativos (LEIA ANTES DE SUBIR O PRINT)"):
        st.markdown("""
        PASSO A PASSO:
        1. Crie uma nova lista (carteira) no seu TradingView.
        2. Adicione os ativos abaixo em um único print de sua grade completa.
        

| Ativo | Função |
| :--- | :--- |
| [WIN1!](https://br.tradingview.com/symbols/BMFBOVESPA-WIN1!/) | Índice Futuro |
| [WDO1!](https://br.tradingview.com/symbols/BMFBOVESPA-WDO1!/) | Dólar |
| [DI1N2029](https://br.tradingview.com/symbols/BMFBOVESPA-DI11!/?contract=DI1N2029) | Juros |
| [PETR4](https://br.tradingview.com/symbols/BMFBOVESPA-PETR4/) | Commodities |
| [IMAT](https://br.tradingview.com/symbols/BMFBOVESPA-IMAT/) | Materiais |
| [IFNC](https://br.tradingview.com/symbols/BMFBOVESPA-IFNC/) | Bancos |
| [ES1!](https://br.tradingview.com/symbols/CME_MINI-ES1!/) | S&P 500 |
| [NQ1!](https://br.tradingview.com/symbols/CME_MINI-NQ1!/) | Nasdaq |
| [B3SA3](https://br.tradingview.com/symbols/BMFBOVESPA-B3SA3/) | B3 |
| [EWZ](https://br.tradingview.com/symbols/AMEX-EWZ/) | ETF Brasil |
| [VIX](https://br.tradingview.com/symbols/TVC-VIX/) | Volatilidade |

""")
    
    st.info(puxar_calendario())
    
    uploaded_file = st.file_uploader("Suba o print:", type=['jpg', 'png'])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, use_column_width=True)
        
        if st.button("🚀 Processar Análise Evolutiva"):
            with st.spinner("Conectando variáveis macro..."):
                hist_texto = "\n".join(st.session_state.historico_analises)
                full_prompt = PROMPT_SISTEMA.format(historico=hist_texto) + f"\nAGENDA: {puxar_calendario()}"
                
                try:
                    response = model.generate_content([full_prompt, image])
                    st.markdown("### 📊 Relatório Institucional")
                    st.markdown(response.text)
                    st.session_state.historico_analises.append(response.text)
                except Exception as e:
                    st.error(f"Erro: {e}")
    
    if st.sidebar.button("🗑️ Limpar Pregão Atual"):
        st.session_state.historico_analises = []
        st.rerun()

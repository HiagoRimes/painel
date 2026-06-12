import streamlit as st
import google.generativeai as genai
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from PIL import Image
# Configuração da Página
st.set_page_config(page_title="Mentor Institucional WIN", layout="wide")
# Configuração da API
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
# --- TRAVA DE SEGURANÇA ---
SENHA_ACESSO = "aprender" 
def check_password():
    password = st.text_input("🔑 Digite a senha para liberar seu estudo:", type="password")
    if password == SENHA_ACESSO:
        return True
    elif password != "":
        st.error("Senha incorreta.")
        return False
    return False
# --- FUNÇÃO DE PROCESSAMENTO COM FAILOVER ---
def analisar_com_failover(prompt, image):
    modelos_tentativa = ['gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-1.5-flash-8b']
    
    for nome_modelo in modelos_tentativa:
        try:
            with st.status(f"Consultando {nome_modelo}...", expanded=True) as status:
                model = genai.GenerativeModel(nome_modelo)
                response = model.generate_content([prompt, image], request_options={"timeout": 15})
                status.update(label=f"✅ Análise concluída via {nome_modelo}", state="complete")
                return f"### 📊 Relatório Institucional ({nome_modelo})\n\n{response.text}"
        except Exception as e:
            st.warning(f"O modelo {nome_modelo} falhou. Tentando o próximo...")
            continue
            
    return "❌ Todos os modelos Gemini estão indisponíveis no momento."
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
            eventos = [f"• **{e.find('time').text} ({e.find('country').text})**: {e.find('title').text}" 
                       for e in root.findall('event') if e.find('date').text == hoje_dt.strftime("%m-%d-%Y") and e.find('impact').text in ['High', 'Medium']]
            return f"### 📅 Agenda: {hoje_dt.strftime('%d/%m/%Y')}\n\n" + "\n".join(eventos) if eventos else "Sem eventos."
        except: return "### 📅 Calendário indisponível."
    st.title("🎓 Mentor Institucional de Fluxo")
    with st.expander("📖 Guia: Como configurar sua Grade de Ativos (LEIA ANTES DE SUBIR O PRINT)"):
        st.markdown("""
        **PASSO A PASSO:**
        1. Crie uma **nova lista (carteira)** no seu TradingView.
        2. Adicione todos os ativos abaixo nesta **mesma lista**.
        3. **IMPORTANTE:** O Mentor só analisa a correlação se você enviar **um único print** com todos os ativos juntos.
        

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
    uploaded_file = st.file_uploader("Suba o print (único):", type=['jpg', 'png'])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, use_column_width=True)
        
        if st.button("🚀 Processar Análise Evolutiva"):
            hist_texto = "\n".join(st.session_state.historico_analises)
            full_prompt = PROMPT_SISTEMA.format(historico=hist_texto) + f"\nAGENDA: {puxar_calendario()}"
            
            resultado = analisar_com_failover(full_prompt, image)
            st.markdown(resultado)
            
            if "✅" in resultado:
                st.session_state.historico_analises.append(resultado)
    if st.sidebar.button("🗑️ Limpar Pregão Atual"):
        st.session_state.historico_analises = []
        st.rerun()

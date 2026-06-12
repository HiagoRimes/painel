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
def get_model():
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    prioridade = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro']
    for p in prioridade:
        if p in models: return genai.GenerativeModel(p)
    return genai.GenerativeModel(models[0])
model = get_model()
# Gerenciamento de Memória (Auto-limpeza por dia)
if 'historico_data' not in st.session_state: st.session_state.historico_data = datetime.now().date()
if 'historico_analises' not in st.session_state: st.session_state.historico_analises = []
if st.session_state.historico_data != datetime.now().date():
    st.session_state.historico_analises = []
    st.session_state.historico_data = datetime.now().date()
# Protocolo Didático-Institucional
PROMPT_SISTEMA = """
Você é um Estrategista de Mesa de Operações e um Mestre em Educação Financeira. 
Sua missão é realizar a leitura institucional do WIN, priorizando o aprendizado do usuário.
Protocolo de Análise:
1. CONTEXTO DO DIA: Resuma a agenda e o clima macro de forma simples.
2. ESTADO DOS MOTORES: Avalie DI, WDO, S&P, Nasdaq, VIX, IFNC e IMAT.
3. CARTEIRA: Analise a correlação da carteira com o WIN.
4. TRANSMISSÃO DE FLUXO: Identifique quem está comandando o mercado (Exterior/Macro/Interno).
5. ESTADO FINAL DO MERCADO: Defina a direção provável do WIN e a justificativa técnica.
6. MODO PROFESSOR (DIDÁTICO):
   - Explique o raciocínio por trás desta análise como um tutor faria.
   - Defina qualquer termo técnico utilizado (ex: 'Absorção', 'Exaustão').
   - Indique o 'erro de iniciante' mais comum neste cenário.
   - Deixe uma lição prática baseada na correlação observada hoje.
REGRAS: O WIN é sempre a consequência. Se houver divergência entre agenda e preço, o preço (fluxo real) sempre vence.
HISTÓRICO DO PREGÃO: {historico}
"""
@st.cache_data(ttl=3600)
def puxar_calendario():
    try:
        url = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        root = ET.fromstring(response.content)
        hoje_dt = datetime.now()
        data_formatada = hoje_dt.strftime("%d/%m/%Y")
        hoje_str = hoje_dt.strftime("%m-%d-%Y")
        eventos = [f"• **{e.find('time').text} ({e.find('country').text})**: {e.find('title').text}" 
                   for e in root.findall('event') if e.find('date').text == hoje_str and e.find('impact').text in ['High', 'Medium']]
        if not eventos:
            return f"### 📅 Data: {data_formatada}\n*Sem eventos de impacto relevante hoje.*"
        return f"### 📅 Agenda Econômica: {data_formatada}\n\n" + "\n".join(eventos)
    except:
        return "### 📅 Calendário\nErro ao carregar dados."
# --- INTERFACE ---
st.title("🎓 Mentor Institucional de Fluxo")
# Guia de Configuração Interativa
with st.expander("📖 Guia: Como configurar sua Grade de Ativos (Clique aqui)"):
    st.markdown("""

| Ativo | Função no Fluxo | Link (TradingView) |
| :--- | :--- | :--- |
| **[WIN1!](https://br.tradingview.com/symbols/BMFBOVESPA-WIN1/)** | Índice Futuro (O objeto da análise) | [Abrir](https://br.tradingview.com/symbols/BMFBOVESPA-WIN1/) |
| **[WDO1!](https://br.tradingview.com/symbols/BMFBOVESPA-WDO1/)** | Dólar (Motor macro/câmbio) | [Abrir](https://br.tradingview.com/symbols/BMFBOVESPA-WDO1/) |
| **[DI1N2029](https://br.tradingview.com/symbols/BMFBOVESPA-DI11!/?contract=DI1N2029)** | Juros Futuros (Motor de longo prazo) | [Abrir](https://br.tradingview.com/symbols/BMFBOVESPA-DI11!/?contract=DI1N2029) |
| **[PETR4](https://br.tradingview.com/symbols/BMFBOVESPA-PETR4/)** | Commodities (Líder da bolsa BR) | [Abrir](https://br.tradingview.com/symbols/BMFBOVESPA-PETR4/) |
| **[IMAT](https://br.tradingview.com/symbols/BMFBOVESPA-IMAT/)** | Materiais Básicos (Força industrial) | [Abrir](https://br.tradingview.com/symbols/BMFBOVESPA-IMAT/) |
| **[IFNC](https://br.tradingview.com/symbols/BMFBOVESPA-IFNC/)** | Setor Financeiro (Bancos) | [Abrir](https://br.tradingview.com/symbols/BMFBOVESPA-IFNC/) |
| **[ES1!](https://br.tradingview.com/symbols/CME_MINI-ES1/)** | S&P 500 (Sentimento global) | [Abrir](https://br.tradingview.com/symbols/CME_MINI-ES1/) |
| **[NQ1!](https://br.tradingview.com/symbols/CME_MINI-NQ1!/)** | Nasdaq (Tecnologia/Risco) | [Abrir](https://br.tradingview.com/symbols/CME_MINI-NQ1!/) |
| **[B3SA3](https://br.tradingview.com/symbols/BMFBOVESPA-B3SA3/)** | B3 (Termômetro da bolsa) | [Abrir](https://br.tradingview.com/symbols/BMFBOVESPA-B3SA3/) |
| **[EWZ](https://br.tradingview.com/symbols/AMEX-EWZ/)** | ETF Brasil (Sentimento estrangeiro) | [Abrir](https://br.tradingview.com/symbols/AMEX-EWZ/) |
| **[VIX](https://br.tradingview.com/symbols/TVC-VIX/)** | Índice de Volatilidade (O "medo") | [Abrir](https://br.tradingview.com/symbols/TVC-VIX/) |

    """)
    st.markdown("*Dica: Certifique-se de que a variação percentual (%) esteja visível no print!*")
st.info(puxar_calendario())
uploaded_file = st.file_uploader("Suba o print (Pré-mercado ou Durante o pregão):", type=['jpg', 'png'])
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, use_column_width=True)
    
    if st.button("🚀 Processar Análise Evolutiva"):
        with st.spinner("Conectando variáveis macro e histórico do dia..."):
            hist_texto = "\n".join(st.session_state.historico_analises)
            full_prompt = PROMPT_SISTEMA.format(historico=hist_texto) + f"\nAGENDA DO DIA: {puxar_calendario()}"
            
            try:
                response = model.generate_content([full_prompt, image])
                st.markdown("### 📊 Relatório Institucional")
                st.markdown(response.text)
                st.session_state.historico_analises.append(response.text)
            except Exception as e:
                st.error(f"Erro na análise: {e}")
if st.sidebar.button("🗑️ Limpar Pregão Atual"):
    st.session_state.historico_analises = []
    st.rerun()

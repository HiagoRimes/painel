import streamlit as st
import google.generativeai as genai
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from PIL import Image

st.set_page_config(page_title="Mentor Institucional WIN", layout="wide")
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

def get_model():
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    prioridade = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro']
    for p in prioridade:
        if p in models: return genai.GenerativeModel(p)
    return genai.GenerativeModel(models[0])

model = get_model()

# Gerenciamento de Memória
if 'historico_data' not in st.session_state: st.session_state.historico_data = datetime.now().date()
if 'historico_analises' not in st.session_state: st.session_state.historico_analises = []

if st.session_state.historico_data != datetime.now().date():
    st.session_state.historico_analises = []
    st.session_state.historico_data = datetime.now().date()

# Protocolo Evolutivo
PROMPT_SISTEMA = """
Você é um Estrategista de Mesa de Operações. Seu foco é a correlação entre Macro, Geopolítica, Notícias e o Fluxo do WIN.
Protocolo de Análise:
1. MODO PRÉ-MERCADO: Se for antes das 09:00, compare o fechamento do dia anterior (do print) com o cenário externo atual para projetar a abertura.
2. ANÁLISE EVOLUTIVA: Considere as análises anteriores deste pregão. O fluxo está mantendo a tendência ou há mudança de dominância?
3. SÍNTESE INSTITUCIONAL: Siga os 6 blocos (Contexto, Motores, Carteira, Fluxo, Estado Final, Modo Professor).
4. REGRAS: WIN é consequência. Se os dados da agenda e os do print divergirem, a prioridade é o fluxo real (absorção/exaustão).

HISTÓRICO DO DIA: {historico}
"""

@st.cache_data(ttl=3600)
def puxar_calendario():
    try:
        url = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        root = ET.fromstring(response.content)
        hoje = datetime.now().strftime("%m-%d-%Y")
        eventos = [f"• {e.find('time').text}: {e.find('title').text}" for e in root.findall('event') if e.find('date').text == hoje]
        return "\n".join(eventos) if eventos else "Sem eventos."
    except: return "Calendário indisponível."

# Interface
st.title("🎓 Mentor Institucional de Fluxo")

# --- GUIA NO TOPO ---
with st.expander("📖 Guia: Como configurar sua Grade de Ativos"):
    st.markdown("""
    Para o Mentor realizar uma análise perfeita, sua lista no TradingView deve conter estes ativos:
    **WIN1!, WDO1!, DI1N2029, PETR4, IMAT, IFNC, ES1!, NQ1!, B3SA3, EWZ, VIX.**
    *Certifique-se de que a variação percentual esteja visível no print enviado!*
    """)

st.info(f"**Agenda Econômica:**\n{puxar_calendario()}")

uploaded_file = st.file_uploader("Suba o print (Pré-mercado ou Durante o pregão):", type=['jpg', 'png'])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, use_column_width=True)
    
    if st.button("🚀 Processar Análise Evolutiva"):
        with st.spinner("Conectando variáveis macro e histórico do dia..."):
            hist_texto = "\n".join(st.session_state.historico_analises)
            full_prompt = PROMPT_SISTEMA.format(historico=hist_texto) + f"\nAGENDA: {puxar_calendario()}"
            
            try:
                response = model.generate_content([full_prompt, image])
                st.markdown("### 📊 Resultado da Análise")
                st.markdown(response.text)
                st.session_state.historico_analises.append(response.text)
            except Exception as e:
                st.error(f"Erro: {e}")

if st.sidebar.button("🗑️ Limpar Pregão Atual"):
    st.session_state.historico_analises = []
    st.rerun()
    

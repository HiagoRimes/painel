import streamlit as st
import google.generativeai as genai
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from PIL import Image

# Configuração da página
st.set_page_config(page_title="Mentor Institucional WIN", layout="wide")

# Configuração da API
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Detecção Automática de Modelo
def get_model():
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    prioridade = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']
    for p in prioridade:
        if p in models: return genai.GenerativeModel(p)
    return genai.GenerativeModel(models[0])

try:
    model = get_model()
except Exception as e:
    st.error(f"Erro ao carregar modelo: {e}")

# Função Calendário
@st.cache_data(ttl=3600)
def puxar_calendario():
    try:
        url = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        root = ET.fromstring(response.content)
        traducao = {
            "Non-Farm Employment Change": "Payroll", "Unemployment Rate": "Taxa de Desemprego",
            "Consumer Price Index (CPI)": "IPCA/CPI", "Federal Funds Rate": "Juros Fed",
            "GDP": "PIB", "Retail Sales": "Vendas Varejo", "Manufacturing PMI": "PMI Ind"
        }
        hoje = datetime.now().strftime("%m-%d-%Y")
        eventos = [f"• **{e.find('time').text} ({e.find('country').text})**: {traducao.get(e.find('title').text, e.find('title').text)}"
                   for e in root.findall('event') if e.find('date').text == hoje and e.find('impact').text in ['High', 'Medium']]
        return "\n".join(eventos) if eventos else "Sem eventos de impacto hoje."
    except: return "Calendário indisponível."

# Protocolo do Sistema
PROMPT_SISTEMA = """
Você é um Analista de Fluxo Institucional Sênior. Analise o print da grade de ativos e a agenda fornecida seguindo estritamente este protocolo:

1. CONTEXTO DO DIA: Analise a agenda e classifique o impacto (Alta/Média/Baixa). Resuma o clima macro.
2. ESTADO DOS MOTORES: Avalie DI, WDO, S&P, Nasdaq, VIX, IFNC e IMAT (Direção/Força/Influência).
3. CARTEIRA: Analise a correlação dos ativos do print com o WIN. Defina se estão alinhados ou em conflito.
4. TRANSMISSÃO DE FLUXO: Identifique quem está comandando o mercado (Exterior/Macro/Interno/Cabo de Guerra).
5. ESTADO FINAL DO MERCADO: Defina Compra/Venda/Neutro. Dê a direção provável do WIN com justificativa técnica.
6. MODO PROFESSOR: Explique o mecanismo de correlação, um erro comum de leitura e uma regra prática para o dia.

REGRAS: WIN é consequência. Cruzar dados de todos os blocos. Ser objetivo e scannable.
"""

# Interface
st.title("🎓 Mentor de Fluxo Institucional")
st.info(f"**Agenda Econômica:**\n{puxar_calendario()}")

uploaded_file = st.file_uploader("Suba o print do Profit/TradingView:", type=['jpg', 'jpeg', 'png'])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Cenário de Mercado", use_column_width=True)
    
    if st.button("🚀 Analisar Fluxo Agora"):
        with st.spinner("O Mentor está processando a leitura institucional..."):
            try:
                full_prompt = f"{PROMPT_SISTEMA}\n\nAGENDA MACRO PARA ANÁLISE:\n{puxar_calendario()}"
                response = model.generate_content([full_prompt, image])
                st.markdown("---")
                st.markdown(response.text)
                if 'historico' not in st.session_state: st.session_state.historico = []
                st.session_state.historico.append(response.text)
            except Exception as e:
                st.error(f"Erro na análise: {e}")

if st.sidebar.button("🗑️ Limpar Sessão"):
    st.session_state.historico = []
    st.rerun()

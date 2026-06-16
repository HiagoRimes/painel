import streamlit as st
import google.generativeai as genai
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from PIL import Image

# ---------------------------
# CONFIGURAÇÃO DA PÁGINA
# ---------------------------
st.set_page_config(page_title="Mentor Institucional WIN", layout="wide")

# ---------------------------
# TRAVA DE SEGURANÇA
# ---------------------------
SENHA_ACESSO = "aprender"

def check_password():
    password = st.text_input("🔑 Digite a senha para liberar seu estudo:", type="password")
    if password == SENHA_ACESSO:
        return True
    elif password != "":
        st.error("Senha incorreta. Tente novamente.")
        return False
    return False

# ---------------------------
# CONFIGURAÇÃO API GEMINI
# ---------------------------
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

def get_model():
    try:
        models = [
            m.name for m in genai.list_models()
            if "generateContent" in m.supported_generation_methods
        ]

        prioridade = [
            "models/gemini-2.5-flash",
            "models/gemini-2.5-pro",
            "models/gemini-1.5-flash",
            "models/gemini-1.5-pro",
        ]

        for p in prioridade:
            if p in models:
                return genai.GenerativeModel(p)

        return genai.GenerativeModel(models[0])

    except Exception:
        return genai.GenerativeModel("models/gemini-1.5-flash")


model = get_model()

# ---------------------------
# CONTROLE DE SESSÃO
# ---------------------------
if "historico_data" not in st.session_state:
    st.session_state.historico_data = datetime.now().date()

if "historico_analises" not in st.session_state:
    st.session_state.historico_analises = []

if st.session_state.historico_data != datetime.now().date():
    st.session_state.historico_analises = []
    st.session_state.historico_data = datetime.now().date()

# ---------------------------
# PROMPT BASE
# ---------------------------
PROMPT_SISTEMA = """
Você é um Estrategista de Mesa de Operações e um Mestre em Educação Financeira.
Sua missão é realizar a leitura institucional do WIN, priorizando aprendizado.

Protocolo:
Contexto, Motores, Carteira, Fluxo, Estado Final, Modo Professor Didático.

Regras:
- WIN é consequência
- Fluxo real sempre vence

Histórico do pregão:
{historico}
"""

# ---------------------------
# CALENDÁRIO ECONÔMICO
# ---------------------------
@st.cache_data(ttl=3600)
def puxar_calendario():
    try:
        url = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)

        root = ET.fromstring(response.content)
        hoje_dt = datetime.now()

        eventos = [
            f"• {e.find('time').text} ({e.find('country').text}): {e.find('title').text}"
            for e in root.findall('event')
            if e.find('date').text == hoje_dt.strftime("%m-%d-%Y")
            and e.find('impact').text in ["High", "Medium"]
        ]

        if eventos:
            return "### 📅 Agenda: " + hoje_dt.strftime("%d/%m/%Y") + "\n\n" + "\n".join(eventos)

        return "### 📅 Agenda: Sem eventos relevantes hoje."

    except Exception:
        return "### 📅 Calendário indisponível."

# ---------------------------
# INTERFACE
# ---------------------------
st.title("🎓 Mentor Institucional de Fluxo")

with st.expander("📖 Guia de configuração da grade"):
    st.markdown("""
1. Monte sua lista no TradingView  
2. Adicione os ativos institucionais  
3. Capture um único print da grade completa  

Ativos:
- WIN1!, WDO1!, DI1N2029
- PETR4, IMAT, IFNC
- ES1!, NQ1!, B3SA3, EWZ, VIX
""")

st.info(puxar_calendario())

uploaded_file = st.file_uploader("Suba o print:", type=["jpg", "png"])

# ---------------------------
# EXECUÇÃO IA
# ---------------------------
if check_password():

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)

        if st.button("🚀 Processar Análise Evolutiva"):

            with st.spinner("Conectando variáveis macro..."):

                historico = "\n".join(st.session_state.historico_analises)

                full_prompt = (
                    PROMPT_SISTEMA.format(historico=historico)
                    + "\n\nAGENDA:\n"
                    + puxar_calendario()
                )

                try:
                    response = model.generate_content([full_prompt, image])

                    st.markdown("### 📊 Relatório Institucional")
                    st.markdown(response.text)

                    st.session_state.historico_analises.append(response.text)

                except Exception as e:
                    st.error(f"Erro na análise: {str(e)}")

    # ---------------------------
    # LIMPAR SESSÃO
    # ---------------------------
    if st.sidebar.button("🗑️ Limpar Pregão Atual"):
        st.session_state.historico_analises = []
        st.rerun()

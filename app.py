import streamlit as st
import google.generativeai as genai
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from PIL import Image

# ---------------------------
# CONFIGURAÇÃO STREAMLIT
# ---------------------------
st.set_page_config(page_title="Mentor Institucional WIN", layout="wide")
st.set_option('client.toolbarMode', 'minimal')

# ---------------------------
# SEGURANÇA
# ---------------------------
SENHA_ACESSO = "aprender"

def check_password():
    password = st.text_input("🔑 Digite a senha para liberar seu estudo:", type="password")

    if password == SENHA_ACESSO:
        return True

    if password != "":
        st.error("Senha incorreta.")
    return False

# ---------------------------
# GEMINI API
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
# SESSION STATE
# ---------------------------
if "historico_analises" not in st.session_state:
    st.session_state.historico_analises = []

if "historico_data" not in st.session_state:
    st.session_state.historico_data = datetime.now().date()

if st.session_state.historico_data != datetime.now().date():
    st.session_state.historico_analises = []
    st.session_state.historico_data = datetime.now().date()

# ---------------------------
# PROMPT
# ---------------------------
PROMPT_SISTEMA = """
Você é um Estrategista de Mesa de Operações e Educador Financeiro.
Faça leitura institucional do WIN.

Estrutura:
Contexto, Motores, Carteira, Fluxo, Estado Final, Modo Professor.

Regra:
WIN é consequência do fluxo.

Histórico:
{historico}
"""

# ---------------------------
# CALENDÁRIO
# ---------------------------
@st.cache_data(ttl=3600)
def puxar_calendario():
    try:
        url = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)

        root = ET.fromstring(response.content)
        hoje = datetime.now()

        eventos = []

        for e in root.findall("event"):
            if e.find("date").text == hoje.strftime("%m-%d-%Y"):
                if e.find("impact").text in ["High", "Medium"]:
                    eventos.append(
                        f"• {e.find('time').text} ({e.find('country').text}): {e.find('title').text}"
                    )

        if eventos:
            return "### 📅 Agenda\n\n" + "\n".join(eventos)

        return "### 📅 Agenda: sem eventos relevantes hoje."

    except:
        return "### 📅 Calendário indisponível"

# ---------------------------
# UI
# ---------------------------
st.title("🎓 Mentor Institucional WIN")

with st.expander("📖 Guia"):
    st.markdown("""
Monte sua grade no TradingView e envie um print único contendo:

- WIN1!, WDO1!, DI1N2029
- PETR4, IMAT, IFNC
- ES1!, NQ1!, VIX
""")

st.info(puxar_calendario())

# ---------------------------
# AUTENTICAÇÃO
# ---------------------------
if not check_password():
    st.stop()

# ---------------------------
# UPLOAD + FLUXO SEGURO
# ---------------------------
uploaded_file = st.file_uploader("Suba o print:", type=["jpg", "png"])

if uploaded_file is not None:

    image = Image.open(uploaded_file)
    st.image(image, use_container_width=True)

    processar = st.button("🚀 Processar Análise")

    if processar:

        with st.spinner("Processando leitura institucional..."):

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
                st.error(f"Erro na análise: {e}")

# ---------------------------
# LIMPEZA SEGURA
# ---------------------------
if st.sidebar.button("🗑️ Limpar histórico"):
    st.session_state.historico_analises = []
    st.success("Histórico limpo.")

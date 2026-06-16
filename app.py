import streamlit as st
import google.generativeai as genai
import requests
from datetime import datetime
from PIL import Image

# ---------------------------
# CONFIG STREAMLIT
# ---------------------------
st.set_page_config(page_title="Mentor Institucional WIN", layout="wide")
st.set_option('client.toolbarMode', 'minimal')

# ---------------------------
# LOGIN
# ---------------------------
SENHA_ACESSO = "aprender"

def check_password():
    password = st.text_input("🔑 Senha:", type="password")

    if password == SENHA_ACESSO:
        return True

    if password != "":
        st.error("Senha incorreta")

    return False

# ---------------------------
# GEMINI
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

    except:
        return genai.GenerativeModel("models/gemini-1.5-flash")

model = get_model()

# ---------------------------
# SESSION STATE
# ---------------------------
if "historico" not in st.session_state:
    st.session_state.historico = []

# ---------------------------
# CALENDÁRIO REAL (TRADING ECONOMICS)
# ---------------------------
def puxar_calendario():
    try:
        url = "https://api.tradingeconomics.com/calendar?c=guest:guest"
        r = requests.get(url, timeout=10)
        data = r.json()

        hoje = datetime.now().date()
        eventos = []

        for e in data:
            try:
                data_evento = e.get("Date", "")[:10]
                pais = e.get("Country", "")
                evento = e.get("Event", "")
                impacto = e.get("Importance", "")

                # filtros institucionais
                if data_evento == str(hoje):
                    if impacto in ["2", "3"]:
                        if pais in ["United States", "Brazil"]:
                            eventos.append(f"• {pais}: {evento}")

            except:
                continue

        if eventos:
            return "### 📅 Macro real (automático)\n\n" + "\n".join(eventos)

        return "### 📅 Macro real: sem eventos relevantes hoje"

    except:
        return "### 📅 Calendário indisponível"

# ---------------------------
# PROMPT
# ---------------------------
PROMPT = """
Você é um Estrategista Institucional de Mesa.

Analise o WIN com base em:
- fluxo institucional
- correlação macro
- impacto dos eventos do dia

Histórico:
{historico}
"""

# ---------------------------
# UI
# ---------------------------
st.title("🎓 Mentor Institucional WIN")

st.info(puxar_calendario())

if not check_password():
    st.stop()

uploaded_file = st.file_uploader("Suba o print:", type=["jpg", "png"])

if uploaded_file:

    image = Image.open(uploaded_file)
    st.image(image, use_container_width=True)

    if st.button("🚀 Analisar fluxo"):

        with st.spinner("Processando..."):

            historico = "\n".join(st.session_state.historico)

            prompt = PROMPT.format(historico=historico)

            try:
                response = model.generate_content([prompt, image])

                st.markdown("### 📊 Resultado")
                st.markdown(response.text)

                st.session_state.historico.append(response.text)

            except Exception as e:
                st.error(f"Erro: {e}")

# ---------------------------
# LIMPAR
# ---------------------------
if st.sidebar.button("🗑️ Limpar histórico"):
    st.session_state.historico = []
    st.success("Limpo")

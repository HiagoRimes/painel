import streamlit as st
import google.generativeai as genai
from datetime import datetime
from PIL import Image

# ---------------------------
# CONFIG STREAMLIT
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

Regra central:
WIN é consequência do fluxo institucional.

Histórico:
{historico}
"""

# ---------------------------
# CALENDÁRIO PRÓPRIO (SEM API)
# ---------------------------
def puxar_calendario():
    hoje = datetime.now()

    eventos = [
        "🇧🇷 COPOM - Decisão de Juros",
        "🇧🇷 IPCA - Inflação Brasil",
        "🇧🇷 PIB Brasil",
        "🇺🇸 FOMC - Juros EUA",
        "🇺🇸 CPI - Inflação EUA",
        "🇺🇸 NFP - Payroll EUA",
        "🇺🇸 PCE - Inflação EUA",
        "🌍 VIX - Volatilidade Global",
        "🌍 DXY - Índice do Dólar"
    ]

    return (
        f"### 📅 Calendário institucional (WIN)\n\n"
        + "\n".join(f"• {e}" for e in eventos)
    )

# ---------------------------
# UI
# ---------------------------
st.title("🎓 Mentor Institucional WIN")

with st.expander("📖 Guia de uso"):
    st.markdown("""
Monte sua grade no TradingView com:

- WIN1!, WDO1!, DI1N2029  
- PETR4, IMAT, IFNC  
- ES1!, NQ1!, VIX  

Envie um print único da grade completa.
""")

st.info(puxar_calendario())

# ---------------------------
# LOGIN
# ---------------------------
if not check_password():
    st.stop()

# ---------------------------
# UPLOAD
# ---------------------------
uploaded_file = st.file_uploader("Suba o print:", type=["jpg", "png"])

if uploaded_file is not None:

    image = Image.open(uploaded_file)
    st.image(image, use_container_width=True)

    processar = st.button("🚀 Processar Análise")

    if processar:

        with st.spinner("Analisando fluxo institucional..."):

            historico = "\n".join(st.session_state.historico_analises)

            full_prompt = (
                PROMPT_SISTEMA.format(historico=historico)
                + "\n\nAGENDA MACRO:\n"
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
# LIMPAR HISTÓRICO
# ---------------------------
if st.sidebar.button("🗑️ Limpar histórico"):
    st.session_state.historico_analises = []
    st.success("Histórico limpo.")

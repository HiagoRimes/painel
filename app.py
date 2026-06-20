import streamlit as st
import requests
import json
from datetime import datetime
from io import BytesIO
from reportlab.pdfgen import canvas

# =========================
# CONFIG
# =========================

st.set_page_config(
    page_title="Bolão Copa 2026",
    layout="wide",
    initial_sidebar_state="collapsed"
)

JSON_URL = "https://jsonblob.com/api/jsonBlob/1319022513903362048"

# =========================
# CSS
# =========================

st.markdown("""
<style>

body {
    background-color: #f5f7fb;
}

.block-container {
    padding-top: 1.5rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

.title {
    font-size: 34px;
    font-weight: 800;
    color: #002776;
    text-align: center;
}

.subtitle {
    text-align: center;
    color: #009c3b;
    margin-bottom: 20px;
}

.card {
    background: white;
    padding: 15px;
    border-radius: 16px;
    box-shadow: 0px 3px 10px rgba(0,0,0,0.08);
}

</style>
""", unsafe_allow_html=True)

# =========================
# DATA
# =========================

def load_data():
    try:
        r = requests.get(JSON_URL, timeout=10)
        return r.json()
    except:
        return {"boloes": []}


def save_data(data):
    requests.put(JSON_URL, json=data, timeout=10)


data = load_data()

# =========================
# STATE
# =========================

if "page" not in st.session_state:
    st.session_state.page = "home"

if "selected_bolao" not in st.session_state:
    st.session_state.selected_bolao = None


# =========================
# HELPERS
# =========================

def find_bolao(nome):
    for b in data.get("boloes", []):
        if b["nome"] == nome:
            return b
    return None


def ensure_bolao(nome):
    if "boloes" not in data:
        data["boloes"] = []

    bolao = find_bolao(nome)

    if not bolao:
        bolao = {"nome": nome, "apostas": []}
        data["boloes"].append(bolao)
        save_data(data)

    return bolao


def upsert_aposta(bolao_nome, jogo, participante, placar):
    bolao = find_bolao(bolao_nome)
    if not bolao:
        return

    if "apostas" not in bolao:
        bolao["apostas"] = []

    # remove duplicidade participante+jogo
    bolao["apostas"] = [
        a for a in bolao["apostas"]
        if not (a["participante"] == participante and a["jogo"] == jogo)
    ]

    # bloqueio placar duplicado
    for a in bolao["apostas"]:
        if a["jogo"] == jogo and a["placar"] == placar:
            return "PL_DUP"

    bolao["apostas"].append({
        "participante": participante,
        "jogo": jogo,
        "placar": placar,
        "data": str(datetime.now())
    })

    save_data(data)
    return "OK"


# =========================
# API JOGOS (placeholder)
# =========================

def get_worldcup_matches():
    return [{"jogo": "Brasil vs Escócia"}]


# =========================
# HEADER
# =========================

st.markdown("<div class='title'>🇧🇷 Bolão Copa 2026</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Família • Amigos • Loja • Trabalho</div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🏆 Participar"):
        st.session_state.page = "participar"

with col2:
    if st.button("🛠️ Criar Bolão"):
        st.session_state.page = "criar"

with col3:
    if st.button("📊 Resultado"):
        st.session_state.page = "resultado"

st.markdown("---")

# =========================
# CRIAR BOLÃO
# =========================

def page_criar():
    st.markdown("## 🛠️ Criar Bolão")

    nome = st.text_input("Nome do bolão", key="criar_bolao_nome")

    if st.button("Criar"):
        if not nome:
            st.warning("Digite um nome")
            return

        ensure_bolao(nome)
        st.session_state.selected_bolao = nome
        st.session_state.page = "participar"
        st.rerun()


# =========================
# PARTICIPAR
# =========================

def page_participar():
    st.markdown("## 🏆 Participar")

    boloes = [b["nome"] for b in data.get("boloes", [])]

    if not boloes:
        st.info("Nenhum bolão criado")
        return

    selected = st.selectbox(
        "Bolão",
        boloes,
        key="select_bolao"
    )

    st.session_state.selected_bolao = selected

    jogos = get_worldcup_matches()

    jogo = st.selectbox(
        "Jogo",
        [j["jogo"] for j in jogos],
        key="select_jogo"
    )

    nome = st.text_input("Seu nome", key="participar_nome")

    col1, col2 = st.columns(2)

    with col1:
        a = st.number_input("Time A", min_value=0, key="gols_a")

    with col2:
        b = st.number_input("Time B", min_value=0, key="gols_b")

    placar = f"{a}x{b}"

    if st.button("Confirmar"):
        if not nome:
            st.warning("Digite seu nome")
            return

        res = upsert_aposta(selected, jogo, nome, placar)

        if res == "PL_DUP":
            st.error("Placar já escolhido por outro participante")
            return

        st.success("Aposta registrada")
        st.session_state.page = "resultado"
        st.rerun()


# =========================
# RESULTADO
# =========================

def page_resultado():
    st.markdown("## 📊 Resultado")

    bolao = find_bolao(st.session_state.selected_bolao)

    if not bolao:
        st.info("Selecione um bolão")
        return

    st.markdown(f"### {bolao['nome']}")

    st.markdown("### Palpites")

    for a in bolao.get("apostas", []):
        st.markdown(f"""
        <div style="padding:10px;background:#eee;border-radius:10px;margin:5px 0;">
        <b>{a['participante']}</b><br>
        {a['jogo']}<br>
        {a['placar']}
        </div>
        """, unsafe_allow_html=True)


# =========================
# ROUTER
# =========================

if st.session_state.page == "criar":
    page_criar()

elif st.session_state.page == "participar":
    page_participar()

elif st.session_state.page == "resultado":
    page_resultado()

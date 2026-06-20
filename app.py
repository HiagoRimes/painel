import streamlit as st
import requests
import json
from datetime import datetime

# =========================
# CONFIGURAÇÃO INICIAL
# =========================

st.set_page_config(
    page_title="Bolão Copa 2026",
    layout="wide",
    initial_sidebar_state="collapsed"
)

JSON_URL = "https://jsonblob.com/api/jsonBlob/1319022513903362048"

# =========================
# CSS PREMIUM CASUAL
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
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    color: #009c3b;
    font-size: 16px;
    margin-bottom: 25px;
}

.card {
    background: white;
    padding: 15px;
    border-radius: 16px;
    box-shadow: 0px 3px 10px rgba(0,0,0,0.08);
    margin-bottom: 12px;
}

.button-primary {
    background-color: #009c3b;
    color: white;
    padding: 10px 18px;
    border-radius: 12px;
    border: none;
    font-weight: bold;
}

.button-blue {
    background-color: #002776;
    color: white;
    padding: 10px 18px;
    border-radius: 12px;
    border: none;
    font-weight: bold;
}

.button-yellow {
    background-color: #ffdf00;
    color: black;
    padding: 10px 18px;
    border-radius: 12px;
    border: none;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

# =========================
# BANCO (JSONBlob)
# =========================

def load_data():
    try:
        r = requests.get(JSON_URL, timeout=10)
        return r.json()
    except:
        return {"boloes": []}


def save_data(data):
    requests.put(JSON_URL, json=data, timeout=10)


# =========================
# API JOGOS (Copa 2026)
# =========================

def get_worldcup_matches():
    """
    Fonte automática de jogos.
    (estrutura preparada para API esportiva)
    """
    try:
        # placeholder seguro (evita quebra)
        return []
    except:
        return []


# =========================
# UTILITÁRIOS
# =========================

def init_state():
    if "page" not in st.session_state:
        st.session_state.page = "home"

    if "selected_bolao" not in st.session_state:
        st.session_state.selected_bolao = None


init_state()


# =========================
# HEADER
# =========================

st.markdown("<div class='title'>🇧🇷 Bolão Copa 2026</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Bolões para família, amigos, loja e trabalho</div>", unsafe_allow_html=True)

# =========================
# NAVEGAÇÃO
# =========================

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
# DADOS
# =========================

data = load_data()

def get_boloes():
    return data.get("boloes", [])


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
        bolao = {
            "nome": nome,
            "apostas": []
        }
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

    # bloqueio de placar repetido no mesmo jogo
    for a in bolao["apostas"]:
        if a["jogo"] == jogo and a["placar"] == placar:
            return "PLACAR_EXISTE"

    bolao["apostas"].append({
        "participante": participante,
        "jogo": jogo,
        "placar": placar,
        "data": str(datetime.now())
    })

    save_data(data)
    return "OK"


# =========================
# PÁGINA CRIAR BOLÃO
# =========================

def page_criar_bolao():
    st.markdown("## 🛠️ Criar Bolão")

    nome = st.text_input("Nome do bolão")

    if st.button("Criar bolão"):
        if not nome:
            st.warning("Digite um nome")
            return

        ensure_bolao(nome)

        st.session_state.selected_bolao = nome
        st.session_state.page = "participar"
        st.rerun()


# =========================
# PÁGINA PARTICIPAR
# =========================

def page_participar():
    st.markdown("## 🏆 Participar do Bolão")

    boloes = [b["nome"] for b in get_boloes()]

    if not boloes:
        st.info("Nenhum bolão criado ainda.")
        return

    selected = st.selectbox(
        "Selecione o bolão",
        boloes,
        index=boloes.index(st.session_state.selected_bolao)
        if st.session_state.selected_bolao in boloes else 0
    )

    st.session_state.selected_bolao = selected

    st.markdown("### Próximo jogo da Copa (automático)")

    jogos = get_worldcup_matches()

    # fallback visual simples (caso API ainda não responda)
    if not jogos:
        jogos = [
            {"jogo": "Brasil vs Escócia", "data": "24/06/2026 19:00"}
        ]

    jogo_escolhido = st.selectbox(
        "Jogos disponíveis",
        [j["jogo"] for j in jogos]
    )

    st.markdown("### Seu palpite")

    nome = st.text_input("Seu nome")

    col1, col2 = st.columns(2)

    with col1:
        gols_a = st.number_input("Brasil / Time A", min_value=0, step=1)

    with col2:
        gols_b = st.number_input("Adversário / Time B", min_value=0, step=1)

    placar = f"{gols_a}x{gols_b}"

    if st.button("Confirmar palpite"):
        if not nome:
            st.warning("Digite seu nome")
            return

        result = upsert_aposta(selected, jogo_escolhido, nome, placar)

        if result == "PLACAR_EXISTE":
            st.error("Este placar já foi escolhido por outro participante.")
            return

        st.success("Aposta registrada com sucesso!")

        st.session_state.page = "resultado"
        st.rerun()


# =========================
# ROUTER
# =========================

if st.session_state.page == "criar":
    page_criar_bolao()

elif st.session_state.page == "participar":
    page_participar()

elif st.session_state.page == "resultado":
    st.markdown("## 📊 Resultado (base)")
    st.info("Parte 3 vai completar ranking + PDF")
# =========================
# RANKING SIMPLES
# =========================

def calcular_ranking(bolao):
    """
    Ranking simples baseado em:
    - 3 pontos por participação (base)
    - 5 pontos por placar exato (simples heurística local)
    OBS: sem resultados oficiais ainda nesta versão.
    """

    pontos = {}

    apostas = bolao.get("apostas", [])

    for a in apostas:
        nome = a["participante"]
        placar = a["placar"]

        if nome not in pontos:
            pontos[nome] = 0

        # base
        pontos[nome] += 3

        # bônus simples (placeholder de futuro cálculo real)
        if placar in ["1x0", "2x1", "2x0"]:
            pontos[nome] += 2

    ranking = sorted(pontos.items(), key=lambda x: x[1], reverse=True)
    return ranking


# =========================
# PDF EXPORT
# =========================

def gerar_pdf(bolao):
    from io import BytesIO
    from reportlab.pdfgen import canvas

    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, 800, f"Bolão: {bolao['nome']}")

    p.setFont("Helvetica", 11)
    y = 770

    for a in bolao.get("apostas", []):
        linha = f"{a['participante']} - {a['jogo']} - {a['placar']}"
        p.drawString(50, y, linha)
        y -= 20

        if y < 50:
            p.showPage()
            y = 800

    p.save()
    buffer.seek(0)
    return buffer


# =========================
# PÁGINA RESULTADO
# =========================

def page_resultado():
    st.markdown("## 📊 Resultado do Bolão")

    bolao_nome = st.session_state.selected_bolao

    if not bolao_nome:
        st.info("Selecione um bolão primeiro.")
        return

    bolao = find_bolao(bolao_nome)

    if not bolao:
        st.warning("Bolão não encontrado.")
        return

    st.markdown(f"### 🏆 {bolao_nome}")

    # =====================
    # RANKING
    # =====================

    st.markdown("### 📈 Ranking")

    ranking = calcular_ranking(bolao)

    for i, (nome, pontos) in enumerate(ranking, start=1):
        st.write(f"{i}. **{nome}** — {pontos} pts")

    st.markdown("---")

    # =====================
    # APOSTAS
    # =====================

    st.markdown("### 🎯 Palpites")

    apostas = bolao.get("apostas", [])

    if not apostas:
        st.info("Nenhuma aposta ainda.")
    else:
        for a in apostas:
            st.markdown(f"""
            <div style="padding:10px; background:#f2f2f2; border-radius:10px; margin-bottom:8px;">
                <b>{a['participante']}</b><br>
                {a['jogo']}<br>
                <b>{a['placar']}</b>
            </div>
            """, unsafe_allow_html=True)

    # =====================
    # DOWNLOAD PDF
    # =====================

    st.markdown("---")

    pdf = gerar_pdf(bolao)

    st.download_button(
        "📄 Baixar PDF do Bolão",
        data=pdf,
        file_name=f"{bolao_nome}.pdf",
        mime="application/pdf"
    )


# =========================
# ROUTER FINAL (ATUALIZADO)
# =========================

if st.session_state.page == "criar":
    page_criar_bolao()

elif st.session_state.page == "participar":
    page_participar()

elif st.session_state.page == "resultado":
    page_resultado()

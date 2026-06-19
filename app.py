import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
from fpdf import FPDF

# --- CONFIGURAÇÃO VISUAL PREMIUM DA PÁGINA ---
st.set_page_config(
    page_title="Bolão Seleção Brasileira ⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    [data-testid="collapsedControl"] { display: none; }
    h1, h2, h3 { color: #009c3b !important; font-family: 'Helvetica Neue', sans-serif; }
    .status-box { padding: 15px; border-radius: 8px; background-color: rgba(0, 156, 59, 0.15) !important; border-left: 5px solid #009c3b !important; margin-bottom: 15px; color: var(--text-color) !important; }
    .stat-card { padding: 15px; border-radius: 8px; background-color: var(--secondary-background-color) !important; border: 1px solid rgba(128, 128, 128, 0.2) !important; text-align: center; box-shadow: 0px 2px 4px rgba(0,0,0,0.05); color: var(--text-color) !important; }
    .stat-card strong { color: #009c3b !important; }
    div[data-testid="stHorizontalBlock"] { background-color: var(--secondary-background-color); padding: 8px; border-radius: 10px; margin-bottom: 20px; border: 1px solid rgba(128, 128, 128, 0.2); }
    .stButton>button { border-radius: 8px !important; font-weight: bold !important; transition: 0.3s !important; }
    .stButton>button[data-testid="stBaseButton-secondary"] { background-color: var(--secondary-background-color) !important; color: var(--text-color) !important; border: 1px solid rgba(128, 128, 128, 0.4) !important; }
    .stButton>button[data-testid="stBaseButton-primary"] { background-color: #002776 !important; color: white !important; border: 2px solid #ffdf00 !important; }
    .stFormSubmitButton>button { background-color: #009c3b !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: bold !important; }
    </style>
""", unsafe_allow_html=True)

# --- BANCO DE DADOS ---
DATABASE_URL = "https://jsonblob.com/api/jsonBlob/1319022513903362048"

def carregar_banco():
    try:
        r = requests.get(DATABASE_URL, timeout=10)
        return r.json() if r.status_code == 200 else {}
    except: return {}

def salvar_banco(dados):
    requests.put(DATABASE_URL, json=dados, timeout=10)
    st.session_state.dados = dados

if "dados" not in st.session_state: st.session_state.dados = carregar_banco()

# --- NAVEGAÇÃO ---
st.markdown("<h1 style='text-align: center;'>⚽ Bolão dos Amigos da Seleção</h1>", unsafe_allow_html=True)
if "aba" not in st.session_state: st.session_state.aba = "🏆 Entrar & Apostar"

col1, col2, col3 = st.columns(3)
if col1.button("🏆 Entrar & Apostar", use_container_width=True, type="primary" if st.session_state.aba=="🏆 Entrar & Apostar" else "secondary"): st.session_state.aba = "🏆 Entrar & Apostar"
if col2.button("🛠️ Criar Novo Bolão", use_container_width=True, type="primary" if st.session_state.aba=="🛠️ Criar Novo Bolão" else "secondary"): st.session_state.aba = "🛠️ Criar Novo Bolão"
if col3.button("📊 Ver Palpites & Download", use_container_width=True, type="primary" if st.session_state.aba=="📊 Ver Palpites & Download" else "secondary"): st.session_state.aba = "📊 Ver Palpites & Download"

st.markdown("---")

# --- LÓGICA DE EXECUÇÃO ---
if st.session_state.aba == "🏆 Entrar & Apostar":
    if not st.session_state.dados: st.warning("Crie um bolão primeiro.")
    else:
        grupo = st.selectbox("Selecione o Bolão:", list(st.session_state.dados.keys()))
        detalhes = st.session_state.dados[grupo]
        st.markdown(f"<div class='status-box'>📍 <strong>Bolão:</strong> {grupo} | ⚽ <strong>Jogo:</strong> {detalhes['jogo']}</div>", unsafe_allow_html=True)
        
        with st.form("form_aposta"):
            nome = st.text_input("Seu Nome:")
            c1, c2 = st.columns(2)
            br = c1.number_input("Gols Brasil", 0, 10)
            op = c2.number_input("Gols Adversário", 0, 10)
            if st.form_submit_button("Confirmar Palpite"):
                st.session_state.dados[grupo]['apostas'].append({"Nome": nome, "Palpite": f"{br} x {op}", "Data": datetime.now().strftime("%d/%m")})
                salvar_banco(st.session_state.dados)
                st.success("Palpite registrado!")

elif st.session_state.aba == "🛠️ Criar Novo Bolão":
    nome = st.text_input("Nome do Grupo:")
    jogo = st.selectbox("Jogo:", ["Brasil x Haiti", "Brasil x Escócia"])
    if st.button("🚀 Criar este Bolão"):
        st.session_state.dados[nome] = {"jogo": jogo, "apostas": [], "resultado": ""}
        salvar_banco(st.session_state.dados)
        st.success("Bolão criado!")

elif st.session_state.aba == "📊 Ver Palpites & Download":
    if not st.session_state.dados: st.info("Nada a exibir.")
    else:
        grupo = st.selectbox("Selecione o grupo:", list(st.session_state.dados.keys()))
        df = pd.DataFrame(st.session_state.dados[grupo]['apostas'])
        if not df.empty:
            st.table(df)
            if st.checkbox("🔑 Administrar"):
                res = st.text_input("Resultado Real:")
                if st.button("Salvar Resultado"):
                    st.session_state.dados[grupo]['resultado'] = res
                    salvar_banco(st.session_state.dados)

# --- COMPARTILHAMENTO ---
link = "https://bolaodobrasil.streamlit.app/"
st.link_button("📲 Convidar amigos no WhatsApp", f"https://api.whatsapp.com/send?text=Participe do meu Bolão! {link}")

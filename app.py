import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# Configuração da Página
st.set_page_config(page_title="Bolão Seleção Brasileira ⚽", layout="wide")

# URL do banco
DATABASE_URL = "https://jsonblob.com/api/jsonBlob/1319022513903362048"

# --- FUNÇÕES DE BANCO ---
def carregar_dados():
    try:
        response = requests.get(DATABASE_URL, headers={"Cache-Control": "no-cache"})
        return response.json() if response.status_code == 200 else {}
    except: return {}

def salvar_dados(dados):
    requests.put(DATABASE_URL, json=dados, headers={"Content-Type": "application/json"})
    st.session_state.dados = dados

# --- ESTADO INICIAL ---
if 'dados' not in st.session_state: st.session_state.dados = carregar_dados()
if 'tab' not in st.session_state: st.session_state.tab = 'Apostar'

# --- CSS E LAYOUT ---
st.markdown("""
    <style>
    .status-box { padding: 15px; border-radius: 10px; background-color: #e8f5e9; border-left: 5px solid #009c3b; margin: 15px 0; }
    .stButton>button { border-radius: 20px !important; font-weight: bold !important; }
    </style>
""", unsafe_allow_html=True)

st.title("⚽ Bolão dos Amigos da Seleção")

# Navegação
c1, c2, c3 = st.columns(3)
if c1.button("🏆 Entrar & Apostar", use_container_width=True): st.session_state.tab = 'Apostar'; st.rerun()
if c2.button("🛠️ Criar Novo Bolão", use_container_width=True): st.session_state.tab = 'Criar'; st.rerun()
if c3.button("📊 Resultados", use_container_width=True): st.session_state.tab = 'Resultados'; st.rerun()

# --- LÓGICA ---
if st.session_state.tab == 'Apostar':
    dados = carregar_dados() 
    if not dados:
        st.warning("Nenhum bolão disponível. Vá na aba 'Criar Novo Bolão'.")
    else:
        grupo = st.selectbox("Selecione o seu bolão:", list(dados.keys()))
        info = dados[grupo]
        st.markdown(f"<div class='status-box'>📌 Bolão: {grupo} | ⚽ Jogo: {info['jogo']}</div>", unsafe_allow_html=True)
        
        with st.form("aposta_form", clear_on_submit=True):
            nome = st.text_input("Seu nome:")
            c1, c2 = st.columns(2)
            g1 = c1.number_input("Gols Brasil", 0, 10)
            g2 = c2.number_input("Gols Adversário", 0, 10)
            if st.form_submit_button("Confirmar Palpite"):
                if nome:
                    novo = {"Nome": nome, "Palpite": f"{g1} x {g2}", "Data": datetime.now().strftime("%d/%m %H:%M")}
                    dados[grupo]['apostas'] = [a for a in dados[grupo]['apostas'] if a['Nome'] != nome] + [novo]
                    salvar_dados(dados)
                    st.success("Palpite salvo!")
                    st.session_state.tab = 'Resultados'
                    st.rerun()

elif st.session_state.tab == 'Criar':
    st.subheader("Criar novo grupo")
    nome = st.text_input("Nome do Grupo:")
    jogo = st.selectbox("Jogo:", ["Brasil x Escócia (24/06/2026)", "Brasil x Fase Final (28/06/2026)"])
    if st.button("🚀 Criar Bolão"):
        if nome:
            dados = carregar_dados()
            dados[nome] = {"jogo": jogo, "apostas": [], "resultado": ""}
            salvar_dados(dados)
            st.success("Bolão criado com sucesso!")
            st.session_state.tab = 'Apostar'
            st.rerun()

elif st.session_state.tab == 'Resultados':
    dados = carregar_dados()
    if dados:
        grupo = st.selectbox("Ver palpites do grupo:", list(dados.keys()))
        df = pd.DataFrame(dados[grupo]['apostas'])
        if not df.empty: st.table(df)
        else: st.write("Ainda não há palpites.")

import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
from fpdf import FPDF

# --- CONFIGURAÇÃO VISUAL PREMIUM ---
st.set_page_config(page_title="Bolão Seleção Brasileira ⚽", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    [data-testid="collapsedControl"] { display: none; }
    h1, h2, h3 { color: #009c3b !important; font-family: 'Helvetica Neue', sans-serif; }
    .status-box { padding: 15px; border-radius: 8px; background-color: rgba(0, 156, 59, 0.15) !important; border-left: 5px solid #009c3b !important; margin-bottom: 15px; }
    .stButton>button { border-radius: 20px !important; font-weight: bold !important; transition: 0.3s !important; }
    .stButton>button[data-testid="stBaseButton-secondary"] { background-color: #f0f2f6 !important; color: #333 !important; }
    .stButton>button[data-testid="stBaseButton-primary"] { background-color: #009c3b !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

# --- BANCO DE DADOS ---
DATABASE_URL = "https://jsonblob.com/api/jsonBlob/1319022513903362048"

def carregar():
    try:
        r = requests.get(DATABASE_URL, timeout=10)
        return r.json() if r.status_code == 200 else {}
    except: return {}

def salvar(dados):
    requests.put(DATABASE_URL, json=dados, timeout=10)
    st.session_state.dados = dados

if "dados" not in st.session_state: st.session_state.dados = carregar()
if "aba_ativa" not in st.session_state: st.session_state.aba_ativa = "🏆 Entrar & Apostar"
if "grupo_sel" not in st.session_state: st.session_state.grupo_sel = None

# --- NAVEGAÇÃO ---
st.markdown("<h1 style='text-align: center;'>⚽ Bolão dos Amigos da Seleção</h1>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
if c1.button("🏆 Entrar & Apostar", use_container_width=True, type="primary" if st.session_state.aba_ativa == "🏆 Entrar & Apostar" else "secondary"): 
    st.session_state.aba_ativa = "🏆 Entrar & Apostar"; st.rerun()
if c2.button("🛠️ Criar Novo Bolão", use_container_width=True, type="primary" if st.session_state.aba_ativa == "🛠️ Criar Novo Bolão" else "secondary"): 
    st.session_state.aba_ativa = "🛠️ Criar Novo Bolão"; st.rerun()
if c3.button("📊 Ver Palpites & Download", use_container_width=True, type="primary" if st.session_state.aba_ativa == "📊 Ver Palpites & Download" else "secondary"): 
    st.session_state.aba_ativa = "📊 Ver Palpites & Download"; st.rerun()

st.markdown("---")

# --- LÓGICA DE EXECUÇÃO ---
if st.session_state.aba_ativa == "🏆 Entrar & Apostar":
    st.subheader("📝 Registrar o seu Palpite")
    if not st.session_state.dados: st.warning("Nenhum bolão ativo.")
    else:
        lista = list(st.session_state.dados.keys())
        if st.session_state.grupo_sel not in lista: st.session_state.grupo_sel = lista[0]
        
        cols = st.columns(len(lista))
        for i, g in enumerate(lista):
            if cols[i].button(f"🔵 {g}" if st.session_state.grupo_sel == g else f"⚪ {g}", use_container_width=True):
                st.session_state.grupo_sel = g; st.rerun()
        
        grupo = st.session_state.grupo_sel
        d = st.session_state.dados[grupo]
        st.markdown(f"<div class='status-box'>📌 <strong>Bolão Ativo:</strong> {grupo} | ⚽ <strong>Confronto:</strong> {d['jogo']}</div>", unsafe_allow_html=True)
        
        with st.form("aposta", clear_on_submit=True):
            nome = st.text_input("Seu Nome ou Alcunha:")
            c_g1, c_g2 = st.columns(2)
            br = c_g1.number_input("Gols do Brasil:", 0, 20)
            op = c_g2.number_input("Gols do Adversário:", 0, 20)
            
            if st.form_submit_button("Confirmar Palpite"):
                novo_palpite = {"Nome": nome, "Palpite": f"{br} x {op}", "Data": datetime.now().strftime("%d/%m %H:%M")}
                
                # Previne duplicata verificando se o nome já existe na lista
                d['apostas'] = [a for a in d['apostas'] if a['Nome'] != nome] + [novo_palpite]
                
                salvar(st.session_state.dados)
                st.session_state.aba_ativa = "📊 Ver Palpites & Download"
                st.rerun()

elif st.session_state.aba_ativa == "🛠️ Criar Novo Bolão":
    nome = st.text_input("Nome do Bolão:")
    jogo = st.selectbox("Jogo:", ["Brasil x Haiti (19/06/2026)", "Brasil x Escócia (24/06/2026)"])
    if st.button("🚀 Inicializar Meu Bolão"):
        if nome and nome not in st.session_state.dados:
            st.session_state.dados[nome] = {"jogo": jogo, "apostas": [], "resultado": ""}
            salvar(st.session_state.dados)
            st.session_state.aba_ativa = "🏆 Entrar & Apostar"; st.rerun()
        else: st.error("Nome inválido ou já existe!")

elif st.session_state.aba_ativa == "📊 Ver Palpites & Download":
    if not st.session_state.dados: st.info("Nada a exibir.")
    else:
        grupo = st.selectbox("Selecione o grupo:", list(st.session_state.dados.keys()))
        df = pd.DataFrame(st.session_state.dados[grupo]['apostas'])
        if not df.empty: st.table(df)
        
        if st.checkbox("🔑 Administrar"):
            res = st.text_input("Resultado Real (ex: 2 x 0):")
            if st.button("Salvar Resultado"):
                st.session_state.dados[grupo]['resultado'] = res
                salvar(st.session_state.dados); st.rerun()

st.markdown("---")
link_whats = f"https://api.whatsapp.com/send?text=Aposte no meu Bolão! Acesse: https://bolaodobrasil.streamlit.app/"
st.link_button("📲 Convidar amigos no WhatsApp", link_whats)

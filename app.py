import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Bolão Seleção Brasileira ⚽", layout="wide", initial_sidebar_state="collapsed")

# --- CSS FIEL AO ORIGINAL ---
st.markdown("""
    <style>
    [data-testid="collapsedControl"] { display: none; }
    h1 { color: #009c3b !important; text-align: center; }
    .status-box { padding: 15px; border-radius: 8px; background-color: rgba(0, 156, 59, 0.15) !important; border-left: 5px solid #009c3b !important; margin-bottom: 15px; }
    .stButton>button { border-radius: 20px !important; font-weight: bold !important; transition: 0.3s !important; border: 1px solid #009c3b !important; }
    /* Pílulas coloridas */
    .stButton>button[data-testid="stBaseButton-secondary"] { background-color: white !important; color: #009c3b !important; }
    .stButton>button[data-testid="stBaseButton-primary"] { background-color: #009c3b !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

# --- BANCO DE DADOS (SEM CACHE) ---
DATABASE_URL = "https://jsonblob.com/api/jsonBlob/1319022513903362048"

def carregar_banco_sem_cache():
    try:
        r = requests.get(DATABASE_URL, headers={"Cache-Control": "no-cache"}, timeout=10)
        return r.json() if r.status_code == 200 else {}
    except: return {}

def salvar_banco(dados):
    requests.put(DATABASE_URL, json=dados, timeout=10)
    st.session_state.dados = dados

# Recarrega sempre para garantir sincronia entre dispositivos
st.session_state.dados = carregar_banco_sem_cache()

# --- NAVEGAÇÃO ---
st.markdown("<h1>⚽ Bolão dos Amigos da Seleção</h1>", unsafe_allow_html=True)

if "aba_ativa" not in st.session_state: st.session_state.aba_ativa = "🏆 Entrar & Apostar"

c1, c2, c3 = st.columns(3)
if c1.button("🏆 Entrar & Apostar", use_container_width=True, type="primary" if st.session_state.aba_ativa == "🏆 Entrar & Apostar" else "secondary"): 
    st.session_state.aba_ativa = "🏆 Entrar & Apostar"; st.rerun()
if c2.button("🛠️ Criar Novo Bolão", use_container_width=True, type="primary" if st.session_state.aba_ativa == "🛠️ Criar Novo Bolão" else "secondary"): 
    st.session_state.aba_ativa = "🛠️ Criar Novo Bolão"; st.rerun()
if c3.button("📊 Ver Palpites & Download", use_container_width=True, type="primary" if st.session_state.aba_ativa == "📊 Ver Palpites & Download" else "secondary"): 
    st.session_state.aba_ativa = "📊 Ver Palpites & Download"; st.rerun()

st.markdown("---")

# --- LÓGICA ---
if st.session_state.aba_ativa == "🏆 Entrar & Apostar":
    st.subheader("📝 Registrar o seu Palpite")
    if not st.session_state.dados: st.warning("Nenhum bolão ativo encontrado.")
    else:
        lista = list(st.session_state.dados.keys())
        if "grupo_sel" not in st.session_state or st.session_state.grupo_sel not in lista: st.session_state.grupo_sel = lista[0]
        
        cols = st.columns(len(lista))
        for i, g in enumerate(lista):
            if cols[i].button(g, use_container_width=True, type="primary" if st.session_state.grupo_sel == g else "secondary"):
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
                novo = {"Nome": nome, "Palpite": f"{br} x {op}", "Data": datetime.now().strftime("%d/%m %H:%M")}
                d['apostas'] = [a for a in d['apostas'] if a['Nome'] != nome] + [novo]
                salvar_banco(st.session_state.dados)
                st.session_state.aba_ativa = "📊 Ver Palpites & Download"
                st.rerun()

elif st.session_state.aba_ativa == "🛠️ Criar Novo Bolão":
    nome = st.text_input("Nome do novo bolão:")
    jogo = st.selectbox("Jogo:", ["Brasil x Haiti (19/06/2026)", "Brasil x Escócia (24/06/2026)"])
    if st.button("🚀 Inicializar Meu Bolão"):
        if nome and nome not in st.session_state.dados:
            st.session_state.dados[nome] = {"jogo": jogo, "apostas": [], "resultado": ""}
            salvar_banco(st.session_state.dados)
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
                salvar_banco(st.session_state.dados); st.rerun()

st.markdown("---")
st.link_button("📲 Convidar amigos no WhatsApp", f"https://api.whatsapp.com/send?text=Aposte no meu Bolão! https://bolaodobrasil.streamlit.app/")

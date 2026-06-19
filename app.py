import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
from fpdf import FPDF
import base64

# Configuração da Página
st.set_page_config(page_title="Bolão Seleção Brasileira ⚽", layout="wide", initial_sidebar_state="collapsed")

# --- CSS INTEGRAL ---
st.markdown("""
    <style>
    [data-testid="collapsedControl"] { display: none; }
    h1, h2, h3 { color: #009c3b !important; font-family: 'Helvetica Neue', sans-serif; }
    .status-box { padding: 15px; border-radius: 8px; background-color: rgba(0, 156, 59, 0.15) !important; border-left: 5px solid #009c3b !important; margin-bottom: 15px; }
    .stButton>button { border-radius: 20px !important; font-weight: bold !important; transition: 0.3s !important; padding: 10px 20px; }
    .stButton>button[data-testid="stBaseButton-secondary"] { background-color: #f0f2f6 !important; color: #333 !important; border: 1px solid #ccc !important; }
    .stButton>button[data-testid="stBaseButton-primary"] { background-color: #009c3b !important; color: white !important; border: 1px solid #009c3b !important; }
    </style>
""", unsafe_allow_html=True)

# --- BANCO DE DADOS ---
DATABASE_URL = "https://jsonblob.com/api/jsonBlob/1319022513903362048"

def ler_banco():
    try:
        response = requests.get(DATABASE_URL)
        if response.status_code == 200:
            return response.json()
    except: pass
    return {}

def gravar_banco(dados):
    try:
        requests.put(DATABASE_URL, json=dados)
        st.session_state.dados = dados
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")

# Inicialização de Estado
if 'dados' not in st.session_state:
    st.session_state.dados = ler_banco()
if 'aba' not in st.session_state:
    st.session_state.aba = 'Apostar'

# --- NAVEGAÇÃO SUPERIOR ---
st.markdown("<h1 style='text-align: center;'>⚽ Bolão dos Amigos da Seleção</h1>", unsafe_allow_html=True)
col_nav1, col_nav2, col_nav3 = st.columns(3)

if col_nav1.button("🏆 Entrar & Apostar", use_container_width=True, type="primary" if st.session_state.aba == 'Apostar' else "secondary"):
    st.session_state.aba = 'Apostar'
    st.rerun()
if col_nav2.button("🛠️ Criar Novo Bolão", use_container_width=True, type="primary" if st.session_state.aba == 'Criar' else "secondary"):
    st.session_state.aba = 'Criar'
    st.rerun()
if col_nav3.button("📊 Ver Palpites & Download", use_container_width=True, type="primary" if st.session_state.aba == 'Resultados' else "secondary"):
    st.session_state.aba = 'Resultados'
    st.rerun()

st.markdown("---")

# --- LÓGICA DE ABA: APOSTAR ---
if st.session_state.aba == 'Apostar':
    st.markdown("## 📝 Registrar o seu Palpite")
    dados = ler_banco()
    if not dados:
        st.warning("Ainda não existem bolões criados.")
    else:
        # Seleção de bolão por botões (pílulas)
        lista_boloes = list(dados.keys())
        if 'bolao_sel' not in st.session_state or st.session_state.bolao_sel not in lista_boloes:
            st.session_state.bolao_sel = lista_boloes[0]
            
        cols_btns = st.columns(len(lista_boloes))
        for i, nome_bolao in enumerate(lista_boloes):
            if cols_btns[i].button(nome_bolao, use_container_width=True, type="primary" if st.session_state.bolao_sel == nome_bolao else "secondary"):
                st.session_state.bolao_sel = nome_bolao
                st.rerun()
        
        bolao_ativo = st.session_state.bolao_sel
        info = dados[bolao_ativo]
        st.markdown(f"<div class='status-box'>📌 <strong>Bolão Ativo:</strong> {bolao_ativo} | ⚽ <strong>Confronto:</strong> {info['jogo']}</div>", unsafe_allow_html=True)
        
        with st.form("form_aposta", clear_on_submit=True):
            nome_usuario = st.text_input("O seu Nome ou Alcunha:")
            col_g1, col_g2 = st.columns(2)
            gols_br = col_g1.number_input("Gols do Brasil:", min_value=0, step=1)
            gols_op = col_g2.number_input("Gols do Adversário:", min_value=0, step=1)
            
            if st.form_submit_button("Confirmar Palpite"):
                if nome_usuario:
                    novo_palpite = {"Nome": nome_usuario, "Palpite": f"{gols_br} x {gols_op}", "Data": datetime.now().strftime("%d/%m %H:%M")}
                    # Filtra palpite anterior do mesmo nome
                    lista_apostas = [a for a in info['apostas'] if a['Nome'] != nome_usuario]
                    lista_apostas.append(novo_palpite)
                    dados[bolao_ativo]['apostas'] = lista_apostas
                    gravar_banco(dados)
                    st.success("Palpite registrado com sucesso!")
                    st.session_state.aba = 'Resultados'
                    st.rerun()

# --- LÓGICA DE ABA: CRIAR ---
elif st.session_state.aba == 'Criar':
    st.markdown("## 🛠️ Configurar um Novo Grupo")
    nome_novo = st.text_input("Nome do Bolão:")
    jogo_sel = st.selectbox("Escolha o jogo:", ["Brasil x Haiti (19/06/2026)", "Brasil x Escócia (24/06/2026)"])
    if st.button("🚀 Inicializar Meu Bolão"):
        dados = ler_banco()
        if nome_novo and nome_novo not in dados:
            dados[nome_novo] = {"jogo": jogo_sel, "apostas": [], "resultado": ""}
            gravar_banco(dados)
            st.session_state.aba = 'Apostar'
            st.rerun()

# --- LÓGICA DE ABA: RESULTADOS ---
elif st.session_state.aba == 'Resultados':
    st.markdown("## 📊 Resultados e Palpites")
    dados = ler_banco()
    if not dados:
        st.info("Nenhum palpite para exibir.")
    else:
        grupo_escolhido = st.selectbox("Selecione o grupo:", list(dados.keys()))
        df_apostas = pd.DataFrame(dados[grupo_escolhido]['apostas'])
        if not df_apostas.empty:
            st.table(df_apostas)
            
            if st.checkbox("🔑 Administrar"):
                res_real = st.text_input("Resultado Real (ex: 2 x 0):")
                if st.button("Salvar Resultado Oficial"):
                    dados[grupo_escolhido]['resultado'] = res_real
                    gravar_banco(dados)
                    st.rerun()
        else:
            st.write("Ainda não há palpites neste bolão.")

st.markdown("---")
st.link_button("📲 Convidar amigos no WhatsApp", f"https://api.whatsapp.com/send?text=Aposte no meu Bolão! Acesse: https://bolaodobrasil.streamlit.app/")

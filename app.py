import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
from fpdf import FPDF

# Configuração da Página
st.set_page_config(page_title="Bolão Seleção Brasileira ⚽", layout="wide")

# URL do banco de dados compartilhado
DATABASE_URL = "https://jsonblob.com/api/jsonBlob/1319022513903362048"

# --- FUNÇÕES DE APOIO ---
def carregar_dados():
    try:
        r = requests.get(DATABASE_URL, timeout=10)
        return r.json() if r.status_code == 200 else {}
    except: return {}

def salvar_dados(dados):
    try:
        requests.put(DATABASE_URL, json=dados, timeout=10)
        st.session_state.dados = dados
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")

if "dados" not in st.session_state:
    st.session_state.dados = carregar_dados()

# --- FUNÇÕES DE CÁLCULO E PDF ---
def calcular_pontos(palpite, resultado_real):
    try:
        gp, gr = palpite.split(" x "), resultado_real.split(" x ")
        if gp == gr: return 10
        # Lógica de acerto de vencedor simplificada
        return 3
    except: return 0

def gerar_pdf(nome_grupo, apostas, resultado):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Bolão: {nome_grupo}", ln=True, align="C")
    pdf.set_font("Arial", '', 12)
    for a in apostas:
        pdf.cell(0, 10, f"{a['Nome']}: {a['Palpite']}", ln=True)
    return pdf.output(dest='S')

# --- INTERFACE ---
st.title("⚽ Bolão da Seleção Brasileira")
aba1, aba2, aba3 = st.tabs(["🏆 Apostar", "🛠️ Criar Bolão", "📊 Classificação"])

# ABA 1: APOSTAR
with aba1:
    if not st.session_state.dados:
        st.write("Crie um bolão na aba 'Criar Bolão' primeiro.")
    else:
        grupo = st.selectbox("Escolha o Bolão:", list(st.session_state.dados.keys()), key="sel_apostar")
        with st.form("form_aposta"):
            nome = st.text_input("Seu Nome")
            br = st.number_input("Gols Brasil", 0, 10)
            op = st.number_input("Gols Adversário", 0, 10)
            if st.form_submit_button("Enviar Palpite"):
                palpite = f"{br} x {op}"
                if any(a['Nome'] == nome for a in st.session_state.dados[grupo]['apostas']):
                    st.error("Você já deu seu palpite neste grupo!")
                else:
                    st.session_state.dados[grupo]['apostas'].append({"Nome": nome, "Palpite": palpite, "Data": datetime.now().strftime("%d/%m %H:%M")})
                    salvar_dados(st.session_state.dados)
                    st.success("Palpite registrado!")

# ABA 2: CRIAR BOLÃO
with aba2:
    nome_bolao = st.text_input("Nome do Novo Bolão")
    jogo = st.selectbox("Jogo:", ["Brasil x Haiti", "Brasil x Escócia"])
    if st.button("🚀 Criar este Bolão", key="btn_criar_completo"):
        if nome_bolao in st.session_state.dados:
            st.error("Nome já existe!")
        else:
            st.session_state.dados[nome_bolao] = {"jogo": jogo, "apostas": [], "resultado": ""}
            salvar_dados(st.session_state.dados)
            st.rerun()

# ABA 3: RESULTADOS
with aba3:
    if st.session_state.dados:
        grupo = st.selectbox("Escolha o Bolão:", list(st.session_state.dados.keys()), key="sel_res")
        st.write(f"Palpites para {grupo}:")
        df = pd.DataFrame(st.session_state.dados[grupo]['apostas'])
        if not df.empty:
            st.table(df)
            if st.button("📥 Baixar PDF"):
                pdf_bin = gerar_pdf(grupo, st.session_state.dados[grupo]['apostas'], "")
                st.download_button("Clique aqui para baixar", pdf_bin, "bolao.pdf")
        
        # Admin Simples
        if st.checkbox("Painel Admin"):
            res = st.text_input("Definir Resultado (ex: 2 x 0)")
            if st.button("Salvar Resultado"):
                st.session_state.dados[grupo]['resultado'] = res
                salvar_dados(st.session_state.dados)
                st.rerun()

# Rodapé de Compartilhamento
st.markdown("---")
link_msg = f"Aposte no meu bolão! Acesse: https://bolaodobrasil.streamlit.app/"
st.link_button("📲 Convidar amigos via WhatsApp", f"https://api.whatsapp.com/send?text={requests.utils.quote(link_msg)}")

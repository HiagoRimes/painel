import streamlit as st
import google.generativeai as genai
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# Configuração da Página
st.set_page_config(page_title="Mentor Institucional WIN", layout="wide")

# --- SENHA DE ACESSO ---
SENHA_ACESSO = "aprender" 
def check_password():
    password = st.text_input("🔑 Digite a senha para liberar seu estudo:", type="password")
    if password == SENHA_ACESSO:
        return True
    elif password != "":
        st.error("Senha incorreta.")
        return False
    return False

# --- CONFIGURAÇÃO API ---
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# --- FUNÇÃO DE BUSCA BRAPI ---
def buscar_dados_mercado(tickers):
    token = "T95TARf3vRa3adDmBwCJAZ"
    resultados = []
    for ticker in tickers:
        try:
            url = f"https://brapi.dev/api/quote/{ticker}?token={token}"
            response = requests.get(url, timeout=5)
            data = response.json()
            preco = data['results'][0]['regularMarketPrice']
            var = data['results'][0]['regularMarketChangePercent']
            resultados.append(f"{ticker}: R${preco} ({var}%)")
        except:
            resultados.append(f"{ticker}: Dado indisponível")
    return "\n".join(resultados)

# --- CALENDÁRIO ---
@st.cache_data(ttl=3600)
def puxar_calendario():
    try:
        url = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        root = ET.fromstring(response.content)
        hoje_dt = datetime.now()
        eventos = [f"• **{e.find('time').text} ({e.find('country').text})**: {e.find('title').text}" 
                   for e in root.findall('event') if e.find('date').text == hoje_dt.strftime("%m-%d-%Y") and e.find('impact').text in ['High', 'Medium']]
        return f"### 📅 Agenda: {hoje_dt.strftime('%d/%m/%Y')}\n\n" + "\n".join(eventos) if eventos else "Sem eventos."
    except: return "### 📅 Calendário indisponível."

# --- LÓGICA PRINCIPAL ---
if check_password():
    if 'historico_data' not in st.session_state: st.session_state.historico_data = datetime.now().date()
    if 'historico_analises' not in st.session_state: st.session_state.historico_analises = []
    
    st.title("🎓 Mentor Institucional de Fluxo (Automatizado)")
    st.info(puxar_calendario())

    # Lista de ativos para monitorar
    lista_ativos = ["WINM26", "WDOJ26", "DI1F27", "PETR4", "ES1!", "NQ1!", "VIX"]

    if st.button("🚀 Processar Análise de Mercado"):
        with st.spinner("Conectando na B3 e analisando..."):
            dados_reais = buscar_dados_mercado(lista_ativos)
            hist_texto = "\n".join(st.session_state.historico_analises)
            
            prompt_final = f"""
            Você é um Estrategista de Mesa de Operações e um Mestre em Educação Financeira.
            Analise estes dados de mercado obtidos em tempo real:
            {dados_reais}
            
            HISTÓRICO DO PREGÃO: {hist_texto}
            AGENDA: {puxar_calendario()}
            
            REGRAS: WIN é consequência. Fluxo real sempre vence. 
            Realize uma leitura institucional priorizando o aprendizado.
            """
            
            try:
                response = model.generate_content(prompt_final)
                st.markdown("### 📊 Relatório Institucional")
                st.markdown(response.text)
                st.session_state.historico_analises.append(response.text)
            except Exception as e:
                st.error(f"Erro na análise: {e}")

    if st.sidebar.button("🗑️ Limpar Histórico"):
        st.session_state.historico_analises = []
        st.rerun()

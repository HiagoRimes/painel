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
        st.error("Senha incorreta. Tente novamente.")
        return False
    else:
        return False

# --- CONFIGURAÇÃO API GOOGLE ---
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

def get_model():
    """Detecta automaticamente o modelo disponível para evitar erro 404."""
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Tenta modelos da família 1.5, se não, pega o primeiro disponível
        for m in ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']:
            if m in models: return genai.GenerativeModel(m)
        return genai.GenerativeModel(models[0])
    except Exception as e:
        st.error(f"Erro ao configurar modelo: {e}")
        return None

model = get_model()

# --- FUNÇÃO DE BUSCA BRAPI (AUTOMAÇÃO) ---
def buscar_dados_mercado(tickers):
    token = "T95TARf3vRa3adDmBwCJAZ"
    resultados = []
    for ticker in tickers:
        try:
            url = f"https://brapi.dev/api/quote/{ticker}?token={token}"
            response = requests.get(url, timeout=5)
            data = response.json()
            if 'results' in data and len(data['results']) > 0:
                preco = data['results'][0]['regularMarketPrice']
                var = data['results'][0]['regularMarketChangePercent']
                resultados.append(f"{ticker}: R${preco} ({var}%)")
            else:
                resultados.append(f"{ticker}: Dado não encontrado")
        except:
            resultados.append(f"{ticker}: Erro na conexão")
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
        return f"### 📅 Agenda: {hoje_dt.strftime('%d/%m/%Y')}\n\n" + "\n".join(eventos) if eventos else "Sem eventos relevantes."
    except: return "### 📅 Calendário indisponível."

# --- LÓGICA PRINCIPAL ---
if check_password():
    if 'historico_analises' not in st.session_state: st.session_state.historico_analises = []
    
    st.title("🎓 Mentor Institucional de Fluxo (Tempo Real)")
    st.info(puxar_calendario())

    # Ativos monitorados
    lista_ativos = ["WINM26", "WDOJ26", "DI1F27", "PETR4", "ES1!", "NQ1!", "VIX"]

    if st.button("🚀 Processar Análise de Mercado"):
        with st.spinner("Consultando dados da B3/Global..."):
            dados_reais = buscar_dados_mercado(lista_ativos)
            hist_texto = "\n".join(st.session_state.historico_analises[-5:]) # Mantém os últimos 5 para contexto
            
            prompt_final = f"""
            Você é um Estrategista de Mesa de Operações e um Mestre em Educação Financeira.
            Sua missão é realizar a leitura institucional do WIN e ativos correlacionados.
            
            DADOS DE MERCADO (TEMPO REAL):
            {dados_reais}
            
            HISTÓRICO RECENTE: {hist_texto}
            AGENDA DO DIA: {puxar_calendario()}
            
            REGRAS: WIN é consequência. Fluxo real sempre vence. 
            Seja didático e direto.
            """
            
            try:
                if model:
                    response = model.generate_content(prompt_final)
                    st.markdown("### 📊 Relatório Institucional")
                    st.markdown(response.text)
                    st.session_state.historico_analises.append(response.text)
                else:
                    st.error("Modelo não configurado.")
            except Exception as e:
                st.error(f"Erro na análise: {e}")

    if st.sidebar.button("🗑️ Limpar Pregão Atual"):
        st.session_state.historico_analises = []
        st.rerun()
    

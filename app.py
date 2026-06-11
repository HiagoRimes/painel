import streamlit as st
import google.generativeai as genai
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Mentor de Fluxo Institucional", layout="wide")

# Inicializa a memória da sessão
if 'historico_analises' not in st.session_state:
    st.session_state.historico_analises = []

# Configuração da API do Google
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-3.5-flash')
except Exception as e:
    st.error("Erro na chave de API.")
    st.stop()

# Função do Calendário Econômico (Forex Factory formatado)
@st.cache_data(ttl=3600)
def puxar_calendario_macro():
    try:
        url = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        root = ET.fromstring(response.content)
        hoje = datetime.now().strftime("%m-%d-%Y")
        eventos = []
        for event in root.findall('event'):
            if event.find('date').text == hoje and event.find('impact').text in ['High', 'Medium']:
                hora = event.find('time').text
                moeda = event.find('country').text
                titulo = event.find('title').text
                eventos.append(f"• **{hora} ({moeda})**: {titulo}")
        return "\n".join(eventos) if eventos else "Sem eventos de alto impacto hoje."
    except:
        return "Erro ao carregar calendário."

# Função da Carteira (Aqui você plugará sua API real)
def puxar_dados_carteira():
    # Exemplo: Aqui você faria uma requisição para sua plataforma
    return """
    Ativos Monitorados: WIN, WDO, DI, DXY, VALE3, PETR4, IFNC, IMAT
    Posição Atual: Comprado 5 WINQ26
    IFNC: +0.45% | DI1F27: -0.12% | DXY: 104.50
    """

st.title("🎓 Mentor de Fluxo Institucional")

# Exibição do Calendário
st.markdown("### 📰 Calendário Econômico do Dia")
st.info(puxar_calendario_macro())

# Botão de análise
if st.button("🔄 Puxar Dados e Analisar Fluxo"):
    with st.spinner("Analisando correlações..."):
        try:
            dados = puxar_dados_carteira()
            agenda = puxar_calendario_macro()
            
            # Histórico de contexto
            contexto = "\n".join(st.session_state.historico_analises[-2:])
            
            prompt = f"""
            Você é um mentor institucional. Analise o fluxo do WIN.
            AGENDA: {agenda}
            DADOS ATUAIS: {dados}
            LEITURAS ANTERIORES: {contexto}
            
            Responda focando em:
            1. Impacto da agenda no fluxo.
            2. Correlação entre DXY, DI e os setores (IFNC/IMAT).
            3. Direção provável e ponto de atenção.
            """
            
            response = model.generate_content(prompt)
            st.session_state.historico_analises.append(response.text)
            
            st.markdown("### 📊 Parecer Institucional")
            st.markdown(response.text)
            
        except Exception as e:
            st.error(f"Erro: {e}")

# Sidebar de controle
if st.sidebar.button("🗑️ Limpar Memória (Novo Pregão)"):
    st.session_state.historico_analises = []
    st.rerun()

with st.sidebar.expander("📜 Histórico de Leituras"):
    for a in st.session_state.historico_analises:
        st.write(a)
        st.divider()

import streamlit as st
import google.generativeai as genai
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from PIL import Image

# Configuração da página
st.set_page_config(page_title="Mentor Institucional", layout="wide")

# Configuração simplificada da API
# O SDK gerencia a versão da API automaticamente ao receber a chave
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Inicialização do modelo
# Se o modelo 'models/gemini-1.5-flash' falhar, 
# tente mudar para 'gemini-1.5-flash' ou 'gemini-1.5-pro'
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Erro ao inicializar o modelo: {e}")

# Função Calendário
@st.cache_data(ttl=3600)
def puxar_calendario():
    try:
        url = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        root = ET.fromstring(response.content)
        
        traducao = {
            "Non-Farm Employment Change": "Payroll (Folha de Pagamento)",
            "Unemployment Rate": "Taxa de Desemprego",
            "Consumer Price Index (CPI)": "IPCA / CPI (Inflação)",
            "Federal Funds Rate": "Decisão de Taxa de Juros (Fed)",
            "GDP": "PIB",
            "Retail Sales": "Vendas no Varejo",
            "Manufacturing PMI": "PMI Industrial",
            "Prelim UoM Consumer Sentiment": "Sentimento do Consumidor UoM",
            "Prelim UoM Inflation Expectations": "Expectativas de Inflação UoM"
        }
        
        hoje = datetime.now().strftime("%m-%d-%Y")
        eventos = []
        for e in root.findall('event'):
            if e.find('date').text == hoje and e.find('impact').text in ['High', 'Medium']:
                titulo = e.find('title').text
                titulo_traduzido = traducao.get(titulo, titulo)
                eventos.append(f"• **{e.find('time').text} ({e.find('country').text})**: {titulo_traduzido}")
        return "\n".join(eventos) if eventos else "Sem eventos de impacto hoje."
    except: return "Calendário indisponível."

# Interface Principal
st.title("🎓 Mentor de Fluxo Institucional")
st.info(f"**Agenda Econômica:**\n{puxar_calendario()}")

uploaded_file = st.file_uploader("Suba o print do Profit/TradingView:", type=['jpg', 'jpeg', 'png'])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Cenário de Mercado", use_column_width=True)
    
    if st.button("🚀 Analisar Fluxo"):
        with st.spinner("Analisando sua tela..."):
            try:
                prompt = f"""
                Analise esta imagem que contém a grade de ativos.
                AGENDA MACRO: {puxar_calendario()}
                
                Sua tarefa:
                1. Identifique a variação dos ativos.
                2. Avalie se o cenário reflete compra ou venda no WIN.
                3. Dê uma recomendação técnica institucional clara.
                """
                response = model.generate_content([prompt, image])
                st.markdown("### 📊 Parecer Institucional")
                st.write(response.text)
                st.session_state.historico.append(response.text)
            except Exception as e:
                st.error(f"Erro na análise: {e}")

# Limpeza
if st.sidebar.button("🗑️ Limpar Sessão"):
    st.session_state.historico = []
    st.rerun()

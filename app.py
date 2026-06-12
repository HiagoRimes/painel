import streamlit as st
import google.generativeai as genai
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from PIL import Image

# Configuração da página
st.set_page_config(page_title="Mentor Institucional", layout="wide")

# Inicializa sessão
if 'historico' not in st.session_state:
    st.session_state.historico = []

# Configuração API
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    # O modelo 'gemini-1.5-flash' é o padrão atual para visão e texto
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Erro ao conectar com a API do Google: {e}")

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
            "Manufacturing PMI": "PMI Industrial"
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

# Interface
st.title("🎓 Mentor de Fluxo WIN")
st.info(f"**Agenda Econômica:**\n{puxar_calendario()}")

uploaded_file = st.file_uploader("Suba o print da sua tela:", type=['jpg', 'jpeg', 'png'])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Print carregado para análise", use_column_width=True)
    
    if st.button("🚀 Analisar Fluxo"):
        with st.spinner("Analisando sua tela e cruzando com a agenda..."):
            try:
                prompt = f"""
                Analise esta imagem que mostra a tela do trader.
                CALENDÁRIO MACRO: {puxar_calendario()}
                
                Sua tarefa:
                1. Identifique a variação de cada ativo na lista (incluindo Juros Futuros, WDO, PETR4, etc).
                2. Avalie se o cenário atual no print reflete uma leitura de compra ou venda.
                3. Dê uma recomendação técnica institucional clara.
                """
                
                response = model.generate_content([prompt, image])
                st.session_state.historico.append(response.text)
                st.markdown("### 📊 Parecer Institucional")
                st.write(response.text)
            except Exception as e:
                st.error(f"Erro na análise: {e}")

# Sidebar
if st.sidebar.button("🗑️ Limpar Sessão"):
    st.session_state.historico = []
    st.rerun()

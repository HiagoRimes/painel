import streamlit as st
import google.generativeai as genai
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from PIL import Image

# Configuração da página
st.set_page_config(page_title="Mentor Institucional", layout="wide")

# Configuração da API - Protegida
api_key = st.secrets.get("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# Tente inicializar o modelo. Caso o nome esteja divergente na sua conta, ele avisará.
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Erro ao carregar o modelo. Verifique se sua chave está ativa no Google AI Studio. Detalhe: {e}")

# Função Calendário (Tradução Inclusa)
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
st.title("🎓 Mentor de Fluxo Institucional")
st.info(f"**Agenda Econômica:**\n{puxar_calendario()}")

uploaded_file = st.file_uploader("Suba o print do Profit/TradingView:", type=['jpg', 'jpeg', 'png'])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Cenário de Mercado", use_column_width=True)
    
    if st.button("🚀 Analisar Fluxo"):
        with st.spinner("Analisando a tela com IA..."):
            try:
                # O prompt é enviado junto com a imagem processada pela PIL
                prompt = f"""
                Você é um mentor de trading. Analise a imagem anexada, que contém a grade de ativos.
                AGENDA MACRO: {puxar_calendario()}
                
                Analise os dados do print (WDO, WIN, Juros, etc) e cruze com a agenda.
                Dê uma leitura institucional: o fluxo está comprador ou vendedor?
                O que a relação entre o print e a agenda indica para a próxima operação?
                """
                
                response = model.generate_content([prompt, image])
                st.markdown("### 📊 Parecer Institucional")
                st.write(response.text)
            except Exception as e:
                st.error(f"Erro ao gerar conteúdo: {e}")

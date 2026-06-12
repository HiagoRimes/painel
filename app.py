import streamlit as st
import google.generativeai as genai
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from PIL import Image

# Configuração da página
st.set_config = st.set_page_config(page_title="Mentor Institucional", layout="wide")

# Configuração da API
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- DETECÇÃO AUTOMÁTICA DE MODELO ---
def get_model():
    # Lista modelos disponíveis que suportam geração de conteúdo
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    # Prioridade de modelos (do mais moderno para o básico)
    prioridade = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro', 'models/gemini-1.0-pro']
    
    for p in prioridade:
        if p in models:
            return genai.GenerativeModel(p)
    
    # Se não achar nenhum da lista, pega o primeiro disponível
    return genai.GenerativeModel(models[0])

try:
    model = get_model()
except Exception as e:
    st.error(f"Erro ao listar modelos: {e}")

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

# Interface
st.title("🎓 Mentor de Fluxo Institucional")
st.info(f"**Agenda Econômica:**\n{puxar_calendario()}")

uploaded_file = st.file_uploader("Suba o print do Profit/TradingView:", type=['jpg', 'jpeg', 'png'])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Cenário de Mercado", use_column_width=True)
    
    if st.button("🚀 Analisar Fluxo"):
        with st.spinner("O Mentor está lendo sua tela..."):
            try:
                prompt = f"""
                Analise esta imagem que contém a grade de ativos.
                AGENDA MACRO: {puxar_calendario()}
                
                Sua tarefa:
                1. Identifique a variação dos ativos.
                2. Avalie se o cenário reflete compra ou venda.
                3. Dê uma recomendação técnica clara.
                """
                response = model.generate_content([prompt, image])
                st.markdown("### 📊 Parecer Institucional")
                st.write(response.text)
            except Exception as e:
                st.error(f"Erro na análise: {e}. Tente novamente.")

# Limpeza
if st.sidebar.button("🗑️ Limpar Sessão"):
    st.rerun()

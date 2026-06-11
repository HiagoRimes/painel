import streamlit as st
import google.generativeai as genai
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from PIL import Image

# Configuração da página
st.set_page_config(page_title="Mentor de Fluxo WIN", layout="wide")

# Inicializa memória
if 'historico' not in st.session_state:
    st.session_state.historico = []

# Configuração API
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash') # Modelo otimizado para visão

# --- CALENDÁRIO AUTOMÁTICO (Mantido) ---
@st.cache_data(ttl=3600)
def puxar_calendario():
    try:
        url = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        root = ET.fromstring(response.content)
        hoje = datetime.now().strftime("%m-%d-%Y")
        eventos = [f"• **{e.find('time').text} ({e.find('country').text})**: {e.find('title').text}" 
                   for e in root.findall('event') if e.find('date').text == hoje and e.find('impact').text in ['High', 'Medium']]
        return "\n".join(eventos) if eventos else "Sem eventos de alto impacto hoje."
    except: return "Calendário indisponível no momento."

st.title("🎓 Mentor de Fluxo WIN (Versão Vision)")

# Exibe calendário sempre no topo
st.info(f"**Agenda Econômica do Dia:**\n{puxar_calendario()}")

# --- ÁREA DE UPLOAD (Seu sistema principal) ---
uploaded_file = st.file_uploader("Cole o print da sua tela aqui...", type=['jpg', 'jpeg', 'png'])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Analisando cenário...", use_column_width=True)
    
    if st.button("🚀 Analisar Fluxo Agora"):
        with st.spinner("Interpretando dados da tela..."):
            prompt = f"""
            Analise este print de tela de um trader.
            CALENDÁRIO MACRO PARA HOJE: {puxar_calendario()}
            
            Sua missão:
            1. Leia os ativos da carteira no print.
            2. Identifique o fluxo principal e a correlação atual.
            3. Dê a diretriz operacional para o WIN.
            """
            response = model.generate_content([prompt, image])
            st.session_state.historico.append(response.text)
            st.markdown("### 📊 Parecer Institucional")
            st.write(response.text)

# Limpeza
if st.sidebar.button("🗑️ Limpar Sessão"):
    st.session_state.historico = []
    st.rerun()

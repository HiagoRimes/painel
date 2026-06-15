import streamlit as st
import google.generativeai as genai
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from PIL import Image
import os

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Mesa Institucional WIN", layout="wide")

# Configuração simples como no código antigo
os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Função simples como no código antigo
def get_model():
    # Sem list_models(), sem v1beta, sem filtro. Apenas instanciar.
    return genai.GenerativeModel('gemini-1.5-flash')

model = get_model()

# --- ESTADO ---
if 'historico' not in st.session_state: 
    st.session_state.historico = []

# --- UTILS ---
@st.cache_data(ttl=1800)
def puxar_calendario():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get("https://nfs.faireconomy.media/ff_calendar_thisweek.xml", headers=headers, timeout=5)
        root = ET.fromstring(resp.content)
        hoje = datetime.now().strftime("%m-%d-%Y")
        evts = [f"{e.find('time').text} ({e.find('country').text}): {e.find('title').text}" 
                for e in root.findall('event') if e.find('date').text == hoje and e.find('impact').text in ['High', 'Medium']]
        return "\n".join(evts) if evts else "Sem eventos macro."
    except: return "Agenda indisponível."

# --- INTERFACE ---
st.title("🎓 Mesa Institucional WIN")
file = st.file_uploader("Upload print:", type=['jpg', 'png'])

if file and st.button("🚀 Executar Análise"):
    with st.spinner("Conectando..."):
        try:
            image = Image.open(file)
            
            # Prompt unificado para não precisar de system_instruction
            prompt = f"""
            Você é uma Mesa Institucional de Operações.
            Analise este print focado em WIN, WDO, DI, ES, NQ, VIX.
            AGENDA: {puxar_calendario()}
            HISTÓRICO: {str(st.session_state.historico[-3:])}
            
            Termine com:
            MEMORIA: VIES=[C/V/N] CONVICCAO=[0-100] MOTOR=[Ativo]
            """
            
            # Chamada direta e simples
            response = model.generate_content([prompt, image])
            
            st.markdown("### 📊 Relatório")
            st.markdown(response.text)
            st.session_state.historico.append(response.text)
            
        except Exception as e:
            st.error(f"Erro: {e}")
            st.write("Dica: Se o erro persistir, o token AQ expirou. Capture um novo.")
            

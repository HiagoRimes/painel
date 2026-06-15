import streamlit as st
import google.generativeai as genai
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from PIL import Image
import os

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Mesa Institucional WIN", layout="wide")

os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

SYSTEM_INST = """Você é uma Mesa Institucional de Operações.
Analise prints do TradingView focado em WIN, WDO, DI, ES, NQ, VIX, IFNC, IMAT, PETR4, B3SA3, EWZ.
REGRAS: 
- Identifique divergências entre WIN e motores. Explique o motivo.
- Quebras de correlação, absorções e transferências de liderança devem ser explicadas tecnicamente.
- Ao final da análise, OBRIGATORIAMENTE termine a resposta com o bloco:
MEMORIA:
VIES=[Compra/Venda/Neutro]
CONVICCAO=[0-100]
MOTOR=[Ativo]
"""

@st.cache_resource
def get_model():
    # Alterado para 'gemini-pro' para máxima compatibilidade em contas organizacionais
    return genai.GenerativeModel('gemini-pro')

model = get_model()

# --- ESTADO ---
if 'historico' not in st.session_state: 
    st.session_state.historico = []

def adicionar_historico(item):
    if len(st.session_state.historico) >= 3:
        st.session_state.historico.pop(0)
    st.session_state.historico.append(item)

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

def preparar_imagem(file):
    img = Image.open(file)
    if img.width < 500 or img.height < 400:
        raise ValueError("Resolução insuficiente.")
    img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
    return img.convert("RGB") if img.mode != "RGB" else img

def processar_memoria(texto):
    match = re.search(r"MEMORIA:\s*VIES=(.*?)\s*CONVICCAO=([0-9.,%]+)\s*MOTOR=(.*)$", texto, re.MULTILINE | re.IGNORECASE)
    return f"{match.group(1).strip()} | {match.group(2).strip()} | {match.group(3).strip()}" if match else None

# --- INTERFACE ---
st.title("🎓 Mesa Institucional WIN")
periodo = "Pré-mercado" if datetime.now().hour < 9 else "Mercado aberto" if datetime.now().hour < 17 else "Pós-fechamento"
file = st.file_uploader("Upload print do TradingView:", type=['jpg', 'png'])

if file and st.button("🚀 Executar Análise"):
    with st.spinner("Analisando fluxo institucional..."):
        try:
            img = preparar_imagem(file)
            hist = "\n".join(st.session_state.historico)
            prompt_var = f"{SYSTEM_INST}\n\nHORÁRIO: {periodo} | AGENDA: {puxar_calendario()} | HISTÓRICO: {hist}"
            
            # Chamada direta
            res = model.generate_content([prompt_var, img])
            
            if res.text:
                st.markdown(res.text)
                nova_memoria = processar_memoria(res.text)
                if nova_memoria:
                    adicionar_historico(nova_memoria)
            else:
                st.warning("Análise bloqueada ou vazia.")
                    
        except Exception as e:
            if "ResourceExhausted" in str(e):
                st.error("🚨 Cota excedida! Aguarde alguns instantes.")
            elif "401" in str(e):
                st.error("🚨 Token expirado! Atualize seu token AQ.")
            else:
                st.error(f"Falha técnica: {str(e)}")
        

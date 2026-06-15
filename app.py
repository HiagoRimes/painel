import streamlit as st
import google.generativeai as genai
from google.api_core import exceptions
import requests
import xml.etree.ElementTree as ET
import re
import os
from datetime import datetime
from PIL import Image
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Mesa Institucional WIN", layout="wide")

# Força o SDK a ler a chave do secrets
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
    # Usando 1.5-flash pela maior estabilidade de cota no nível gratuito
    return genai.GenerativeModel("gemini-1.5-flash")

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
    img.thumbnail((1024, 1024), Image.Resampling.LANCZOS) # Redução leve para economizar cota
    return img.convert("RGB") if img.mode != "RGB" else img

def processar_memoria(texto):
    match = re.search(r"MEMORIA:\s*VIES=(.*?)\s*CONVICCAO=([0-9.,%]+)\s*MOTOR=(.*)$", texto, re.MULTILINE | re.IGNORECASE)
    return f"{match.group(1).strip()} | {match.group(2).strip()} | {match.group(3).strip()}" if match else None

# --- RETRY POLICY (Aumentada para respeitar limites de cota) ---
@retry(
    stop=stop_after_attempt(5), 
    wait=wait_exponential(multiplier=5, min=10, max=40),
    retry=retry_if_exception_type((exceptions.ResourceExhausted, exceptions.ServiceUnavailable))
)
def gerar_analise_segura(prompt, img):
    return model.generate_content([prompt, img], request_options={"timeout": 60})

# --- INTERFACE ---
st.title("🎓 Mesa Institucional WIN")
periodo = "Pré-mercado" if datetime.now().hour < 9 else "Mercado aberto" if datetime.now().hour < 17 else "Pós-fechamento"
file = st.file_uploader("Upload print do TradingView:", type=['jpg', 'png'])

if file and st.button("🚀 Executar Análise"):
    with st.spinner("Analisando fluxo institucional..."):
        try:
            img = preparar_imagem(file)
            hist = "\n".join(st.session_state.historico)
            
            # Incorporação da instrução no prompt para evitar erro 401/permissão
            prompt_var = f"{SYSTEM_INST}\n\nHORÁRIO: {periodo} | AGENDA: {puxar_calendario()} | HISTÓRICO: {hist}"
            
            res = gerar_analise_segura(prompt_var, img)
            
            if res.candidates and res.candidates[0].finish_reason == genai.types.FinishReason.STOP:
                st.markdown(res.text)
                nova_memoria = processar_memoria(res.text)
                if nova_memoria:
                    adicionar_historico(nova_memoria)
            else:
                st.warning("Análise bloqueada ou incompleta.")
                    
        except Exception as e:
            if "ResourceExhausted" in str(e):
                st.error("🚨 Cota excedida! O Google limitou suas requisições temporariamente. Aguarde 1 minuto e tente novamente.")
            elif "401" in str(e):
                st.error("🚨 Token expirado! Atualize seu token AQ no secrets.")
            else:
                st.error(f"Falha técnica: {str(e)}")
    

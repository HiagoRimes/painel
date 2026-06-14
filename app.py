import streamlit as st
import google.generativeai as genai
from google.api_core import exceptions
import requests
import xml.etree.ElementTree as ET
import re
from datetime import datetime
from PIL import Image
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Mesa Institucional WIN", layout="wide")
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

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
    return genai.GenerativeModel("gemini-2.0-flash", system_instruction=SYSTEM_INST)

model = get_model()

# --- ESTADO (Serialização Sênior) ---
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
        raise ValueError("Resolução insuficiente para análise institucional.")
    img.thumbnail((1536, 1536), Image.Resampling.LANCZOS)
    return img.convert("RGB") if img.mode != "RGB" else img

def processar_memoria(texto):
    match = re.search(r"MEMORIA:\s*VIES=(.*?)\s*CONVICCAO=([0-9.,%]+)\s*MOTOR=(.*)$", texto, re.MULTILINE | re.IGNORECASE)
    return f"{match.group(1).strip()} | {match.group(2).strip()} | {match.group(3).strip()}" if match else None

# --- RETRY POLICY (Proteção contra ResourceExhausted) ---
@retry(
    stop=stop_after_attempt(3), 
    wait=wait_exponential(multiplier=2, min=4, max=20),
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
            prompt_var = f"HORÁRIO: {periodo} | AGENDA: {puxar_calendario()} | HISTÓRICO: {hist}"
            
            res = gerar_analise_segura(prompt_var, img)
            
            if res.candidates and res.candidates[0].finish_reason == genai.types.FinishReason.STOP:
                st.markdown(res.text)
                nova_memoria = processar_memoria(res.text)
                if nova_memoria:
                    adicionar_historico(nova_memoria)
            else:
                st.warning(f"Análise limitada: {res.candidates[0].finish_reason.name if res.candidates else 'Erro crítico'}")
                    
        except Exception as e:
            if "ResourceExhausted" in str(e):
                st.error("🚨 Limite de cota atingido! Aguarde alguns instantes ou verifique seu plano no Google AI Studio.")
            elif "finish_reason" in str(e).lower() or "safety" in str(e).lower():
                st.warning("A análise foi bloqueada por diretrizes de segurança.")
            else:
                st.error(f"Falha técnica na mesa: {str(e)}")
    

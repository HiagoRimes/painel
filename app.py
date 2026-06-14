import streamlit as st
import google.generativeai as genai
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from PIL import Image

# Configuração da Página
st.set_page_config(page_title="Mesa Institucional WIN", layout="wide")

# --- CONFIGURAÇÃO API ---
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

def get_model():
    # Configuração de segurança conforme solicitado
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]
    
    # Lista de modelos solicitada (priorizando 2.5 e 1.5-pro)
    prioridade = ['gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-1.5-pro']
    
    for p in prioridade:
        try:
            return genai.GenerativeModel(p, safety_settings=safety_settings)
        except:
            continue
    return genai.GenerativeModel('gemini-1.5-pro', safety_settings=safety_settings)

model = get_model()

# --- PROMPT MESTRE ---
PROMPT_SISTEMA = """
Você é um Analista Institucional especializado em fluxo, correlação e dominância.
Sua função é explicar a dinâmica de força entre ativos e o impacto no WIN.
REGRA MESTRA: WIN é consequência. Fluxo real sempre vence.

ANALISE OS ATIVOS: WIN, WDO, DI, ES, NQ, VIX, IFNC, IMAT, PETR4, B3SA3, EWZ.
(Se não identificado no print, informe "Não identificado no print").

ESTRUTURA OBRIGATÓRIA DA RESPOSTA:

CAPÍTULO 1 – CONTEXTO DO DIA
- Eventos
- Notícias
- Ambiente predominante
- Conclusão

CAPÍTULO 2 – PAINEL DE FORÇAS
(Para cada ativo: Ativo, Direção, Força, Impacto no WIN)
Classificar: 🔴 Dominância Forte, 🟠 Dominância Moderada, ⚪ Neutro.

CAPÍTULO 3 – HIERARQUIA DE DOMINÂNCIA
- Motor Principal, Secundário, Terciário
- Direção, Intensidade, Dominância estimada, Justificativa.

CAPÍTULO 4 – TRANSMISSÃO DE FLUXO
- Quem lidera, ajuda, atrapalha, ignorado.
- Absorção, conflito, transferência de liderança.

CAPÍTULO 5 – CORRELAÇÕES
(DI, WDO, EWZ, IFNC, IMAT, ES/NQ x WIN)
Classificar: Muito Forte, Forte, Moderada, Fraca, Muito Fraca.
Informar: Correlação Dominante, Em Transferência, Ignorada.

CAPÍTULO 6 – QUALIDADE DO CENÁRIO
- Classificação (Excelente a Péssima)
- Convicção (0-100)

CAPÍTULO 7 – RESUMO OPERACIONAL
- Viés Atual (Compra/Venda/Neutro)
- Convicção, Motor Dominante, Motor Ignorado, Principal Correlação, Principal Risco.

CAPÍTULO 8 – MODO PROFESSOR
- O que moveu o mercado, Erro comum do iniciante, O que observar primeiro, Principal lição institucional.

REGRAS ABSOLUTAS: Não descrever individualmente, focar em dominância/fluxo. Explicar sempre o WIN.
"""

@st.cache_data(ttl=1800)
def puxar_calendario():
    try:
        url = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        root = ET.fromstring(response.content)
        hoje_dt = datetime.now()
        eventos = [f"• {e.find('time').text} ({e.find('country').text}): {e.find('title').text}" 
                   for e in root.findall('event') if e.find('date').text == hoje_dt.strftime("%m-%d-%Y")]
        return "\n".join(eventos) if eventos else "Sem eventos hoje."
    except: return "Calendário indisponível."

# --- INTERFACE ---
st.title("🎓 Mesa Institucional WIN")
st.info(f"📅 Agenda: {puxar_calendario()}")

uploaded_file = st.file_uploader("Suba o print do TradingView:", type=['jpg', 'png'])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, use_column_width=True)
    
    if st.button("🚀 Executar Análise Institucional"):
        with st.spinner("Decodificando dominância..."):
            try:
                response = model.generate_content([PROMPT_SISTEMA, image])
                st.markdown("---")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Erro na Mesa Institucional: {e}")

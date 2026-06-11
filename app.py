import streamlit as st
import google.generativeai as genai
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from PIL import Image

# Configuração da página
st.set_page_config(page_title="Mentor de Fluxo WIN", layout="wide")

# Inicializa memória da sessão
if 'historico' not in st.session_state:
    st.session_state.historico = []

# Configuração API do Google
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# --- FUNÇÃO DO CALENDÁRIO COM TRADUÇÃO ---
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
    except: 
        return "Calendário indisponível."

# --- INTERFACE ---
st.title("🎓 Mentor de Fluxo Institucional")

# Exibe o Calendário no topo
st.info(f"**📰 Agenda Econômica de Hoje:**\n{puxar_calendario()}")

# Upload de Imagem
uploaded_file = st.file_uploader("Suba o print do seu Profit/TradingView...", type=['jpg', 'jpeg', 'png'])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Cenário Atual", use_column_width=True)
    
    if st.button("🚀 Analisar Fluxo e Montar Tese"):
        with st.spinner("O Mentor está processando os dados..."):
            prompt = f"""
            Você é um trader institucional sênior. Analise o print enviado e a agenda abaixo.
            AGENDA MACRO: {puxar_calendario()}
            
            Protocolo de Resposta:
            1. CONTEXTO: Como a agenda impacta o fluxo atual?
            2. LEITURA DE TELA: Analise os ativos, volume e preços presentes no print.
            3. DIVERGÊNCIAS: Há sinais de exaustão ou absorção?
            4. Veredito: Direção provável e regra de bolso para a próxima operação.
            """
            
            response = model.generate_content([prompt, image])
            st.session_state.historico.append(response.text)
            st.markdown("### 📊 Parecer Institucional")
            st.write(response.text)

# Barra Lateral de Controle
with st.sidebar:
    st.title("⚙️ Controle")
    if st.button("🗑️ Limpar Sessão"):
        st.session_state.historico = []
        st.rerun()
    
    if st.session_state.historico:
        st.subheader("📜 Diário de Bordo")
        for i, analise in enumerate(reversed(st.session_state.historico)):
            st.markdown(f"**Leitura {len(st.session_state.historico) - i}**")
            st.write(analise[:150] + "...") # Preview
            st.divider()

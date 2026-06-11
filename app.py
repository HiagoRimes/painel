import streamlit as st
import google.generativeai as genai
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Mentor Institucional WIN", layout="wide")

# Inicializa a memória
if 'historico_analises' not in st.session_state:
    st.session_state.historico_analises = []

# Configuração do Gemini
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    model_name = 'gemini-3.5-flash' 
    model = genai.GenerativeModel(model_name)
except Exception as e:
    st.error("Configuração de API pendente nas Secrets.")
    st.stop()

# --- NOVA FUNÇÃO AUTOMÁTICA: Calendário Econômico (Forex Factory) ---
@st.cache_data(ttl=3600) # Salva no cache por 1 hora para evitar bloqueios do servidor
def puxar_calendario_macro():
    try:
        url = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        root = ET.fromstring(response.content)

        # O servidor XML usa o fuso horário americano, mas as datas são precisas
        hoje_str = datetime.now().strftime("%m-%d-%Y") 
        eventos = []

        for event in root.findall('event'):
            data_evento = event.find('date').text
            impacto = event.find('impact').text
            
            # Filtra apenas o dia de hoje e notícias relevantes (High/Medium)
            if data_evento == hoje_str and impacto in ['High', 'Medium']:
                hora = event.find('time').text
                moeda = event.find('country').text
                titulo = event.find('title').text
                eventos.append(f"[{moeda}] {hora} - {titulo} (Impacto: {impacto})")

        if not eventos:
            return "Nenhum evento macro de alto impacto previsto para hoje."
        return "\n".join(eventos)
    except Exception as e:
        return f"Sistema operando às cegas. Falha ao puxar calendário: {e}"

# Executa a busca do calendário assim que o app abre
agenda_do_dia = puxar_calendario_macro()

# Seu Protocolo Base
PROTOCOL_FINAL = """
Você é um mentor de trading institucional de alta performance focado no ativo WIN.
Siga rigorosamente este protocolo:

1. CONTEXTO DO DIA: Avalie a agenda macroeconômica fornecida.
2. CONTEXTO DA CARTEIRA: Analise a posição atual, saldo e exposição.
3. ESTADO DOS MOTORES: Macro, Externo e Interno (com base nos dados).
4. TRANSMISSÃO DE FLUXO: Mecanismo dominante.
5. ESTADO FINAL DO MERCADO: Direção provável e decisão operacional.
6. MODO PROFESSOR: Erro típico, padrão de aprendizado e regra prática.
"""

st.title("🎓 Mentor de Fluxo WIN")

# --- EXIBIÇÃO DA AGENDA (Automático) ---
st.markdown("### 📰 Contexto Macro (API Automática)")
st.info(f"**Eventos de Hoje:**\n\n{agenda_do_dia}")
st.markdown("---")

# --- ÁREA DA API DA CARTEIRA ---
st.markdown("### 💼 Sincronização de Carteira")

def puxar_dados_api():
    # Substitua futuramente pela API da sua plataforma
    return """
    Ativo: WINQ26
    Posição: Comprado em 5 minicontratos
    Preço Médio: 125.400
    Resultado Aberto: + R$ 150,00
    IFNC: +0.45% | DI1F27: -0.12% | WDO: -0.20%
    """

if st.button("🔄 Puxar Dados da Corretora e Analisar"):
    with st.spinner("Analisando fluxo institucional..."):
        try:
            dados_atuais = puxar_dados_api()
            
            # Exibe os dados crus na tela
            st.success(f"**Leitura de Plataforma OK:**\n{dados_atuais}")

            # Monta o histórico intraday
            contexto_intraday = ""
            if len(st.session_state.historico_analises) > 0:
                contexto_intraday = "HISTÓRICO DAS ANÁLISES HOJE:\n"
                for i, analise in enumerate(st.session_state.historico_analises[-3:]):
                    contexto_intraday += f"--- Leitura Anterior {i+1} ---\n{analise}\n\n"
                contexto_intraday += "INSTRUÇÃO: Com base nas leituras anteriores, calendário macro e NOVOS DADOS, atualize a tese. O mercado confirmou a leitura?\n\n"

            # Junta TUDO no prompt invisível (Agenda + Protocolo + Histórico + Dados)
            prompt_completo = f"AGENDA MACRO HOJE:\n{agenda_do_dia}\n\n{PROTOCOL_FINAL}\n\n{contexto_intraday}\n\nDADOS DA PLATAFORMA AGORA:\n{dados_atuais}"
            
            response = model.generate_content(prompt_completo)
            st.session_state.historico_analises.append(response.text)
            
            st.markdown("### 📊 Mentoria e Diretriz Operacional")
            st.markdown(response.text)
            
        except Exception as e:
            st.error(f"Erro na análise: {e}")

# Gestão de Memória
st.sidebar.markdown("### 🧠 Gestão Intraday")
if st.sidebar.button("🗑️ Fim do Pregão (Limpar Memória)"):
    st.session_state.historico_analises = []
    st.cache_data.clear() # Limpa o cache da API do calendário também
    st.sidebar.success("Memória e APIs zeradas para o próximo pregão!")

if len(st.session_state.historico_analises) > 0:
    st.sidebar.markdown("---")
    with st.sidebar.expander("📜 Diário de Bordo (Hoje)"):
        for i, analise in enumerate(st.session_state.historico_analises):
            st.markdown(f"**Leitura {i+1}**")
            st.markdown(analise)
            st.markdown("---")

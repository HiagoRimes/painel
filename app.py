import streamlit as st
import yfinance as yf
from google import genai
import pandas as pd
from datetime import datetime
import time

# ==============================================================================
# CONFIGURAÇÃO INTERFACE E AMBIENTE
# ==============================================================================
st.set_page_config(
    page_title="Mesa Quant - Protocolo Mestre WIN", 
    page_icon="🔮", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização customizada em CSS para visual de Mesa de Operações
st.markdown("""
    <style>
    .reportview-container { background: #0e1117; }
    .metric-box {
        background-color: #161b22;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #30363d;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🔮 Monitor Quantitativo Autônomo — WIN M15")
st.caption("Conectado via API ao Yahoo Finance | Inteligência de Fluxo Institucional")

if "GEMINI_API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("❌ ERRO: Configure a sua 'GEMINI_API_KEY' nos Secrets.")
    st.stop()

# ==============================================================================
# PROMPT MESTRE INTEGRAL (PADRÃO MESA DE OPERAÇÕES)
# ==============================================================================
PROMPT_MESTRE = """
Atue como um analista técnico e de fluxo institucional. Processar grade abaixo e retornar relatório em 22 blocos:

1. 📊 AGENDA ECONÔMICA, NOTÍCIAS E MATRIZ DE IMPACTO
2. 📈 GRADE DE VARIAÇÃO (O SEMÁFORO VISUAL)
3. 🛡️ FILTROS DE CORRELAÇÃO E VALIDAÇÃO
4. 🎯 DIAGNÓSTICO DO WIN
5. 👑 HIERARQUIA DE DOMINÂNCIA (DRIVERS DO MERCADO)
6. 🌐 ANÁLISE DE DOMINÂNCIA MACRO
7. 🧩 FRAGMENTAÇÃO OU CONCENTRAÇÃO
8. ⚙️ REGIME DE MERCADO
9. ⚔️ CONFLITOS ENTRE MOTORES
10. 🔥 ÍNDICE DE CONVICÇÃO DO CENÁRIO
11. 🎯 DIAGNÓSTICO PROFISSIONAL FINAL
12. 🎯 FATOR DOMINANTE DO DIA
13. ⚠️ FALHAS DE CORRELAÇÃO
14. 🔄 TRANSFERÊNCIA DE LIDERANÇA
15. ⚙️ PLAYBOOK OPERACIONAL DO AMBIENTE
16. 🏛️ FLUXO ESTRANGEIRO (QUALIDADE DO MOVIMENTO)
17. ⏳ CONTINUIDADE OU ESGOTAMENTO
18. 🚨 ALERTAS INSTITUCIONAIS
19. 🏦 CURVA DE JUROS E PRESSÃO MACRO
20. 🌎 REGIME GLOBAL DE RISCO
21. 🎯 PLACAR INSTITUCIONAL DE FORÇAS
22. 📉 FORÇA DA CORRELAÇÃO INSTITUCIONAL

DADOS: {grade_dados}
NOTÍCIAS: {noticias}

REGRA MESTRA: Trate o WIN como consequência. Quem lidera? Quem ajuda? Quem ignora?
"""

# ==============================================================================
# MOTOR DE CAPTURA DE DADOS (DADOS MESTRES)
# ==============================================================================
def engine_coleta_dados():
    ativos = {
        "WIN (Ibov via BOVA11)": "BOVA11.SA",
        "WDO (Dólar Comercial)": "BRL=X",
        "PETR4": "PETR4.SA",
        "B3SA3": "B3SA3.SA",
        "ITUB4 (Proxy IFNC)": "ITUB4.SA",
        "VALE3 (Proxy IMAT)": "VALE3.SA",
        "EWZ (ETF Brasil)": "EWZ",
        "S&P 500 Futuro": "ES=F",
        "NASDAQ Futuro": "NQ=F",
        "VIX (Índice do Medo)": "^VIX"
    }
    
    grade_texto = ""
    resumo_sidebar = {}
    bloco_noticias = ""
    
    for nome, ticker in ativos.items():
        try:
            ticker_obj = yf.Ticker(ticker)
            df = ticker_obj.history(period="5d")
            if not df.empty and len(df) >= 2:
                var = ((df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
                grade_texto += f"- {nome}: {var:+.2f}%\n"
                resumo_sidebar[nome] = f"{var:+.2f}%"
            else:
                grade_texto += f"- {nome}: N/A\n"
        except:
            grade_texto += f"- {nome}: Erro\n"
    return grade_texto, resumo_sidebar, bloco_noticias

# ==============================================================================
# EXECUÇÃO DO PROTOCOLO MESTRE
# ==============================================================================
st.sidebar.header("📊 Grade de Cotações Real-Time")
grade_dados, mini_dashboard, noticias = engine_coleta_dados()

for ativo, var in mini_dashboard.items():
    st.sidebar.markdown(f"**{ativo}**: `{var}`")

if st.sidebar.button("🔄 Forçar Recalibragem"):
    if "cache" in st.session_state: del st.session_state["cache"]
    st.rerun()

if "ultima_exec" not in st.session_state:
    st.session_state["ultima_exec"] = datetime.min
    st.session_state["cache"] = ""

tempo_passado = (datetime.now() - st.session_state["ultima_exec"]).total_seconds()

if tempo_passado > 850 or not st.session_state["cache"]:
    with st.spinner("🤖 Executando Modelo de Inteligência Institucional..."):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=PROMPT_MESTRE.format(grade_dados=grade_dados, noticias=noticias)
            )
            st.session_state["cache"] = response.text
            st.session_state["ultima_exec"] = datetime.now()
        except Exception as e:
            st.error(f"Erro na API: {e}")

st.markdown(st.session_state["cache"])

time.sleep(900)
st.rerun()
        

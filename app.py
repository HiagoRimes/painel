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

# Estilização customizada em CSS
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
    st.error("❌ ERRO: Configure a sua 'GEMINI_API_KEY' nos Secrets do Streamlit.")
    st.stop()

# ==============================================================================
# PROMPT MESTRE (INTEGRAL - 22 BLOCOS)
# ==============================================================================
PROMPT_MESTRE = """
Atue como um analista técnico e de fluxo institucional de mercado financeiro, focado em Day Trade no minicontrato de Índice Bovespa (WIN). Toda vez que eu te enviar a grade de cotações por texto com as variações reais colhidas da API, você deve processar esses dados e me retornar OBRIGATORIAMENTE um relatório cirúrgico estruturado exatamente nos 22 passos abaixo:

1. 📊 AGENDA ECONÔMICA, NOTÍCIAS E MATRIZ DE IMPACTO
2. 📈 GRADE DE VARIAÇÃO (O SEMÁFORO VISUAL)
3. 🛡️ FILTROS DE CORRELAÇÃO E VALIDAÇÃO (AS TRAVAS DE SEGURANÇA)
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

REGRA MESTRA: Trate sempre o WIN como consequência dos drivers. Identifique quem lidera e quem ignora.
DADOS: {grade_dados} | NOTÍCIAS: {noticias}
"""

# ==============================================================================
# MOTOR DE CAPTURA DE DADOS (COM FALLBACK)
# ==============================================================================
def engine_coleta_dados():
    # Lista completa de ativos com lista de alternativas para evitar o erro de fonte
    ativos = {
        "WIN (Ibov via BOVA11)": ["BOVA11.SA"],
        "WDO (Dólar Comercial)": ["BRL=X"],
        "PETR4": ["PETR4.SA"],
        "B3SA3": ["B3SA3.SA"],
        "ITUB4 (Proxy IFNC)": ["ITUB4.SA"],
        "VALE3 (Proxy IMAT)": ["VALE3.SA"],
        "EWZ (ETF Brasil)": ["EWZ"],
        "S&P 500 Futuro": ["ES=F", "^GSPC"],
        "NASDAQ Futuro": ["NQ=F", "^IXIC"],
        "VIX": ["^VIX"]
    }
    
    grade_texto = ""
    resumo_sidebar = {}
    bloco_noticias = ""
    
    for nome, tickers in ativos.items():
        sucesso = False
        for t in tickers:
            try:
                ticker_obj = yf.Ticker(t)
                df = ticker_obj.history(period="5d")
                if not df.empty and len(df) >= 2:
                    var = ((df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
                    grade_texto += f"- {nome}: {var:+.2f}%\n"
                    resumo_sidebar[nome] = f"{var:+.2f}%"
                    sucesso = True
                    break
            except: continue
        if not sucesso:
            grade_texto += f"- {nome}: N/A\n"
            resumo_sidebar[nome] = "Erro"
            
    return grade_texto, resumo_sidebar, ""

# ==============================================================================
# EXECUÇÃO DO PROTOCOLO MESTRE
# ==============================================================================
st.sidebar.header("📊 Grade de Cotações Real-Time")
grade_dados, mini_dashboard, noticias = engine_coleta_dados()

for ativo, var in mini_dashboard.items():
    st.sidebar.markdown(f"**{ativo}**: `{var}`")

# Bloqueio para evitar 429
if "ultima_execucao" not in st.session_state:
    st.session_state["ultima_execucao"] = datetime.min
    st.session_state["analise_cache"] = ""

tempo_passado = (datetime.now() - st.session_state["ultima_execucao"]).total_seconds()

if tempo_passado > 850 or not st.session_state["analise_cache"]:
    with st.spinner("🤖 Executando Modelo de Inteligência Institucional..."):
        try:
            # Modelo 1.5-flash pela alta estabilidade
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=PROMPT_MESTRE.format(grade_dados=grade_dados, noticias=noticias)
            )
            st.session_state["analise_cache"] = response.text
            st.session_state["ultima_execucao"] = datetime.now()
        except Exception as e:
            if "503" in str(e):
                time.sleep(30)
                st.rerun()
            else:
                st.error(f"Erro na API: {e}")

st.markdown(st.session_state["analise_cache"])

time.sleep(900)
st.rerun()
            

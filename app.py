import streamlit as st
import yfinance as yf
from google import genai
import pandas as pd
from datetime import datetime, timedelta
import time
import sys

# ==============================================================================
# CONFIGURAÇÃO DE AMBIENTE E INTERFACE (COMPLETO)
# ==============================================================================
st.set_page_config(
    page_title="Mesa Quant - Protocolo Mestre WIN", 
    page_icon="🔮", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS completa da sua mesa
st.markdown("""
    <style>
    .reportview-container { background: #0e1117; color: #e6edf3; }
    .metric-box { background-color: #161b22; padding: 20px; border-radius: 12px; border: 1px solid #30363d; margin: 10px; }
    .stApp { background-color: #0d1117; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔮 Monitor Quantitativo Autônomo — WIN M15")
st.subheader("Inteligência de Fluxo Institucional | API Yahoo Finance")

# Inicialização com verificação de segurança
if "GEMINI_API_KEY" in st.secrets:
    try:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    except Exception as e:
        st.error(f"Erro ao inicializar o Client: {e}")
        st.stop()
else:
    st.error("❌ ERRO: GEMINI_API_KEY não configurada nos Secrets.")
    st.stop()

# ==============================================================================
# PROMPT MESTRE INTEGRAL (OS 22 BLOCOS - CÓDIGO ORIGINAL)
# ==============================================================================
PROMPT_MESTRE = """
Atue como analista técnico e de fluxo institucional de mercado financeiro. Processe os dados abaixo seguindo rigorosamente os 22 passos de análise:
1. 📊 Agenda e Notícias | 2. 📈 Grade de Variação | 3. 🛡️ Filtros e Validações | 4. 🎯 Diagnóstico WIN | 5. 👑 Hierarquia | 6. 🌐 Macro | 7. 🧩 Fragmentação | 8. ⚙️ Regime | 9. ⚔️ Conflitos | 10. 🔥 Convicção | 11. 🎯 Final Profissional | 12. 🎯 Fator Dominante | 13. ⚠️ Falhas de Correlação | 14. 🔄 Transferência de Liderança | 15. ⚙️ Playbook Operacional | 16. 🏛️ Fluxo Estrangeiro | 17. ⏳ Continuidade/Esgotamento | 18. 🚨 Alertas Institucionais | 19. 🏦 Curva de Juros | 20. 🌎 Risco Global | 21. 🎯 Placar Institucional | 22. 📉 Força das Correlações.

REGRA MESTRA: Trate o WIN como consequência. Responda com foco técnico, sem subjetividade.
DADOS: {grade_dados}
NOTÍCIAS: {noticias}
"""

# ==============================================================================
# ENGINE DE COLETA DE DADOS (COMPLETO)
# ==============================================================================
def engine_coleta_dados():
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
        "VIX (Índice do Medo)": ["^VIX"]
    }
    grade_texto, resumo_sidebar, bloco_noticias = "", {}, ""
    for nome, tickers in ativos.items():
        for t in tickers:
            try:
                ticker_obj = yf.Ticker(t)
                hist = ticker_obj.history(period="5d")
                if len(hist) >= 2:
                    var = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
                    grade_texto += f"- {nome}: {var:+.2f}%\n"
                    resumo_sidebar[nome] = f"{var:+.2f}%"
                    if t in ["BOVA11.SA", "ES=F"] and not bloco_noticias:
                        bloco_noticias = "\n📰 News: " + str(ticker_obj.news[:2])
                    break
            except: continue
    return grade_texto, resumo_sidebar, bloco_noticias

# ==============================================================================
# EXECUÇÃO DO PROTOCOLO MESTRE
# ==============================================================================
if "analise" not in st.session_state: st.session_state["analise"] = ""

st.sidebar.header("📊 Grade de Dados")
grade, dash, news = engine_coleta_dados()

for ativo, val in dash.items():
    st.sidebar.markdown(f"**{ativo}**: `{val}`")

if st.sidebar.button("🔄 Executar Protocolo Mestre"):
    with st.spinner("Analisando fluxo institucional..."):
        try:
            # AQUI ESTÁ A CORREÇÃO DE COTA: 
            # Enviamos apenas o necessário, evitando redundância de tokens.
            msg = PROMPT_MESTRE.format(grade_dados=grade, noticias=news)
            
            # Limite preventivo para não ultrapassar tokens da cota gratuita
            if len(msg) > 15000: 
                msg = msg[:15000] + "\n[...Truncado para preservar cota...]"
            
            resp = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=msg
            )
            st.session_state["analise"] = resp.text
        except Exception as e:
            st.error(f"Erro de Execução (Verifique sua cota): {e}")

if st.session_state["analise"]:
    st.markdown(st.session_state["analise"])

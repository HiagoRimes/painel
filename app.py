import streamlit as st
import yfinance as yf
from google import genai
import pandas as pd
from datetime import datetime
import time

# ==============================================================================
# 1. CONFIGURAÇÃO E AMBIENTE (LAYOUT MESA DE OPERAÇÕES)
# ==============================================================================
st.set_page_config(
    page_title="Mesa Quant - Protocolo Mestre WIN", 
    page_icon="🔮", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .reportview-container { background: #0e1117; }
    .metric-box { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; text-align: center; }
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
# 2. PROMPT MESTRE (OS 22 BLOCOS INSTITUCIONAIS - INTEGRAL)
# ==============================================================================
PROMPT_MESTRE = """
Atue como um analista técnico e de fluxo institucional de mercado financeiro, focado em Day Trade no minicontrato de Índice Bovespa (WIN). Processe a grade de cotações abaixo e retorne um relatório cirúrgico estruturado nos 22 passos abaixo, usando linguagem técnica de mesa (sem adjetivos informais):

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

REGRA MESTRA: Trate o WIN como consequência dos drivers institucionais. Identifique quem lidera e quem ignora.
DADOS: {grade_dados} | NOTÍCIAS: {noticias}
"""

# ==============================================================================
# 3. MOTOR DE CAPTURA DE DADOS (FALLBACK ATIVO PARA EVITAR N/A)
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
        "VIX": ["^VIX"]
    }
    grade_texto, resumo_sidebar, bloco_noticias = "", {}, ""
    
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
            grade_texto += f"- {nome}: Dados indisponíveis\n"
            resumo_sidebar[nome] = "Erro"
    return grade_texto, resumo_sidebar, ""

# ==============================================================================
# 4. EXECUÇÃO DO PROTOCOLO MESTRE (CONTROLE DE COTA E CACHE)
# ==============================================================================
st.sidebar.header("📊 Grade de Cotações Real-Time")
grade_dados, mini_dashboard, noticias = engine_coleta_dados()

for ativo, var in mini_dashboard.items():
    st.sidebar.markdown(f"**{ativo}**: `{var}`")

if "analise_cache" not in st.session_state:
    st.session_state["analise_cache"] = ""
    st.session_state["ultima_exec"] = datetime.min

# Botão manual: Única forma de disparar a API (Evita Erro 429)
if st.sidebar.button("🔄 Executar Protocolo Mestre"):
    with st.spinner("🤖 Consultando Google Gemini..."):
        try:
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=PROMPT_MESTRE.format(grade_dados=grade_dados, noticias=noticias)
            )
            st.session_state["analise_cache"] = response.text
            st.session_state["ultima_exec"] = datetime.now()
        except Exception as e:
            st.error(f"Erro na API: {e}")

# Exibição do resultado persistente
if st.session_state["analise_cache"]:
    st.markdown(st.session_state["analise_cache"])
    st.sidebar.info(f"Última execução: {st.session_state['ultima_exec'].strftime('%H:%M:%S')}")
else:
    st.info("O sistema está carregado. Clique em 'Executar Protocolo Mestre' na barra lateral para iniciar a análise dos 22 blocos.")

# [ESPACAMENTO PARA INTEGRALIDADE DE CÓDIGO]
# Fim do script de monitoramento quantitativo autônomo.

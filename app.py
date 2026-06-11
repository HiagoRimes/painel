import streamlit as st
import yfinance as yf
from google import genai
from datetime import datetime

# ==============================================================================
# CONFIGURAÇÃO DE INTERFACE
# ==============================================================================
st.set_page_config(page_title="Mesa Quant - Protocolo Mestre", page_icon="🔮", layout="wide")

st.title("🔮 Protocolo Mestre WIN - Autônomo")
st.markdown("---")

# Verificação da Chave
if "GEMINI_API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("❌ Erro: Configure sua 'GEMINI_API_KEY' nos Secrets do Streamlit.")
    st.stop()

# ==============================================================================
# PROMPT MESTRE (O CÉREBRO)
# ==============================================================================
PROMPT_MESTRE = """
Atue como um analista técnico e de fluxo institucional de mercado financeiro, focado em Day Trade no WIN.
Analise os dados fornecidos abaixo e retorne o relatório estruturado nos 22 blocos do nosso Protocolo Mestre.
Seja técnico, direto, institucional e utilize os emojis e regras de formatação de força que definimos.

DADOS DE MERCADO ATUAIS:
{grade_dados}

{noticias}

Aplique a análise de correlação entre os ativos, valide os Filtros de Segurança, defina o Fator Dominante e o Placar Institucional. 
Trate o WIN como consequência.
"""

# ==============================================================================
# FUNÇÃO DE COLETA
# ==============================================================================
def engine_coleta_dados():
    ativos = {
        "WIN": "^BVSP", "WDO": "BRL=X", "PETR4": "PETR4.SA", 
        "B3SA3": "B3SA3.SA", "IFNC": "^IFNC", "IMAT": "^IMAT",
        "EWZ": "EWZ", "S&P 500": "^GSPC", "NASDAQ": "^IXIC", "VIX": "^VIX"
    }
    
    grade_texto = ""
    noticias_resumo = "\n📰 MANCHETES MACRO:\n"
    
    for nome, ticker in ativos.items():
        try:
            obj = yf.Ticker(ticker)
            df = obj.history(period="2d")
            if len(df) >= 2:
                var = ((df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
                grade_texto += f"- {nome}: {var:+.2f}%\n"
            
            # Pega notícias apenas do Ibov/Global
            if ticker in ["^BVSP", "^GSPC"]:
                for n in obj.news[:2]:
                    noticias_resumo += f"• {n['title']}\n"
        except:
            grade_texto += f"- {nome}: Indisponível\n"
            
    return grade_texto, noticias_resumo

# ==============================================================================
# INTERFACE PRINCIPAL
# ==============================================================================
st.sidebar.header("🕹️ Controle de Mesa")
st.sidebar.caption(f"Última leitura: {datetime.now().strftime('%H:%M:%S')}")

if st.sidebar.button("🚀 ATUALIZAR MESA DE OPERAÇÕES"):
    with st.spinner("Analisando mercado..."):
        dados, noticias = engine_coleta_dados()
        
        # Gera o Relatório
        prompt_final = PROMPT_MESTRE.format(grade_dados=dados, noticias=noticias)
        
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt_final
            )
            st.success("Relatório de Cenário Atualizado!")
            st.markdown(response.text)
        except Exception as e:
            st.error(f"Erro na IA: {e}")
else:
    st.info("Toque no botão '🚀 ATUALIZAR' na barra lateral para gerar o diagnóstico mestre de 22 blocos.")
    

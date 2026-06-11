import streamlit as st
import yfinance as yf
from google import genai

st.set_page_config(page_title="Monitor Mestre", layout="wide")
st.title("🔮 Monitor Quantitativo Autônomo")

if "GEMINI_API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("❌ Configure a API_KEY nos Secrets.")
    st.stop()

# Função de Coleta com tratamento robusto
def get_data():
    # Mantendo a lista completa conforme seu primeiro setup
    ativos = {"WIN": "^BVSP", "WDO": "BRL=X", "PETR4": "PETR4.SA", "B3SA3": "B3SA3.SA", 
              "IFNC": "^IFNC", "IMAT": "^IFNC", "EWZ": "EWZ", "SP500": "^GSPC", "NQ": "^IXIC", "VIX": "^VIX"}
    resumo = ""
    for k, v in ativos.items():
        try:
            d = yf.Ticker(v).history(period="2d")
            var = ((d['Close'].iloc[-1] - d['Close'].iloc[-2]) / d['Close'].iloc[-2]) * 100
            resumo += f"- {k}: {var:+.2f}%\n"
        except:
            resumo += f"- {k}: N/A\n"
    return resumo

# Prompt que força a exibição da Carteira + 22 blocos
PROMPT_TOTAL = """
Aja como um analista institucional. 
1. PRIMEIRO, exiba a CARTEIRA DE ATIVOS com suas variações percentuais conforme os dados fornecidos.
2. SEGUNDO, gere um RELATÓRIO TÉCNICO com EXATAMENTE 22 BLOCOS numerados e intitulados.
3. Não resuma nem embole os blocos. Use formatação clara.

DADOS DA CARTEIRA:
{dados}

INÍCIO DO RELATÓRIO:
"""

st.sidebar.header("🕹️ Comando de Mesa")
if st.sidebar.button("🚀 ATUALIZAR MESA"):
    dados = get_data()
    # Mostra a carteira na tela antes do relatório da IA
    st.subheader("📊 Carteira de Ativos (Real-Time)")
    st.text(dados) 
    
    with st.spinner("Gerando diagnóstico mestre..."):
        try:
            resp = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=PROMPT_TOTAL.format(dados=dados)
            )
            st.markdown(resp.text)
        except Exception as e:
            st.error(f"Erro: {e}")
            

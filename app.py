import streamlit as st
import yfinance as yf
from google import genai

st.set_page_config(page_title="Mesa Quant", layout="wide")
st.title("🔮 Monitor Quantitativo Autônomo")

if "GEMINI_API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("❌ Erro de Configuração.")
    st.stop()

# PROMPT ESPECIALIZADO: Força a IA a criar blocos explícitos
PROMPT_TOTAL = """
Analise os dados abaixo e retorne um relatório técnico com exatos 22 blocos numerados.
CADA BLOCO DEVE COMEÇAR COM O TÍTULO E NÚMERO (Ex: "1. AGENDA ECONÔMICA...").
Use quebras de linha duplas entre os blocos para evitar aglomeração de texto.
Se um ativo não estiver disponível na grade, mencione que o dado está "Indisponível" e derive a análise dos ativos correlacionados presentes.

GRADE: {dados}
"""

def get_data():
    ativos = {"WIN": "^BVSP", "WDO": "BRL=X", "PETR4": "PETR4.SA", "B3SA3": "B3SA3.SA", 
              "IFNC": "^IFNC", "IMAT": "^IFNC", "EWZ": "EWZ", "SP500": "^GSPC", "NQ": "^IXIC", "VIX": "^VIX"}
    g = ""
    for k, v in ativos.items():
        try:
            d = yf.Ticker(v).history(period="2d")
            var = ((d['Close'].iloc[-1] - d['Close'].iloc[-2]) / d['Close'].iloc[-2]) * 100
            g += f"{k}: {var:+.2f}% | "
        except:
            g += f"{k}: Sem Dado | "
    return g

st.sidebar.header("🕹️ Comando")
if st.sidebar.button("🚀 ATUALIZAR RELATÓRIO"):
    dados = get_data()
    with st.spinner("Gerando diagnóstico..."):
        try:
            resp = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=PROMPT_TOTAL.format(dados=dados)
            )
            # O st.markdown renderiza o texto como listas e negritos corretamente
            st.markdown(resp.text)
        except Exception as e:
            st.error(f"Falha na API: {e}")
            

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Configuração de layout para responsividade
st.set_page_config(page_title="MACA-QUANTI", layout="wide")

# CSS Global injetado uma única vez
st.markdown("""
    <style>
        [data-testid="stMetricValue"] { font-size: 20px !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🍎 MACA-QUANTI")

macro_ativos = {
    "^BVSP": "IBOVESPA", "BRL=X": "DÓLAR", "FIXA11.SA": "JUROS",
    "MATB11.SA": "IMAT", "FIND11.SA": "IFNC", "B3SA3.SA": "B3SA3",
    "EWZ": "EWZ", "^VIX": "VIX", "ES=F": "S&P 500", "NQ=F": "NASDAQ"
}

# Lógica de cálculo
ativos_processados = []
with st.spinner("Calculando..."):
    for cod, nome in macro_ativos.items():
        try:
            df = yf.download(cod, period="60d", interval="1d", progress=False)
            if not df.empty:
                fechamento = df['Close'].iloc[:, 0] if isinstance(df['Close'], pd.DataFrame) else df['Close']
                z = (fechamento.iloc[-1] - fechamento.rolling(20).mean().iloc[-1]) / fechamento.rolling(20).std().iloc[-1]
                ativos_processados.append({"nome": nome, "z": z})
        except: continue

# Grid Responsivo usando st.columns (Nativo)
cols = st.columns(2) # 2 colunas para garantir visualização no celular
for i, item in enumerate(ativos_processados):
    with cols[i % 2]:
        # Usamos o st.metric para garantir que o layout nunca quebre
        # A cor será gerenciada nativamente pelo Streamlit
        st.metric(label=item['nome'], value=f"Z: {item['z']:.2f}")

# Gráfico
st.subheader("📊 Rastro (15 dias)")
# ... (seu código de gráfico continua igual)
import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="MACA-QUANTI", layout="wide")

# CSS para tornar os blocos padrão do Streamlit mais compactos e bonitos
st.markdown("""
    <style>
        [data-testid="stVerticalBlock"] { gap: 0.5rem; }
        .stButton button { width: 100%; }
        .metric-card {
            background-color: #262730;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            border-left: 5px solid #444;
            margin-bottom: 10px;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🍎 MACA-QUANTI")

macro_ativos = {
    "^BVSP": "IBOVESPA", "BRL=X": "DÓLAR", "FIXA11.SA": "JUROS",
    "MATB11.SA": "IMAT", "FIND11.SA": "IFNC", "B3SA3.SA": "B3SA3",
    "EWZ": "EWZ", "^VIX": "VIX", "ES=F": "S&P 500", "NQ=F": "NASDAQ"
}

# Criamos uma lista de ativos processados
lista_ativos = []
with st.spinner("Calculando..."):
    for cod, nome in macro_ativos.items():
        try:
            df = yf.download(cod, period="60d", interval="1d", progress=False)
            if not df.empty:
                fechamento = df['Close'].iloc[:, 0] if isinstance(df['Close'], pd.DataFrame) else df['Close']
                z = (fechamento.iloc[-1] - fechamento.rolling(20).mean().iloc[-1]) / fechamento.rolling(20).std().iloc[-1]
                lista_ativos.append({"nome": nome, "z": z})
        except: continue

# Criamos as colunas e inserimos os blocos nativos do Streamlit
# Isso resolve o problema do texto HTML aparecendo na tela
cols = st.columns(2)
for i, item in enumerate(lista_ativos):
    cor = "🔴" if item['z'] > 1.5 else ("🟢" if item['z'] < -1.5 else "⚪")
    with cols[i % 2]:
        st.markdown(f"""
            <div class="metric-card" style="border-left-color: {'#FF4B4B' if item['z'] > 1.5 else ('#00CC96' if item['z'] < -1.5 else '#888')};">
                <div style="font-weight:bold;">{item['nome']}</div>
                <div style="font-size:18px;">{cor} Z: {item['z']:.2f}</div>
            </div>
        """, unsafe_allow_html=True)
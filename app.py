import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="MACA-QUANTI", layout="wide")

st.markdown("""
    <style>
        .grid-container {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
            gap: 10px;
            padding: 10px;
        }
        .card {
            background-color: #262730;
            border-radius: 8px;
            padding: 10px;
            text-align: center;
            border-left: 5px solid #444;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🍎 MACA-QUANTI")

macro_ativos = {
    "^BVSP": "IBOVESPA", "BRL=X": "DÓLAR", "FIXA11.SA": "JUROS",
    "MATB11.SA": "IMAT", "FIND11.SA": "IFNC", "B3SA3.SA": "B3SA3",
    "EWZ": "EWZ", "^VIX": "VIX", "ES=F": "S&P 500", "NQ=F": "NASDAQ"
}

html_cards = '<div class="grid-container">'

with st.spinner("Calculando..."):
    for cod, nome in macro_ativos.items():
        try:
            df = yf.download(cod, period="60d", interval="1d", progress=False)
            if not df.empty:
                fechamento = df['Close'].iloc[:, 0] if isinstance(df['Close'], pd.DataFrame) else df['Close']
                z = (fechamento.iloc[-1] - fechamento.rolling(20).mean().iloc[-1]) / fechamento.rolling(20).std().iloc[-1]
                cor = "#FF4B4B" if z > 1.5 else ("#00CC96" if z < -1.5 else "#888888")
                html_cards += f'''
                    <div class="card" style="border-left-color: {cor};">
                        <div style="font-weight:bold; font-size:13px;">{nome}</div>
                        <div style="font-size:12px; color:#aaa;">Z: {z:.2f}</div>
                    </div>
                '''
        except: continue

html_cards += '</div>'
st.markdown(html_cards, unsafe_allow_html=True)
st.caption("🟢 Z < -1.5 (Compra) | 🔴 Z > 1.5 (Venda)")
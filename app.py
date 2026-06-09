import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Configuração da página
st.set_page_config(page_title="MACA-QUANTI - Mobile Pro", layout="wide")

# CSS para garantir que nada seja cortado
st.markdown("""
    <style>
        .block-container { padding: 1rem !important; }
        .card { background-color: #262730; border-radius: 10px; padding: 15px; margin: 5px; text-align: center; border-left: 5px solid #444; }
        .card-title { font-weight: bold; font-size: 16px; margin-bottom: 5px; }
        .card-val { font-size: 14px; color: #ddd; }
    </style>
""", unsafe_allow_html=True)

st.title("🍎 MACA-QUANTI")

macro_ativos = {
    "^BVSP": "IBOVESPA", "BRL=X": "DÓLAR", "FIXA11.SA": "JUROS",
    "MATB11.SA": "IMAT", "FIND11.SA": "IFNC", "B3SA3.SA": "B3SA3",
    "EWZ": "EWZ", "^VIX": "VIX", "ES=F": "S&P 500", "NQ=F": "NASDAQ"
}

dados = []

with st.spinner("Calculando..."):
    for cod, nome in macro_ativos.items():
        try:
            df = yf.download(cod, period="60d", interval="1d", progress=False)
            if not df.empty:
                fechamento = df['Close'].iloc[:, 0] if isinstance(df['Close'], pd.DataFrame) else df['Close']
                z = (fechamento.iloc[-1] - fechamento.rolling(20).mean().iloc[-1]) / fechamento.rolling(20).std().iloc[-1]
                
                # Cor do card baseada no Z-Score
                cor = "#FF4B4B" if z > 1.5 else ("#00CC96" if z < -1.5 else "#888888")
                dados.append({"nome": nome, "z": z, "cor": cor, "preco": fechamento.iloc[-1]})
        except: continue

# Exibição em grade (Grid) responsiva
cols = st.columns(2) # 2 colunas para ficar perfeito no mobile
for i, item in enumerate(dados):
    with cols[i % 2]:
        st.markdown(f"""
            <div class="card" style="border-left-color: {item['cor']};">
                <div class="card-title">{item['nome']}</div>
                <div class="card-val">Z: {item['z']:.2f}</div>
            </div>
        """, unsafe_allow_html=True)

st.info("🟢 Z < -1.5 (Compra) | 🔴 Z > 1.5 (Venda)")
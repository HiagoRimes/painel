import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="MACA-QUANTI", layout="centered")

st.title("🍎 MACA-QUANTI")
st.caption("Afastamento Estatístico (Média 20 períodos)")

macro_ativos = {
    "^BVSP": "IBOVESPA", "BRL=X": "DÓLAR", "FIXA11.SA": "JUROS",
    "MATB11.SA": "IMAT", "FIND11.SA": "IFNC", "B3SA3.SA": "B3SA3"
}

# Processamento
dados = []
with st.spinner("Calculando..."):
    for cod, nome in macro_ativos.items():
        try:
            df = yf.download(cod, period="60d", interval="1d", progress=False)
            if not df.empty:
                # Pegamos o valor como float puro para evitar erros do Pandas
                fechamento = df['Close'].iloc[-1]
                media = df['Close'].rolling(20).mean().iloc[-1]
                std = df['Close'].rolling(20).std().iloc[-1]
                
                # Garantindo que z seja um número (float)
                z = float((fechamento - media) / std)
                dados.append({"nome": nome, "z": z})
        except: continue

# Grid em 2 colunas
cols = st.columns(2)

for i, item in enumerate(dados):
    with cols[i % 2]:
        # Comparação agora é segura porque z é um float
        if item['z'] < -1.5:
            with st.container(border=True):
                st.success(f"{item['nome']}\n\nZ: {item['z']:.2f}")
        elif item['z'] > 1.5:
            with st.container(border=True):
                st.error(f"{item['nome']}\n\nZ: {item['z']:.2f}")
        else:
            with st.container(border=True):
                st.write(f"{item['nome']}\n\nZ: {item['z']:.2f}")

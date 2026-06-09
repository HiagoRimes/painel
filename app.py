import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="MACA-QUANTI", layout="centered")
st.title("🍎 MACA-QUANTI")

ativos = {"^BVSP": "IBOVESPA", "BRL=X": "DÓLAR", "FIXA11.SA": "JUROS"}

dados_finais = []

# Tentativa direta de processamento
try:
    for cod, nome in ativos.items():
        df = yf.download(cod, period="30d", interval="1d", progress=False)
        if not df.empty:
            fechamento = float(df['Close'].iloc[-1])
            media = float(df['Close'].rolling(20).mean().iloc[-1])
            std = float(df['Close'].rolling(20).std().iloc[-1])
            z = (fechamento - media) / std
            sinal = "🔴 VENDA" if z > 1.5 else ("🟢 COMPRA" if z < -1.5 else "⚪ NEUTRO")
            dados_finais.append({"Ativo": nome, "Z": f"{z:.2f}", "Sinal": sinal})
    
    if dados_finais:
        st.table(pd.DataFrame(dados_finais))
    else:
        st.write("Dados não carregados ainda.")
except Exception as e:
    st.write(f"Erro ao processar: {e}")

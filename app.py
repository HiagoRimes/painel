import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.set_page_config(page_title="MACA-QUANTI", layout="centered")
st.title("🍎 MACA-QUANTI")

macro_ativos = {
    "^BVSP": "IBOVESPA", "BRL=X": "DÓLAR", "FIXA11.SA": "JUROS",
    "MATB11.SA": "IMAT", "FIND11.SA": "IFNC", "B3SA3.SA": "B3SA3"
}

dados_finais = []

with st.spinner("Baixando dados..."):
    for cod, nome in macro_ativos.items():
        try:
            df = yf.download(cod, period="60d", interval="1d", progress=False)
            if not df.empty:
                # Extração segura de dados
                c = df['Close']
                if isinstance(c, pd.DataFrame): c = c.iloc[:, 0]
                
                fechamento = float(c.iloc[-1])
                media = float(c.rolling(20).mean().iloc[-1])
                std = float(c.rolling(20).std().iloc[-1])
                z = (fechamento - media) / std
                
                sinal = "🔴 VENDA" if z > 1.5 else ("🟢 COMPRA" if z < -1.5 else "⚪ NEUTRO")
                dados_finais.append({"Ativo": nome, "Z": f"{z:.2f}", "Sinal": sinal})
            time.sleep(0.3)
        except Exception as e:
            st.error(f"Erro no ativo {nome}: {e}")

if dados_finais:
    st.table(pd.DataFrame(dados_finais))
else:
    st.write("Aguardando carregamento...")

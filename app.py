import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="MACA-QUANTI", layout="wide")

st.title("🍎 MACA-QUANTI")

macro_ativos = {
    "^BVSP": "IBOVESPA", "BRL=X": "DÓLAR", "FIXA11.SA": "JUROS",
    "MATB11.SA": "IMAT", "FIND11.SA": "IFNC", "B3SA3.SA": "B3SA3"
}

dados_finais = []

with st.spinner("Buscando dados..."):
    for cod, nome in macro_ativos.items():
        try:
            df = yf.download(cod, period="60d", interval="1d", progress=False)
            if not df.empty:
                # Pegando os dados como float
                fechamento = float(df['Close'].iloc[-1])
                media = float(df['Close'].rolling(20).mean().iloc[-1])
                std = float(df['Close'].rolling(20).std().iloc[-1])
                z = (fechamento - media) / std
                
                # Definição do sinal
                if z > 1.5: sinal = "🔴 VENDA"
                elif z < -1.5: sinal = "🟢 COMPRA"
                else: sinal = "⚪ NEUTRO"
                
                dados_finais.append({"Ativo": nome, "Z": f"{z:.2f}", "Sinal": sinal})
        except: continue

# Exibe como tabela. Isso NUNCA quebra no celular.
if dados_finais:
    df_exibicao = pd.DataFrame(dados_finais)
    st.table(df_exibicao)
else:
    st.error("Não foi possível carregar os dados. Verifique a conexão.")

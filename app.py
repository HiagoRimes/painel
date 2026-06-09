import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.set_page_config(page_title="MACA-QUANTI", layout="centered")
st.title("🍎 MACA-QUANTI")

# Dicionário completo com todos os seus ativos
macro_ativos = {
    "^BVSP": "IBOV", 
    "BRL=X": "DÓLAR", 
    "FIXA11.SA": "JUROS",
    "MATB11.SA": "IMAT", 
    "FIND11.SA": "IFNC", 
    "B3SA3.SA": "B3SA3",
    "^VIX": "VIX",
    "EWZ": "EWZ",
    "ES=F": "S&P 500",
    "NQ=F": "NASDAQ"
}

dados_finais = []

with st.spinner("Atualizando todos os ativos..."):
    for cod, nome in macro_ativos.items():
        try:
            df = yf.download(cod, period="60d", interval="1d", progress=False)
            if not df.empty:
                c = df['Close']
                if isinstance(c, pd.DataFrame): c = c.iloc[:, 0]
                
                preco_atual = float(c.iloc[-1])
                preco_anterior = float(c.iloc[-2])
                variacao = ((preco_atual / preco_anterior) - 1) * 100
                
                media = float(c.rolling(20).mean().iloc[-1])
                std = float(c.rolling(20).std().iloc[-1])
                z = (preco_atual - media) / std
                
                sinal = "🔴 VENDA" if z > 1.5 else ("🟢 COMPRA" if z < -1.5 else "⚪ NEUTRO")
                
                dados_finais.append({
                    "Ativo": nome, 
                    "Preço": f"{preco_atual:,.2f}", 
                    "Var%": f"{variacao:.1f}%", 
                    "Z": f"{z:.1f}", 
                    "Sinal": sinal
                })
            time.sleep(0.3)
        except Exception: continue

if dados_finais:
    st.table(pd.DataFrame(dados_finais))

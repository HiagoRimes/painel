import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.set_page_config(page_title="MACA-QUANTI", layout="centered")
st.title("🍎 MACA-QUANTI - Direção WIN")

# Ativos que ditam a direção do nosso mercado
macro_ativos = {
    "^BVSP": "IBOV", "BRL=X": "DÓLAR", "EWZ": "EWZ", 
    "ES=F": "S&P500", "NQ=F": "NASDAQ", "^VIX": "VIX"
}

dados_decisao = []
for cod, nome in macro_ativos.items():
    try:
        df = yf.download(cod, period="30d", interval="1d", progress=False)
        c = df['Close'].iloc[:, 0] if isinstance(df['Close'], pd.DataFrame) else df['Close']
        
        # O "Sentimento" é baseado no Z-Score
        z = (float(c.iloc[-1]) - float(c.rolling(20).mean().iloc[-1])) / float(c.rolling(20).std().iloc[-1])
        
        # Lógica de correlação (Ex: Dólar sobe, Win desce -> multiplicador -1)
        multiplicador = -1 if nome == "DÓLAR" or nome == "VIX" else 1
        forca = z * multiplicador
        
        dados_decisao.append({"Ativo": nome, "Força": forca})
        time.sleep(0.3)
    except: continue

# Cálculo da Direção (Soma das forças)
df_decisao = pd.DataFrame(dados_decisao)
direcao_win = df_decisao['Força'].mean()

# Painel de Decisão
st.subheader("🎯 Sugestão para o WIN")
if direcao_win > 0.5:
    st.success(f"VIÉS ALTISTA (Força: {direcao_win:.2f})")
elif direcao_win < -0.5:
    st.error(f"VIÉS BAIXISTA (Força: {direcao_win:.2f})")
else:
    st.info("MERCADO NEUTRO / SEM DIREÇÃO")

st.table(df_decisao)

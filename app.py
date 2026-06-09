import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.set_page_config(page_title="MACA-QUANTI", layout="centered")
st.title("🍎 MACA-QUANTI")

# Dicionário de ativos com seus multiplicadores de correlação para o WIN
# Multiplicador -1 significa: ativo sobe, WIN desce (Correlação Inversa)
macro_ativos = {
    "^BVSP": ("IBOV", 1), "BRL=X": ("DÓLAR", -1), "EWZ": ("EWZ", 1), 
    "ES=F": ("S&P500", 1), "NQ=F": ("NASDAQ", 1), "^VIX": ("VIX", -1)
}

dados = []
for cod, (nome, mult) in macro_ativos.items():
    try:
        df = yf.download(cod, period="30d", interval="1d", progress=False)
        c = df['Close'].iloc[:, 0] if isinstance(df['Close'], pd.DataFrame) else df['Close']
        
        preco = float(c.iloc[-1])
        z = (preco - float(c.rolling(20).mean().iloc[-1])) / float(c.rolling(20).std().iloc[-1])
        forca = z * mult
        
        # Define o sinal visual
        if forca > 0.5: sinal = "🟢 COMPRA"
        elif forca < -0.5: sinal = "🔴 VENDA"
        else: sinal = "⚪ NEUTRO"
        
        dados.append({"Ativo": nome, "Z": f"{z:.2f}", "Força": f"{forca:.2f}", "Sinal": sinal})
        time.sleep(0.3)
    except: continue

# Cálculo do viés geral
df_resumo = pd.DataFrame(dados)
vies_global = pd.DataFrame(dados)['Força'].astype(float).mean()

# Painel de Decisão
st.subheader("🎯 Viés para o WIN")
if vies_global > 0.3:
    st.success(f"VIÉS ALTISTA (Força: {vies_global:.2f})")
elif vies_global < -0.3:
    st.error(f"VIÉS BAIXISTA (Força: {vies_global:.2f})")
else:
    st.info("MERCADO NEUTRO")

# Tabela completa
st.table(df_resumo)

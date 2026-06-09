import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Configuração minimalista
st.set_page_config(page_title="RADAR MACA-QUANTI v8.0", layout="centered")
st.title("🎯 RADAR MACA-QUANTI v8.0")

# Drivers e pesos de impacto (Padrão Institucional)
vies_ativos = {
    "FIXA11.SA": {"corr": -1.0, "peso": 1.2},
    "BRL=X":     {"corr": -1.0, "peso": 1.2},
    "FIND11.SA": {"corr": 1.0,  "peso": 0.8},
    "EWZ":       {"corr": 1.0,  "peso": 0.8},
    "ES=F":      {"corr": 1.0,  "peso": 0.6},
    "^VIX":      {"corr": -1.0, "peso": 0.5},
    "NQ=F":      {"corr": 1.0,  "peso": 0.4},
}

@st.cache_data(ttl=60)
def calcular_forca():
    impactos = []
    for cod, cfg in vies_ativos.items():
        try:
            df = yf.download(cod, period="60d", interval="1d", progress=False)
            if df.empty: continue
            c = df['Close'].iloc[:, -1]
            z = (c.iloc[-1] - c.rolling(20).mean().iloc[-1]) / max(c.rolling(20).std().iloc[-1], 0.0001)
            score = np.tanh(z * 0.5) * 100
            impactos.append(score * cfg['corr'] * cfg['peso'])
        except: continue
    return sum(impactos)

# Execução
forca = calcular_forca()

# Display Visual de Decisão (O que realmente importa)
st.subheader("Bússola de Direção do WIN:")

if forca > 15:
    st.success(f"### 🟢 COMPRA - FORÇA: {forca:.1f}")
    st.write("O fluxo institucional está alinhado para alta. Busque apenas setups de compra.")
elif forca < -15:
    st.error(f"### 🔴 VENDA - FORÇA: {abs(forca):.1f}")
    st.write("O fluxo institucional está alinhado para baixa. Busque apenas setups de venda.")
else:
    st.warning(f"### ⚠️ NEUTRO - FORÇA: {forca:.1f}")
    st.write("Mercado em disputa. Sem dominância clara. Aguarde a força romper 15 ou -15.")

st.divider()
st.caption("MACA-QUANTI ELITE v8.0 | Foco: Operacional Direcional")

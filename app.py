import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="MACA-QUANTI ELITE v8.1", layout="centered")
st.title("🏛️ MACA-QUANTI ELITE v8.1")

vies_ativos = {
    "FIXA11.SA": {"nome": "JUROS", "corr": -1.0, "peso": 1.2},
    "BRL=X":     {"nome": "DÓLAR", "corr": -1.0, "peso": 1.2},
    "FIND11.SA": {"nome": "IFNC",  "corr": 1.0,  "peso": 0.8},
    "EWZ":       {"nome": "EWZ",   "corr": 1.0,  "peso": 0.8},
    "ES=F":      {"nome": "S&P500", "corr": 1.0, "peso": 0.6},
    "^VIX":      {"nome": "VIX",   "corr": -1.0, "peso": 0.5},
    "NQ=F":      {"nome": "NASDAQ", "corr": 1.0, "peso": 0.4},
}

@st.cache_data(ttl=60)
def get_motor_dominancia():
    res = []
    for cod, cfg in vies_ativos.items():
        try:
            df = yf.download(cod, period="60d", interval="1d", progress=False)
            c = df['Close'].iloc[:, -1]
            z = (c.iloc[-1] - c.rolling(20).mean().iloc[-1]) / max(c.rolling(20).std().iloc[-1], 0.0001)
            score = np.tanh(z * 0.5) * 100
            impacto = score * cfg['corr'] * cfg['peso']
            res.append({"Ativo": cfg['nome'], "Impacto": impacto, "Score": score})
        except: continue
    return pd.DataFrame(res)

df = get_motor_dominancia()

# 1. Driver Dominante e Concentração (HHI)
df['Abs_Impacto'] = df['Impacto'].abs()
hhi = (df['Abs_Impacto'] / df['Abs_Impacto'].sum())**2
hhi_sum = hhi.sum()
driver_lider = df.loc[df['Abs_Impacto'].idxmax()]

# 2. Regime de Mercado (Lógica Institucional)
forca_total = df['Impacto'].sum()
# Detectores de regime
is_risk_off = df.loc[df['Ativo']=='VIX', 'Score'].values[0] > 20
is_compressao = hhi_sum < 0.25

regime = "Risk-Off (Stress)" if is_risk_off else ("Compressão" if is_compressao else "Direcional Institucional")

# UI PROFISSIONAL
col1, col2 = st.columns(2)
col1.metric("Regime", regime)
col2.metric("Driver Líder", driver_lider['Ativo'])

st.divider()

# Bússola final
if forca_total > 15: st.success(f"### 🟢 SENTIDO: COMPRA (Força: {forca_total:.1f})")
elif forca_total < -15: st.error(f"### 🔴 SENTIDO: VENDA (Força: {abs(forca_total):.1f})")
else: st.warning(f"### ⚠️ SENTIDO: NEUTRO (Força: {forca_total:.1f})")

st.caption(f"Concentração (HHI): {hhi_sum:.2f} | Motor v8.1 Operacional")

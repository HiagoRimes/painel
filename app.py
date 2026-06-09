import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="MACA-QUANTI ELITE v8.2", layout="centered")
st.title("🏛️ MACA-QUANTI ELITE v8.2")

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
def get_motor_profissional():
    res = []
    for cod, cfg in vies_ativos.items():
        try:
            df = yf.download(cod, period="60d", interval="1d", progress=False)
            c = df['Close'] # Corrigido: Series
            z = (c.iloc[-1] - c.rolling(20).mean().iloc[-1]) / max(c.rolling(20).std().iloc[-1], 0.0001)
            score = np.tanh(z * 0.5) * 100
            res.append({"Ativo": cfg['nome'], "Impacto": score * cfg['corr'] * cfg['peso'], "Score": score})
        except: continue
    return pd.DataFrame(res)

df = get_motor_profissional()

# 1. Ajustes Estatísticos de Precisão
df['Abs_Impacto'] = df['Impacto'].abs()
p = df['Abs_Impacto'] / df['Abs_Impacto'].sum()
hhi_sum = np.sum(p**2)
forca_total = df['Impacto'].sum() / (df['Abs_Impacto'].sum() + 1e-9) # Normalizado [-1, 1]

# 2. Diagnóstico de Regime e Conflito
vix = df.loc[df['Ativo']=='VIX', 'Score'].values[0]
spx = df.loc[df['Ativo']=='S&P500', 'Score'].values[0]
is_risk_off = (vix > 20) and (spx < 0)
tem_conflito = (df['Impacto'].max() > 0) and (df['Impacto'].min() < 0)

# 3. Tradução Operacional (Camada Final)
if is_risk_off:
    regime = "Risk-Off (Stress Institucional)"
    leitura = "Evitar compra direcional. Preferir pullbacks de venda. Alta volatilidade esperada."
elif tem_conflito:
    regime = "Compressão Macro (Briga de Fluxo)"
    leitura = "Mercado sem tendência clara. Focar em scalps curtos ou aguardar rompimento de nível."
else:
    regime = "Direcional Institucional"
    leitura = "Tendência clara alinhada. Seguir a bússola com confiança."

# UI PROFISSIONAL
col1, col2 = st.columns(2)
col1.metric("Regime", regime)
col2.metric("Driver Líder", df.loc[df['Abs_Impacto'].idxmax(), 'Ativo'])

st.info(f"**Leitura Operacional:** {leitura}")

# Bússola Normalizada
if forca_total > 0.3: st.success(f"### 🟢 COMPRA | Força Relativa: {forca_total:.2f}")
elif forca_total < -0.3: st.error(f"### 🔴 VENDA | Força Relativa: {abs(forca_total):.2f}")
else: st.warning(f"### ⚠️ NEUTRO | Força Relativa: {forca_total:.2f}")

st.caption(f"Concentração (HHI): {hhi_sum:.2f} | Conflito Macro: {'Sim' if tem_conflito else 'Não'}")

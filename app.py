import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Configuração de Layout
st.set_page_config(page_title="MACA-QUANTI ELITE v8.4", layout="wide")
st.title("🏛️ MACA-QUANTI ELITE v8.4")

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
            df_y = yf.download(cod, period="60d", interval="1d", progress=False)
            if df_y is None or df_y.empty: continue
            c = df_y['Close']
            if isinstance(c, pd.DataFrame): c = c.iloc[:, -1]
            z = (c.iloc[-1] - c.rolling(20).mean().iloc[-1]) / max(c.rolling(20).std().iloc[-1], 0.0001)
            score = np.tanh(z * 0.5) * 100
            res.append({"Ativo": cfg['nome'], "Impacto": score * cfg['corr'] * cfg['peso'], "Score": score})
        except Exception: continue
    return pd.DataFrame(res) if res else pd.DataFrame(columns=["Ativo", "Impacto", "Score"])

df = get_motor_profissional()
if df.empty: st.stop()

# Cálculos
df['Abs_Impacto'] = df['Impacto'].abs()
forca_total = df['Impacto'].sum() / (df['Abs_Impacto'].sum() + 1e-9)
vix = df.loc[df['Ativo']=='VIX', 'Score'].values[0] if 'VIX' in df['Ativo'].values else 0
spx = df.loc[df['Ativo']=='S&P500', 'Score'].values[0] if 'S&P500' in df['Ativo'].values else 0

# Diagnósticos de Regime
is_risk_off = (vix > 20) and (spx < 0)
tem_conflito = (df['Impacto'].max() > 0) and (df['Impacto'].min() < 0)

# Estrutura em 3 Colunas
col_diag, col_bussola, col_grafico = st.columns([1, 1, 2])

with col_diag:
    st.subheader("Diagnóstico")
    regime = "Risk-Off (Stress)" if is_risk_off else ("Compressão" if tem_conflito else "Direcional")
    st.metric("Regime", regime)
    st.metric("Driver Líder", df.loc[df['Abs_Impacto'].idxmax(), 'Ativo'])
    st.caption("Conflito Macro: " + ("Sim" if tem_conflito else "Não"))

with col_bussola:
    st.subheader("Decisão")
    if forca_total > 0.3: st.success(f"### 🟢 COMPRA\nForça: {forca_total:.2f}")

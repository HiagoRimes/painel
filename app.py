import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Configuração de Layout
st.set_page_config(page_title="MACA-QUANTI ELITE v9.2", layout="wide")
st.title("🏛️ MACA-QUANTI ELITE v9.2 | Motor Institucional")

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
            res.append({"Ativo": cfg['nome'], "Impacto": score * cfg['corr'] * cfg['peso']})
        except Exception: continue
    return pd.DataFrame(res)

df = get_motor_profissional()
if df.empty: st.stop()

# 1. Cálculos de Dominância
df["Abs_Impacto"] = df["Impacto"].abs()
hhi_sum = np.sum((df["Abs_Impacto"] / (df["Abs_Impacto"].sum() + 1e-9))**2)
qualidade_regime = 1 - hhi_sum

# 2. Força Total Estável (Escala Tanh)
forca_total = np.tanh(df['Impacto'].sum() / (df["Abs_Impacto"].sum() + 1e-9))

# 3. Driver Dominante
driver_lider = df.sort_values("Impacto", ascending=False).head(1)["Ativo"].values[0]

# 4. Detecção de Conflito Macro (Corrigida)
vix_score = df.loc[df["Ativo"] == "VIX", "Impacto"].values[0] if "VIX" in df["Ativo"].values else 0
spx_score = df.loc[df["Ativo"]

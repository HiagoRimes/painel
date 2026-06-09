import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(page_title="MACA-QUANTI", layout="wide")
st.title("🏛️ MACA-QUANTI | Radar de Dominância")

# =========================
# UNIVERSO ESTÁVEL
# =========================
ativos = {
    "JUROS LONGOS": {"ticker": "TLT", "corr": -1},
    "DÓLAR": {"ticker": "UUP", "corr": -1},
    "VOLATILIDADE": {"ticker": "VXX", "corr": -1},
    "S&P 500": {"ticker": "SPY", "corr": 1},
    "NASDAQ": {"ticker": "QQQ", "corr": 1},
    "FINANCEIRO": {"ticker": "XLF", "corr": 1},
    "MATERIAIS": {"ticker": "XLB", "corr": 1},
    "PETROBRAS": {"ticker": "PETR4.SA", "corr": 1},
    "VALE": {"ticker": "VALE3.SA", "corr": 1},
    "BRASIL (IBOV)": {"ticker": "EWZ", "corr": 1},
}

# =========================
# DADOS
# =========================
@st.cache_data(ttl=60)
def baixar(ticker):
    try:
        df = yf.download(ticker, period="5d", interval="5m", progress=False)
        if df is None or df.empty:
            return None
        return df["Close"].dropna()
    except:
        return None


# =========================
# SCORE
# =========================
def score(series):
    if series is None or len(series) < 30:
        return 0

    series = series.dropna()

    atual = series.iloc[-1]
    media = series.rolling(30).mean().iloc[-1]
    std = series.rolling(30).std().iloc[-1]

    if pd.isna(std) or std == 0:
        return 0

    z = (atual - media) / std
    return np.tanh(z)


# =========================
# PROCESSAMENTO
# =========================
resultados = []

for nome, cfg in ativos.items():

    serie = baixar(cfg["ticker"])
    if serie is None:
        continue

    s = score(serie)

    try:
        direcao = np.sign(serie.iloc[-1] - serie.iloc[-2])
    except:
        direcao = 0

    impacto = s * cfg["corr"] * direcao * 100

    resultados.append({
        "Ativo": nome,
        "Impacto": impacto
    })

df = pd.DataFrame(resultados)

if df.empty:
    st.error("Sem dados — Yahoo indisponível no momento")
    st.stop()

# =========================
# PRESSÃO
# =========================
compra = df[df["Impacto"] > 0]["Impacto"].sum()
venda = abs(df[df["Impacto"] < 0]["Impacto"].sum())

total = compra + venda + 1e-9

pct_compra = compra / total
pct_venda = venda / total

if pct_compra > 0.55:
    tendencia = "🟢 COMPRA"
elif pct_venda > 0.55:
    tendencia = "🔴 VENDA"
else:
    tendencia = "🟡 NEUTRO"

# =========================
# LÍDER
# =========================
df = df.sort_values("Impacto", ascending=False)
lider = df.iloc[0]["Ativo"]

# =========================
# UI
# =========================
col1, col2, col3 = st.columns(3)

col1.metric("Tendência", tendencia)
col2.metric("Líder", lider)
col3.metric("Hora", datetime.now().strftime("%H:%M:%S"))

st.divider()

st.write(f"Compra: {pct_compra:.2%}")
st.write(f"Venda: {pct_venda:.2%}")

st.divider()

st.dataframe(df, use_container_width=True)

st.caption("MACA-QUANTI v1")

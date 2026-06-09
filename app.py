import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(page_title="MACA-QUANTI HÍBRIDO", layout="wide")
st.title("⚡ MACA-QUANTI | Radar Híbrido de Correlação")

# =========================
# UNIVERSO
# =========================
ativos = {
    "SP500": {"ticker": "SPY", "corr": 1, "mode": "fast"},
    "NASDAQ": {"ticker": "QQQ", "corr": 1, "mode": "fast"},
    "BRASIL": {"ticker": "EWZ", "corr": 1, "mode": "mid"},
    "FINANCEIRO": {"ticker": "XLF", "corr": 1, "mode": "mid"},
    "TECNOLOGIA": {"ticker": "XLK", "corr": 1, "mode": "mid"},
    "MATERIAIS": {"ticker": "XLB", "corr": 1, "mode": "mid"},
    "JUROS": {"ticker": "TLT", "corr": -1, "mode": "mid"},
}

# =========================
# LOAD HÍBRIDO (FALLBACK REAL)
# =========================
@st.cache_data(ttl=60)
def load(ticker, mode):

    try:
        if mode == "fast":
            df = yf.download(ticker, period="2d", interval="5m", progress=False)
        else:
            df = yf.download(ticker, period="10d", interval="15m", progress=False)

        # fallback automático se vazio
        if df is None or df.empty:
            df = yf.download(ticker, period="30d", interval="60m", progress=False)

        if df is None or df.empty:
            return None

        close = pd.to_numeric(df["Close"], errors="coerce").dropna()

        if len(close) < 10:
            return None

        return close

    except:
        return None

# =========================
# SPIKE (leve + estável)
# =========================
def spike(series):

    try:
        r_now = (series.iloc[-1] / series.iloc[-2]) - 1
        r_prev = (series.iloc[-6] / series.iloc[-12]) - 1

        accel = r_now - r_prev

        vol = series.pct_change().rolling(10).std().iloc[-1]
        vol = float(vol) if pd.notna(vol) and vol > 1e-6 else 0.001

        return float(accel / vol)

    except:
        return 0.0

# =========================
# PROCESSAMENTO
# =========================
rows = []

for name, cfg in ativos.items():

    s = load(cfg["ticker"], cfg["mode"])
    if s is None:
        continue

    sp = spike(s)

    try:
        direction = np.sign(float(s.iloc[-1]) - float(s.iloc[-2]))
    except:
        direction = 0

    impact = sp * cfg["corr"] * direction * 100

    rows.append({
        "Ativo": name,
        "Impacto": float(impact),
        "Modo": cfg["mode"]
    })

df = pd.DataFrame(rows)

if df.empty:
    st.error("Sem dados Yahoo mesmo com fallback")
    st.stop()

df["Impacto"] = pd.to_numeric(df["Impacto"], errors="coerce").fillna(0.0)

# =========================
# LÍDER
# =========================
df = df.sort_values("Impacto", ascending=False)

leader = df.iloc[0]["Ativo"]
leader_value = df.iloc[0]["Impacto"]

# =========================
# PRESSÃO GLOBAL
# =========================
buy = df[df["Impacto"] > 0]["Impacto"].sum()
sell = abs(df[df["Impacto"] < 0]["Impacto"].sum())

total = buy + sell + 1e-9

pct_buy = buy / total
pct_sell = sell / total

if pct_buy > 0.6:
    regime = "🟢 RISK ON (COMPRA)"
elif pct_sell > 0.6:
    regime = "🔴 RISK OFF (VENDA)"
else:
    regime = "🟡 NEUTRO / COMPRESSÃO"

# =========================
# ALERTA DE SPIKE
# =========================
if abs(leader_value) > 2:
    alert = "🚨 SPIKE FORTE DETECTADO"
else:
    alert = "OK"

# =========================
# UI
# =========================
c1, c2, c3 = st.columns(3)

c1.metric("Regime", regime)
c2.metric("Líder", leader)
c3.metric("Alerta", alert)

st.divider()

st.write(f"🟢 Compra: {pct_buy:.2%}")
st.write(f"🔴 Venda: {pct_sell:.2%}")

st.divider()

st.dataframe(df, use_container_width=True)

st.caption("MACA-QUANTI | versão híbrida estável (5m + 15m + fallback 60m)")

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(page_title="MACA-QUANTI RADAR", layout="wide")
st.title("⚡ MACA-QUANTI | Radar de Spike de Correlação")

# =========================
# UNIVERSO (ativos líquidos)
# =========================
ativos = {
    "SP500": {"ticker": "SPY", "corr": 1},
    "NASDAQ": {"ticker": "QQQ", "corr": 1},
    "BRASIL": {"ticker": "EWZ", "corr": 1},
    "FINANCEIRO": {"ticker": "XLF", "corr": 1},
    "TECNOLOGIA": {"ticker": "XLK", "corr": 1},
    "MATERIAIS": {"ticker": "XLB", "corr": 1},
    "JUROS": {"ticker": "TLT", "corr": -1},
}

# =========================
# DADOS (intraday curto)
# =========================
@st.cache_data(ttl=30)
def load(ticker):
    try:
        df = yf.download(
            ticker,
            period="2d",
            interval="5m",
            progress=False
        )

        if df is None or df.empty or "Close" not in df:
            return None

        close = pd.to_numeric(df["Close"], errors="coerce").dropna()

        if len(close) < 30:
            return None

        return close

    except:
        return None

# =========================
# SPIKE DE FORÇA (ACELERAÇÃO)
# =========================
def spike_force(series):

    try:
        # retorno curto (momentum imediato)
        r_now = (series.iloc[-1] / series.iloc[-2]) - 1

        # retorno recente (baseline curto)
        r_prev = (series.iloc[-6] / series.iloc[-12]) - 1

        # aceleração = mudança de ritmo
        accel = r_now - r_prev

        # volatilidade curta
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

    s = load(cfg["ticker"])
    if s is None:
        continue

    spike = spike_force(s)

    try:
        direction = np.sign(float(s.iloc[-1]) - float(s.iloc[-2]))
    except:
        direction = 0

    impact = spike * cfg["corr"] * direction * 100

    rows.append({
        "Ativo": name,
        "Spike": float(impact)
    })

df = pd.DataFrame(rows)

if df.empty:
    st.error("Sem dados intraday do Yahoo")
    st.stop()

# =========================
# NORMALIZAÇÃO
# =========================
df["Spike"] = pd.to_numeric(df["Spike"], errors="coerce").fillna(0.0)

# =========================
# RANKING DE LIDERANÇA
# =========================
df = df.sort_values("Spike", ascending=False)

leader = df.iloc[0]["Ativo"]
leader_value = df.iloc[0]["Spike"]

# =========================
# REGIME INSTANTÂNEO
# =========================
buy = df[df["Spike"] > 0]["Spike"].sum()
sell = abs(df[df["Spike"] < 0]["Spike"].sum())

total = buy + sell + 1e-9

pct_buy = buy / total
pct_sell = sell / total

if pct_buy > 0.6:
    regime = "🟢 SPIKE DE COMPRA"
elif pct_sell > 0.6:
    regime = "🔴 SPIKE DE VENDA"
else:
    regime = "🟡 COMPRESSÃO"

# =========================
# ALERTA DE DOMINÂNCIA
# =========================
if abs(leader_value) > 2:
    alert = "🚨 MOVIMENTO ANORMAL NO LÍDER"
else:
    alert = "OK"

# =========================
# UI
# =========================
c1, c2, c3 = st.columns(3)

c1.metric("Regime", regime)
c2.metric("Líder Spike", leader)
c3.metric("Alerta", alert)

st.divider()

st.write(f"🟢 Pressão de Compra: {pct_buy:.2%}")
st.write(f"🔴 Pressão de Venda: {pct_sell:.2%}")

st.divider()

st.dataframe(df, use_container_width=True)

st.caption("Radar de Spike | aceleração intraday em tempo real")

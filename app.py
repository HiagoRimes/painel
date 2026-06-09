import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(page_title="MACA-QUANTI", layout="wide")
st.title("🏛️ MACA-QUANTI | Força de Correlação")

# =========================
# UNIVERSO
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
# DADOS
# =========================
@st.cache_data(ttl=60)
def load(ticker):
    try:
        df = yf.download(
            ticker,
            period="10d",
            interval="15m",
            progress=False
        )

        if df is None or df.empty:
            return None

        close = pd.to_numeric(df["Close"], errors="coerce").dropna()

        if len(close) < 20:
            return None

        return close

    except:
        return None

# =========================
# FORÇA
# =========================
def force(series):
    if series is None or len(series) < 10:
        return 0.0

    series = series.dropna()

    try:
        last = float(series.iloc[-1]) if pd.notna(series.iloc[-1]) else None
        prev = float(series.iloc[-2]) if pd.notna(series.iloc[-2]) else None

        if last is None or prev is None:
            return 0.0

        r1 = (last / prev) - 1
        r5 = (float(series.iloc[-1]) / float(series.iloc[-5])) - 1
        r10 = (float(series.iloc[-1]) / float(series.iloc[-10])) - 1

        retorno = (0.5 * r1 + 0.3 * r5 + 0.2 * r10)

        vol_series = series.pct_change().rolling(20).std()
        vol = vol_series.iloc[-1] if len(vol_series.dropna()) > 0 else np.nan

        vol = float(vol) if pd.notna(vol) else 0.001

        if vol <= 1e-6:
            vol = 0.001

        return float(retorno / vol)

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

    f = force(s)

    # 🔥 proteção total contra dados inválidos
    try:
        last_price = float(s.iloc[-1])
        prev_price = float(s.iloc[-2])
    except:
        continue

    direction = np.sign(last_price - prev_price)

    impact = float(f) * cfg["corr"] * float(direction) * 100

    rows.append({
        "Ativo": name,
        "Impacto": float(impact)
    })

df = pd.DataFrame(rows)

if df.empty:
    st.error("Sem dados Yahoo Finance válidos")
    st.stop()

df["Impacto"] = pd.to_numeric(df["Impacto"], errors="coerce").fillna(0.0)

# =========================
# PRESSÃO
# =========================
buy = df.loc[df["Impacto"] > 0, "Impacto"].sum()
sell = abs(df.loc[df["Impacto"] < 0, "Impacto"].sum())

total = buy + sell + 1e-9

pct_buy = buy / total
pct_sell = sell / total

trend = "🟢 COMPRA" if pct_buy > 0.55 else "🔴 VENDA" if pct_sell > 0.55 else "🟡 NEUTRO"

leader = df.sort_values("Impacto", ascending=False).iloc[0]["Ativo"]

# =========================
# UI
# =========================
c1, c2, c3 = st.columns(3)

c1.metric("Tendência", trend)
c2.metric("Líder", leader)
c3.metric("Hora", datetime.now().strftime("%H:%M:%S"))

st.divider()

st.write(f"🟢 Compra: {pct_buy:.2%}")
st.write(f"🔴 Venda: {pct_sell:.2%}")

st.divider()

st.dataframe(df, use_container_width=True)

st.caption("MACA-QUANTI | versão blindada contra Yahoo")

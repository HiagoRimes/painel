import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(page_title="MACA-QUANTI", layout="wide")
st.title("🏛️ MACA-QUANTI | Correlação Estável")

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
# DATA LOAD COM FALLBACK
# =========================
@st.cache_data(ttl=60)
def load(ticker):

    # 1 tentativa: intraday
    df = yf.download(ticker, period="10d", interval="15m", progress=False)

    if df is None or df.empty or "Close" not in df:
        # fallback 1: 1h
        df = yf.download(ticker, period="30d", interval="60m", progress=False)

    if df is None or df.empty or "Close" not in df:
        # fallback 2: diário
        df = yf.download(ticker, period="60d", interval="1d", progress=False)

    if df is None or df.empty:
        return None

    close = pd.to_numeric(df["Close"], errors="coerce").dropna()

    if len(close) < 10:
        return None

    return close

# =========================
# FORÇA
# =========================
def force(series):
    if series is None or len(series) < 10:
        return 0.0

    r1 = (series.iloc[-1] / series.iloc[-2]) - 1
    r5 = (series.iloc[-1] / series.iloc[-5]) - 1

    retorno = (0.7 * r1 + 0.3 * r5)

    vol = series.pct_change().rolling(20).std().iloc[-1]
    vol = float(vol) if pd.notna(vol) and vol > 1e-6 else 0.001

    return float(retorno / vol)

# =========================
# PROCESSAMENTO
# =========================
rows = []

for name, cfg in ativos.items():

    s = load(cfg["ticker"])
    if s is None:
        continue

    f = force(s)

    try:
        direction = np.sign(float(s.iloc[-1]) - float(s.iloc[-2]))
    except:
        direction = 0

    impact = float(f) * cfg["corr"] * float(direction) * 100

    rows.append({
        "Ativo": name,
        "Impacto": float(impact)
    })

df = pd.DataFrame(rows)

if df.empty:
    st.error("Sem dados válidos mesmo após fallback")
    st.stop()

df["Impacto"] = pd.to_numeric(df["Impacto"], errors="coerce").fillna(0.0)

buy = df.loc[df["Impacto"] > 0, "Impacto"].sum()
sell = abs(df.loc[df["Impacto"] < 0, "Impacto"].sum())

total = buy + sell + 1e-9

pct_buy = buy / total
pct_sell = sell / total

trend = "🟢 COMPRA" if pct_buy > 0.55 else "🔴 VENDA" if pct_sell > 0.55 else "🟡 NEUTRO"

leader = df.sort_values("Impacto", ascending=False).iloc[0]["Ativo"]

c1, c2, c3 = st.columns(3)
c1.metric("Tendência", trend)
c2.metric("Líder", leader)
c3.metric("Hora", datetime.now().strftime("%H:%M:%S"))

st.divider()

st.write(f"🟢 Compra: {pct_buy:.2%}")
st.write(f"🔴 Venda: {pct_sell:.2%}")

st.divider()

st.dataframe(df, use_container_width=True)

st.caption("MACA-QUANTI | fallback automático de dados")

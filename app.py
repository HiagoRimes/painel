import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(page_title="MACA-QUANTI TESTE", layout="wide")
st.title("🏛️ MACA-QUANTI | Modo Diagnóstico")

# =========================
# UNIVERSO
# =========================
ativos = {
    "JUROS": {"ticker": "TLT", "corr": -1},
    "DÓLAR": {"ticker": "UUP", "corr": -1},
    "IFNC": {"ticker": "XLF", "corr": 1},
    "BRASIL": {"ticker": "EWZ", "corr": 1},
    "SP500": {"ticker": "SPY", "corr": 1},
    "VIX": {"ticker": "^VIX", "corr": -1},
    "NASDAQ": {"ticker": "QQQ", "corr": 1},
}

# =========================
# DADOS (MAIOR HISTÓRICO PARA TESTE)
# =========================
@st.cache_data(ttl=120)
def load(ticker):
    try:
        df = yf.download(
            ticker,
            period="30d",      # 🔥 AUMENTADO (teste)
            interval="15m",    # 🔥 meio-termo estável
            progress=False
        )

        if df is None or df.empty:
            return None

        return df["Close"].dropna()

    except:
        return None

# =========================
# FORÇA (SEU MODELO, SEM ALTERAR IDEIA)
# =========================
def force(series):
    if series is None or len(series) < 20:
        return 0.0

    series = series.dropna()

    try:
        r1 = (series.iloc[-1] / series.iloc[-2]) - 1
        r10 = (series.iloc[-1] / series.iloc[-10]) - 1

        retorno = (0.6 * r1 + 0.4 * r10)

        vol = series.pct_change().rolling(30).std().iloc[-1]

        if pd.isna(vol) or vol < 1e-6:
            vol = 0.001

        return float(np.tanh((retorno / vol) * 3))

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
    st.error("Sem dados do Yahoo")
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

st.caption("MODO DIAGNÓSTICO | validação de sinal")

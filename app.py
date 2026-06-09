import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(page_title="MACA-QUANTI", layout="wide")
st.title("🏛️ MACA-QUANTI | Força de Correlação")

# =========================
# UNIVERSO (SEU SISTEMA)
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
# DADOS
# =========================
@st.cache_data(ttl=60)
def load(ticker):
    try:
        df = yf.download(ticker, period="10d", interval="30m", progress=False)
        if df is None or df.empty:
            return None
        return df["Close"].dropna()
    except:
        return None

# =========================
# FORÇA DE MOVIMENTO (AJUSTADA PARA NÃO ZERAR)
# =========================
def force(series):
    if series is None or len(series) < 10:
        return 0

    try:
        series = series.dropna()

        # retorno curto + médio (evita ruído extremo)
        r1 = (series.iloc[-1] / series.iloc[-2]) - 1
        r5 = (series.iloc[-1] / series.iloc[-5]) - 1

        # suavização (isso evita tudo virar zero)
        raw = (0.7 * r1 + 0.3 * r5) * 100

        # normalização leve por volatilidade recente
        vol = series.pct_change().rolling(10).std().iloc[-1]

        if pd.isna(vol) or vol == 0:
            return raw

        return raw / (vol * 100 + 1e-9)

    except:
        return 0

# =========================
# PROCESSAMENTO
# =========================
result = []

for name, cfg in ativos.items():

    s = load(cfg["ticker"])
    if s is None:
        continue

    f = force(s)

    try:
        direction = np.sign(s.iloc[-1] - s.iloc[-2])
    except:
        direction = 0

    impact = f * cfg["corr"] * direction * 100

    result.append({
        "Ativo": name,
        "Impacto": impact
    })

df = pd.DataFrame(result)

if df.empty:
    st.error("Sem dados disponíveis")
    st.stop()

# =========================
# PRESSÃO AGREGADA
# =========================
buy = df[df["Impacto"] > 0]["Impacto"].sum()
sell = abs(df[df["Impacto"] < 0]["Impacto"].sum())

total = buy + sell + 1e-9

pct_buy = buy / total
pct_sell = sell / total

if pct_buy > 0.55:
    trend = "🟢 COMPRA"
elif pct_sell > 0.55:
    trend = "🔴 VENDA"
else:
    trend = "🟡 NEUTRO"

# =========================
# LÍDER
# =========================
df = df.sort_values("Impacto", ascending=False)
leader = df.iloc[0]["Ativo"]

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

st.caption("MACA-QUANTI | correlação + força relativa")

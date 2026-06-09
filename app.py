import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="MACA-QUANTI v9.5", layout="wide")

st.markdown("""
<style>
div[data-testid="metric-container"] {
    min-width: 110px;
}
</style>
""", unsafe_allow_html=True)

st.title("🏛️ MACA-QUANTI ELITE v9.5 | Bloomberg Terminal")

# =========================
# MAPA
# =========================
vies_ativos = {
    "FIXA11.SA": {"nome": "JRS", "corr": -1.0, "peso": 1.2},
    "BRL=X":     {"nome": "USD", "corr": -1.0, "peso": 1.2},
    "FIND11.SA": {"nome": "FIN", "corr": 1.0,  "peso": 0.8},
    "EWZ":       {"nome": "EWZ", "corr": 1.0,  "peso": 0.8},
    "ES=F":      {"nome": "SPX", "corr": 1.0,  "peso": 0.6},
    "^VIX":      {"nome": "VIX", "corr": -1.0, "peso": 0.5},
    "NQ=F":      {"nome": "NDX", "corr": 1.0,  "peso": 0.4},
}

# =========================
# MOTOR
# =========================
@st.cache_data(ttl=60)
def engine():
    out = []

    for cod, cfg in vies_ativos.items():
        df = yf.download(cod, period="60d", interval="1d", progress=False)
        if df.empty:
            continue

        c = df["Close"]
        if isinstance(c, pd.DataFrame):
            c = c.iloc[:, -1]

        z = (c.iloc[-1] - c.rolling(20).mean().iloc[-1]) / max(c.rolling(20).std().iloc[-1], 1e-9)
        score = np.tanh(z * 0.5) * 100

        out.append({
            "Ativo": cfg["nome"],
            "Impacto": score * cfg["corr"] * cfg["peso"]
        })

    return pd.DataFrame(out)

df = engine()
if df.empty:
    st.stop()

# =========================
# MÉTRICAS CORE
# =========================
total_abs = df["Impacto"].abs().sum() + 1e-9
hhi = np.sum((df["Impacto"].abs() / total_abs) ** 2)

raw = df["Impacto"].sum() / total_abs
forca = np.tanh(raw)

qualidade = 1 - hhi
intensidade = abs(forca) * (1 - hhi)

driver = df.loc[df["Impacto"].abs().idxmax(), "Ativo"]

vix = df.loc[df["Ativo"] == "VIX", "Impacto"].values[0] if "VIX" in df["Ativo"].values else 0
spx = df.loc[df["Ativo"] == "SPX", "Impacto"].values[0] if "SPX" in df["Ativo"].values else 0

# =========================
# REGIME ENGINE
# =========================
if vix > 10 and abs(spx) < 5:
    regime = "CONFLITO"
elif vix > 15 and spx < 0:
    regime = "RISK OFF"
elif hhi > 0.4:
    regime = "DOMINÂNCIA"
elif hhi < 0.25:
    regime = "COMPRESSÃO"
elif forca > 0.2:
    regime = "RISK ON"
else:
    regime = "NEUTRO"

# =========================
# HEADER BLOOMBERG BAR
# =========================
colA, colB, colC, colD = st.columns(4)

colA.metric("REGIME", regime)
colB.metric("DRIVER", driver)
colC.metric("HHI", f"{hhi:.2f}")
colD.metric("INT", f"{intensidade:.2f}")

st.divider()

# =========================
# LEFT: SCOREBOARD
# =========================
left, right = st.columns([1, 2])

with left:
    st.subheader("BÚSSOLA")

    if forca > 0.2:
        st.markdown("## 🟢 BUY FLOW")
    elif forca < -0.2:
        st.markdown("## 🔴 SELL FLOW")
    else:
        st.markdown("## ⚪ NEUTRAL")

    st.caption(f"Força: {forca:.2f}")

# =========================
# RIGHT: BLOOMBERG HEAT LIST
# =========================
with right:
    st.subheader("MARKET PULSE")

    def style(val):
        if val > 0:
            return "color:#00ff88;font-weight:700"
        return "color:#ff4d4d;font-weight:700"

    view = df.copy()
    view["DIR"] = np.where(view["Impacto"] > 0, "▲", "▼")
    view["Impacto"] = view["Impacto"].round(2)

    st.dataframe(
        view[["Ativo", "DIR", "Impacto"]]
        .sort_values("Impacto", ascending=False)
        .style.applymap(style, subset=["Impacto"]),
        use_container_width=True,
        hide_index=True
    )

# =========================
# FOOTER
# =========================
st.caption(
    f"v9.5 | Regime={regime} | Qualidade={qualidade:.2f} | Intensidade={intensidade:.2f} | HHI={hhi:.2f}"
)

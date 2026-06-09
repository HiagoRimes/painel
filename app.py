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
# ASSETS
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
# ENGINE
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

        mean20 = c.rolling(20).mean().iloc[-1]
        std20 = c.rolling(20).std().iloc[-1]

        z = (c.iloc[-1] - mean20) / max(std20, 1e-9)
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
# METRICS
# =========================
total_abs = df["Impacto"].abs().sum() + 1e-9

hhi = np.sum((df["Impacto"].abs() / total_abs) ** 2)
qualidade = 1 - hhi

raw = df["Impacto"].sum() / total_abs
forca = np.tanh(raw)

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

consenso = 1 - hhi if forca > 0 else hhi

# =========================
# HEADER
# =========================
c1, c2, c3, c4 = st.columns(4)

c1.metric("REGIME", regime)
c2.metric("DRIVER", driver)
c3.metric("HHI", f"{hhi:.2f}")
c4.metric("INT", f"{intensidade:.2f}")

st.divider()

# =========================
# LEFT PANEL
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
# RIGHT PANEL (FIX STREAMLIT STYLE BUG)
# =========================
with right:
    st.subheader("MARKET PULSE")

    view = df.copy()
    view["DIR"] = np.where(view["Impacto"] > 0, "▲", "▼")
    view["Impacto"] = view["Impacto"].round(2)

    # stable coloring (NO .style.applymap / NO Streamlit crash)
    view["Impacto"] = view["Impacto"].apply(
        lambda x: f"🟢 {x:.2f}" if x > 0 else f"🔴 {x:.2f}"
    )

    st.dataframe(
        view[["Ativo", "DIR", "Impacto"]].sort_values("Impacto", ascending=False),
        use_container_width=True,
        hide_index=True
    )

# =========================
# FOOTER
# =========================
st.caption(
    f"v9.5 | Regime={regime} | Qualidade={qualidade:.2f} | Intensidade={intensidade:.2f} | HHI={hhi:.2f} | Consenso={consenso:.2f}"
)

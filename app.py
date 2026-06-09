import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="MACA-QUANTI v10.0", layout="wide")

st.title("🏛️ MACA-QUANTI v10.0 | FLOW DESK (Bloomberg Style)")

# =========================
# ASSETS
# =========================
assets = {
    "FIXA11.SA": {"name": "JRS", "corr": -1},
    "BRL=X":     {"name": "USD", "corr": -1},
    "FIND11.SA": {"name": "FIN", "corr": 1},
    "EWZ":       {"name": "EWZ", "corr": 1},
    "ES=F":      {"name": "SPX", "corr": 1},
    "^VIX":      {"name": "VIX", "corr": -1},
    "NQ=F":      {"name": "NDX", "corr": 1},
}

# =========================
# DATA ENGINE
# =========================
@st.cache_data(ttl=60)
def build():
    rows = []

    for k, v in assets.items():
        df = yf.download(k, period="60d", interval="1d", progress=False)
        if df.empty:
            continue

        c = df["Close"]
        if isinstance(c, pd.DataFrame):
            c = c.iloc[:, 0]

        ma = c.rolling(20).mean().iloc[-1]
        std = c.rolling(20).std().iloc[-1]

        z = (c.iloc[-1] - ma) / max(std, 1e-9)

        impact = np.tanh(z) * v["corr"]

        rows.append({
            "Asset": v["name"],
            "Impact": impact
        })

    return pd.DataFrame(rows)

df = build()
if df.empty:
    st.stop()

# =========================
# FLOW METRICS
# =========================
total = df["Impact"].abs().sum() + 1e-9

df["Weight"] = df["Impact"].abs() / total
df["Contribution"] = df["Impact"] * df["Weight"]

flow_score = df["Contribution"].sum()

hhi = np.sum(df["Weight"] ** 2)

driver = df.loc[df["Impact"].abs().idxmax(), "Asset"]

vix = df[df["Asset"] == "VIX"]["Impact"].values[0] if "VIX" in df["Asset"].values else 0
spx = df[df["Asset"] == "SPX"]["Impact"].values[0] if "SPX" in df["Asset"].values else 0

# =========================
# REGIME ENGINE
# =========================
if vix > 0.6:
    regime = "RISK OFF (Stress)"
elif flow_score > 0.15:
    regime = "RISK ON"
elif flow_score < -0.15:
    regime = "RISK OFF"
elif hhi > 0.35:
    regime = "IMBALANCED FLOW"
else:
    regime = "NEUTRAL"

# =========================
# HEADER (BLOOMBERG BAR)
# =========================
c1, c2, c3, c4 = st.columns(4)

c1.metric("REGIME", regime)
c2.metric("DRIVER", driver)
c3.metric("FLOW", f"{flow_score:.3f}")
c4.metric("HHI", f"{hhi:.2f}")

st.divider()

# =========================
# LEFT: SIGNAL
# =========================
left, right = st.columns([1, 2])

with left:
    st.subheader("WIN BIAS")

    if flow_score > 0.15:
        st.markdown("## 🟢 BUY PRESSURE")
    elif flow_score < -0.15:
        st.markdown("## 🔴 SELL PRESSURE")
    else:
        st.markdown("## ⚪ NO EDGE")

    st.caption("Flow Score = directional institutional pressure")

# =========================
# RIGHT: BLOOMBERG HEAT MAP
# =========================
with right:
    st.subheader("INSTITUTIONAL FLOW MAP")

    view = df.copy()

    view["DIR"] = np.where(view["Impact"] > 0, "▲", "▼")

    view = view.sort_values("Impact", ascending=False)

    def color(x):
        return "color:#00ff88;font-weight:700" if x > 0 else "color:#ff4d4d;font-weight:700"

    styled = view.style.map(color, subset=["Impact"])

    st.dataframe(
        styled,
        use_container_width=True,
        hide_index=True
    )

# =========================
# FLOW BAR (VISUAL INTUITION)
# =========================
st.subheader("FLOW INTENSITY (WIN DIRECTION PUSH)")

chart_df = df.sort_values("Impact")

st.bar_chart(chart_df.set_index("Asset")["Impact"])

# =========================
# LEGEND
# =========================
with st.expander("How to read this panel"):
    st.markdown("""
- **FLOW SCORE**: directional pressure from global assets into WIN
- **HHI**: concentration of dominance (low = diversified, high = single driver)
- **DRIVER**: asset currently controlling direction
- **GREEN**: bullish pressure
- **RED**: bearish pressure
- WIN is **a consequence**, not a driver
""")

st.caption(f"v10.0 | Flow={flow_score:.3f} | HHI={hhi:.2f} | Regime={regime}")

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# =========================
# CONFIG BLOOMBERG STYLE
# =========================
st.set_page_config(page_title="MACA-QUANTI v13.0", layout="wide")

st.markdown(
    "<h2 style='text-align:center;'>MACA-QUANTI | MARKET DESK</h2>",
    unsafe_allow_html=True
)

# =========================
# UNIVERSE (CLEAN LABELS)
# =========================
assets = {
    "FIXA11.SA": {"name": "RATES", "label": "JUROS", "corr": -1},
    "BRL=X":     {"name": "FX", "label": "USD", "corr": -1},
    "FIND11.SA": {"name": "EQ", "label": "FIN", "corr": 1},
    "EWZ":       {"name": "EQ", "label": "BRL EQ", "corr": 1},
    "ES=F":      {"name": "EQ", "label": "SPX", "corr": 1},
    "NQ=F":      {"name": "EQ", "label": "NDX", "corr": 1},
    "^VIX":      {"name": "VOL", "label": "VIX", "corr": -1},
}

# =========================
# ENGINE
# =========================
@st.cache_data(ttl=60)
def engine():
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
            "GROUP": v["name"],
            "ASSET": v["label"],
            "IMPACT": impact
        })

    return pd.DataFrame(rows)

df = engine()
if df.empty:
    st.stop()

# =========================
# CORE METRICS
# =========================
df["WEIGHT"] = df["IMPACT"].abs() / (df["IMPACT"].abs().sum() + 1e-9)

flow = (df["IMPACT"] * df["WEIGHT"]).sum()
hhi = np.sum(df["WEIGHT"] ** 2)

driver = df.loc[df["IMPACT"].abs().idxmax(), "ASSET"]

vix = df[df["ASSET"] == "VIX"]["IMPACT"].values
vix = vix[0] if len(vix) else 0

# =========================
# REGIME ENGINE
# =========================
if vix > 0.6:
    regime = "RISKOFF"
elif flow > 0.2:
    regime = "RISKON"
elif abs(flow) < 0.1:
    regime = "NEUTRAL"
elif hhi > 0.45:
    regime = "CONCENTRATED"
else:
    regime = "DIRECTIONAL"

# =========================
# HEADER (BLOOMBERG STYLE)
# =========================
c1, c2, c3, c4 = st.columns(4)

c1.metric("REGIME", regime)
c2.metric("DRIVER", driver)
c3.metric("FLOW", f"{flow:.3f}")
c4.metric("HHI", f"{hhi:.2f}")

st.divider()

# =========================
# TABLE DESK STYLE
# =========================
st.markdown("### MARKET FLOW")

view = df.sort_values("IMPACT", ascending=False).copy()

def fmt(x):
    sign = "▲" if x > 0 else "▼"
    return f"{sign} {x:.3f}"

view["IMPACT"] = view["IMPACT"].apply(fmt)

st.dataframe(
    view[["GROUP", "ASSET", "IMPACT"]],
    use_container_width=True,
    hide_index=True
)

st.divider()

# =========================
# DESK VIEW (RAW LIST)
# =========================
st.markdown("### TAPE")

for _, r in view.iterrows():
    st.write(f"{r['GROUP']} | {r['ASSET']} | {r['IMPACT']}")

# =========================
# FOOTER
# =========================
st.caption(f"v13.0 | FLOW={flow:.3f} | HHI={hhi:.2f} | MODE=BLOOMBERG")

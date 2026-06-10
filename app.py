import streamlit as st
import yfinance as yf
import numpy as np

st.set_page_config(page_title="MACRO WIN DASHBOARD", layout="wide")

st.title("MACRO WIN DASHBOARD (WORKING VERSION)")

# =========================
# ASSETS
# =========================

assets = {
    "ES": "^GSPC",
    "NQ": "^IXIC",
    "VIX": "^VIX",
    "DXY": "UUP",
    "US10Y": "^TNX"
}

# =========================
# DATA LOAD
# =========================

data = {}
status = {}

for k, v in assets.items():
    try:
        df = yf.download(v, period="10d", interval="1h", progress=False)
        data[k] = df
        status[k] = "OK" if df is not None and not df.empty else "EMPTY"
    except:
        data[k] = None
        status[k] = "ERROR"

# =========================
# SAFE RETURN (ROBUSTO)
# =========================

def safe_ret(df):
    try:
        if df is None or df.empty:
            return 0.0

        close = df["Close"].dropna()

        if len(close) < 10:
            return 0.0

        last = close.iloc[-1]
        prev = close.iloc[-10]

        if prev == 0:
            return 0.0

        return float(np.log(last / prev))

    except:
        return 0.0

# =========================
# MACRO SCORE (ESTÁVEL)
# =========================

def calculate_macro_score(data):

    es = safe_ret(data.get("ES"))
    nq = safe_ret(data.get("NQ"))
    vix = safe_ret(data.get("VIX"))
    dxy = safe_ret(data.get("DXY"))

    score = 0.0

    # risco global
    score += es
    score += nq

    # risco-off (invertido)
    score -= vix

    # dólar (invertido)
    score -= dxy

    if score > 0.01:
        label = "RISK-ON"
    elif score < -0.01:
        label = "RISK-OFF"
    else:
        label = "NEUTRO"

    return {
        "score": round(score, 4),
        "label": label,
        "details": {
            "ES": es,
            "NQ": nq,
            "VIX": vix,
            "DXY": dxy
        }
    }

# =========================
# REGIME
# =========================

def detect_regime(data):

    try:
        vix = data["VIX"]["Close"].iloc[-1]

        if vix > 20:
            return "SHOCK"
        elif vix > 15:
            return "CHOP"
        else:
            return "TREND"
    except:
        return "UNKNOWN"

# =========================
# BRASIL
# =========================

def brazil_context():
    return {
        "USD/BRL": "não integrado",
        "DI Futuro": "proxy juros Brasil",
        "IFNC": "bancos como risco local",
        "Nota": "Brasil segue fluxo global na maior parte do tempo"
    }

# =========================
# WIN SIGNAL
# =========================

def win_signal(macro, regime):

    if regime == "SHOCK":
        return "NO TRADE"

    score = macro["score"]

    if score > 0.02 and regime == "TREND":
        return "LONG WIN"

    if score < -0.02 and regime == "TREND":
        return "SHORT WIN"

    return "NO TRADE"

# =========================
# RUN
# =========================

macro = calculate_macro_score(data)
regime = detect_regime(data)
brasil = brazil_context()
signal = win_signal(macro, regime)

# =========================
# UI
# =========================

col1, col2, col3 = st.columns(3)

col1.metric("Macro Score", macro["score"], macro["label"])
col2.metric("Regime", regime)
col3.metric("WIN Signal", signal)

st.divider()

st.subheader("Status dos Dados")
st.json(status)

st.subheader("Detalhes Macro")
st.json(macro["details"])

st.subheader("Contexto Brasil")
st.json(brasil)

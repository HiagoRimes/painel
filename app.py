import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="MACRO WIN DASHBOARD", layout="wide")

st.title("MACRO WIN DASHBOARD (STABLE FIXED)")

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

for k, v in assets.items():
    try:
        df = yf.download(v, period="5d", interval="1h", progress=False)
        data[k] = df
    except:
        data[k] = None

# =========================
# SAFE RETURN (FIX DEFINITIVO)
# =========================

def safe_ret(df):
    try:
        if df is None or df.empty:
            return 0.0

        close = df["Close"]

        # garante Series simples
        if hasattr(close, "values"):
            close = close.values

        if len(close) < 2:
            return 0.0

        # retorno simples e seguro
        return float((close[-1] / close[-2]) - 1)

    except:
        return 0.0

# =========================
# MACRO SCORE
# =========================

def calculate_macro_score(data):

    es = safe_ret(data.get("ES"))
    nq = safe_ret(data.get("NQ"))
    vix = safe_ret(data.get("VIX"))
    dxy = safe_ret(data.get("DXY"))

    score = 0

    # Risk assets
    score += 1 if es > 0 else -1
    score += 1 if nq > 0 else -1

    # Risk-off proxy (invertido)
    score += 1 if vix < 0 else -1

    # Dollar effect (invertido)
    score += 1 if dxy < 0 else -1

    if score >= 3:
        label = "RISK-ON FORTE"
    elif score == 2:
        label = "RISK-ON"
    elif score in [1, 0]:
        label = "NEUTRO"
    else:
        label = "RISK-OFF"

    return {
        "score": score,
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
# BRASIL CONTEXT
# =========================

def brazil_context():

    return {
        "USD/BRL": "não integrado neste MVP",
        "DI Futuro": "proxy juros Brasil",
        "IFNC": "bancos como risco local",
        "Nota": "Brasil segue fluxo global na maior parte do tempo"
    }

# =========================
# WIN SIGNAL
# =========================

def win_signal(macro, regime):

    score = macro["score"]

    if regime == "SHOCK":
        return "NO TRADE"

    if score >= 3 and regime == "TREND":
        return "LONG WIN"

    if score <= -2 and regime == "TREND":
        return "SHORT WIN"

    return "NO TRADE"

# =========================
# RUN MODEL
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

st.subheader("Detalhes Macro")
st.json(macro["details"])

st.subheader("Contexto Brasil")
st.json(brasil)

st.subheader("Estrutura do Sistema")

st.write("""
Sistema macro estruturado:

1. Risco global (ES, NQ, VIX, DXY)
2. Regime de volatilidade
3. Contexto Brasil
4. WIN como execução final

Regra:
WIN nunca lidera — apenas executa o fluxo dominante.
""")

import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="MACRO WIN DASHBOARD", layout="wide")

st.title("MACRO WIN DASHBOARD (DEBUG + STABLE)")

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

        if df is None or df.empty:
            status[k] = "NO DATA"
        else:
            status[k] = "OK"

        data[k] = df

    except Exception as e:
        data[k] = None
        status[k] = f"ERROR: {str(e)[:30]}"

# =========================
# SAFE RETURN (ROBUSTO)
# =========================

def safe_ret(df):

    try:
        if df is None or df.empty:
            return None

        close = df["Close"].dropna()

        if len(close) < 10:
            return None

        return float((close.iloc[-1] / close.iloc[-10]) - 1)

    except:
        return None

# =========================
# MACRO SCORE
# =========================

def calculate_macro_score(data):

    es = safe_ret(data.get("ES"))
    nq = safe_ret(data.get("NQ"))
    vix = safe_ret(data.get("VIX"))
    dxy = safe_ret(data.get("DXY"))

    # se qualquer ativo falhar, NÃO força score
    valid_values = [x for x in [es, nq, vix, dxy] if x is not None]

    if len(valid_values) < 3:
        return {
            "score": 0,
            "label": "INSUFFICIENT DATA",
            "details": {
                "ES": es,
                "NQ": nq,
                "VIX": vix,
                "DXY": dxy
            }
        }

    score = 0

    score += 1 if es > 0 else -1
    score += 1 if nq > 0 else -1
    score += 1 if vix < 0 else -1
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
# SIGNAL
# =========================

def win_signal(macro, regime):

    if macro["label"] == "INSUFFICIENT DATA":
        return "NO TRADE"

    score = macro["score"]

    if regime == "SHOCK":
        return "NO TRADE"

    if score >= 3 and regime == "TREND":
        return "LONG WIN"

    if score <= -2 and regime == "TREND":
        return "SHORT WIN"

    return "NO TRADE"

# =========================
# RUN
# =========================

macro = calculate_macro_score(data)
regime = detect_regime(data)
br = brazil_context()
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
st.json(br)

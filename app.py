import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="MACA-QUANTI v12.0", layout="wide")

st.title("🏛️ MACA-QUANTI v12.0 | PAINEL DE REGIME GLOBAL")

# =========================
# UNIVERSO POR BLOCO
# =========================
assets = {
    # RATES
    "FIXA11.SA": {"name": "JUROS", "corr": -1, "group": "RATES"},

    # FX
    "BRL=X": {"name": "DÓLAR", "corr": -1, "group": "FX"},

    # EQUITY BRASIL
    "FIND11.SA": {"name": "FINANCEIRO", "corr": 1, "group": "EQUITY"},
    "EWZ": {"name": "BOLSA BRASIL", "corr": 1, "group": "EQUITY"},

    # GLOBAL EQUITY
    "ES=F": {"name": "S&P 500", "corr": 1, "group": "EQUITY"},
    "NQ=F": {"name": "NASDAQ", "corr": 1, "group": "EQUITY"},

    # VOL
    "^VIX": {"name": "VOLATILIDADE (VIX)", "corr": -1, "group": "VOL"},
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
            "Ativo": v["name"],
            "Grupo": v["group"],
            "Impacto": impact
        })

    return pd.DataFrame(rows)

df = engine()
if df.empty:
    st.stop()

# =========================
# METRICS GLOBAIS
# =========================
df["Peso"] = df["Impacto"].abs() / (df["Impacto"].abs().sum() + 1e-9)

flow_global = (df["Impacto"] * df["Peso"]).sum()
hhi = np.sum(df["Peso"] ** 2)

driver = df.loc[df["Impacto"].abs().idxmax(), "Ativo"]

# =========================
# FUNÇÃO REGIME
# =========================
vix = df[df["Ativo"] == "VOLATILIDADE (VIX)"]["Impacto"].values
vix = vix[0] if len(vix) else 0

spx = df[df["Ativo"] == "S&P 500"]["Impacto"].values
spx = spx[0] if len(spx) else 0

if vix > 0.6:
    regime = "🚨 STRESS / RISK OFF"
elif vix < -0.3 and flow_global > 0.2:
    regime = "🟢 RISK ON FORTE"
elif hhi > 0.45:
    regime = "⚠️ MERCADO CONCENTRADO"
elif abs(flow_global) < 0.1:
    regime = "⚪ COMPRESSÃO / NEUTRO"
else:
    regime = "🟡 DIRECIONAL MODERADO"

# =========================
# HEADER
# =========================
c1, c2, c3, c4 = st.columns(4)

c1.metric("REGIME", regime)
c2.metric("DRIVER", driver)
c3.metric("FLUXO GLOBAL", f"{flow_global:.3f}")
c4.metric("HHI", f"{hhi:.2f}")

st.divider()

# =========================
# FUNÇÃO DE BLOCO
# =========================
def bloco(nome, grupo):
    st.subheader(nome)

    temp = df[df["Grupo"] == grupo].sort_values("Impacto", ascending=False)

    for _, r in temp.iterrows():
        cor = "🟢" if r["Impacto"] > 0 else "🔴"
        st.write(f"{cor} {r['Ativo']}  |  {r['Impacto']:.3f}")

# =========================
# PAINEL POR REGIME
# =========================
col1, col2 = st.columns(2)

with col1:
    bloco("RATES (JUROS)", "RATES")
    bloco("FX (CÂMBIO)", "FX")

with col2:
    bloco("EQUITY (RISCO)", "EQUITY")
    bloco("VOL (STRESS)", "VOL")

st.divider()

# =========================
# LEITURA FINAL
# =========================
st.subheader("LEITURA DE MERCADO")

if flow_global > 0.2:
    st.success("FLUXO POSITIVO DOMINANTE")
elif flow_global < -0.2:
    st.error("FLUXO NEGATIVO DOMINANTE")
else:
    st.warning("MERCADO SEM DIREÇÃO CLARA")

st.caption(
    f"v12.0 | regime system | flow={flow_global:.3f} | hhi={hhi:.2f} | driver={driver}"
)

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# =========================
# CONFIGURAÇÃO
# =========================
st.set_page_config(page_title="MACA-QUANTI", layout="wide")
st.title("🏛️ MACA-QUANTI | Radar de Dominância")

# =========================
# UNIVERSO ESTÁVEL (Yahoo)
# =========================
ativos = {
    "JUROS LONGOS": {"ticker": "TLT", "corr": -1},
    "DÓLAR": {"ticker": "UUP", "corr": -1},
    "VOLATILIDADE": {"ticker": "VXX", "corr": -1},
    "S&P 500": {"ticker": "SPY", "corr": 1},
    "NASDAQ": {"ticker": "QQQ", "corr": 1},
    "FINANCEIRO": {"ticker": "XLF", "corr": 1},
    "MATERIAIS": {"ticker": "XLB", "corr": 1},
    "PETROBRAS": {"ticker": "PETR4.SA", "corr": 1},
    "VALE": {"ticker": "VALE3.SA", "corr": 1},
    "BRASIL (IBOV)": {"ticker": "EWZ", "corr": 1},
}

# =========================
# DADOS
# =========================
@st.cache_data(ttl=60)
def baixar(ticker):
    try:
        df = yf.download(ticker, period="5d", interval="5m", progress=False)
        if df is None or df.empty:
            return None
        serie = df["Close"].dropna()
        if len(serie) < 30:
            return None
        return serie
    except:
        return None

# =========================
# SCORE (ROBUSTO FINAL)
# =========================
def score(series):
    if series is None or len(series) < 30:
        return 0

    try:
        series = series.dropna()

        roll = series.rolling(30)

        atual = float(series.iloc[-1])
        media = float(roll.mean().iloc[-1])
        std = roll.std().iloc[-1]

        # força std escalar (corrige erro pandas/Series)
        if isinstance(std, pd.Series):
            std = float(std.iloc[-1])

        std = float(std)

        if std == 0 or np.isnan(std) or np.isinf(std):
            return 0

        z = (atual - media) / std

        if np.isnan(z) or np.isinf(z):
            return 0

        return np.tanh(z)

    except:
        return 0

# =========================
# PROCESSAMENTO
# =========================
resultados = []

for nome, cfg in ativos.items():

    serie = baixar(cfg["ticker"])
    if serie is None:
        continue

    s = score(serie)

    try:
        direcao = np.sign(float(serie.iloc[-1]) - float(serie.iloc[-2]))
    except:
        direcao = 0

    impacto = s * cfg["corr"] * direcao * 100

    resultados.append({
        "Ativo": nome,
        "Impacto": impacto
    })

df = pd.DataFrame(resultados)

if df.empty:
    st.error("Sem dados suficientes (Yahoo falhou)")
    st.stop()

# =========================
# PRESSÃO AGREGADA
# =========================
compra = df[df["Impacto"] > 0]["Impacto"].sum()
venda = abs(df[df["Impacto"] < 0]["Impacto"].sum())

total = compra + venda + 1e-9

pct_compra = compra / total
pct_venda = venda / total

if pct_compra > 0.55:
    tendencia = "🟢 COMPRA"
elif pct_venda > 0.55:
    tendencia = "🔴 VENDA"
else:
    tendencia = "🟡 NEUTRO"

# =========================
# LÍDER
# =========================
df = df.sort_values("Impacto", ascending=False)
lider = df.iloc[0]["Ativo"]

# =========================
# UI PRINCIPAL
# =========================
col1, col2, col3 = st.columns(3)

col1.metric("Tendência", tendencia)
col2.metric("Líder do Momento", lider)
col3.metric("Atualização", datetime.now().strftime("%H:%M:%S"))

st.divider()

st.subheader("Pressão Agregada")
st.write(f"🟢 Compra: {pct_compra:.2%}")
st.write(f"🔴 Venda: {pct_venda:.2%}")

st.divider()

st.subheader("Ranking de Liderança")

def cor(v):
    if v > 0:
        return "🟢"
    elif v < 0:
        return "🔴"
    return "🟡"

df["Sinal"] = df["Impacto"].apply(cor)

st.dataframe(
    df[["Sinal", "Ativo", "Impacto"]],
    use_container_width=True
)

st.divider()

st.subheader("Regime de Mercado")

if pct_compra > 0.6:
    regime = "🟢 Direcional Altista"
elif pct_venda > 0.6:
    regime = "🔴 Direcional Baixista"
else:
    regime = "🟡 Neutro / Compressão"

st.write(regime)

st.caption("MACA-QUANTI v1 | Radar de dominância intradiária")

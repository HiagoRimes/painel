import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# =========================
# CONFIGURAÇÃO
# =========================
st.set_page_config(page_title="MACA-QUANTI ELITE v1", layout="wide")
st.title("🏛️ MACA-QUANTI ELITE v1 | Radar de Dominância de Mercado")

# =========================
# UNIVERSO
# =========================
ativos = {
    "JUROS LONGOS": {"ticker": "TLT", "corr": -1.0},
    "DÓLAR": {"ticker": "DX-Y.NYB", "corr": -1.0},
    "VOLATILIDADE (VIX)": {"ticker": "^VIX", "corr": -1.0},
    "SETOR FINANCEIRO": {"ticker": "XLF", "corr": 1.0},
    "MATERIAIS BÁSICOS": {"ticker": "XLB", "corr": 1.0},
    "PETROBRAS": {"ticker": "PETR4.SA", "corr": 1.0},
    "VALE": {"ticker": "VALE3.SA", "corr": 1.0},
    "S&P 500": {"ticker": "^GSPC", "corr": 1.0},
    "NASDAQ": {"ticker": "^IXIC", "corr": 1.0},
}

indice_ref = "^BVSP"

# =========================
# DADOS (ROBUSTO)
# =========================
@st.cache_data(ttl=60)
def baixar(ticker):
    for interval in ["1m", "5m"]:
        try:
            df = yf.download(
                ticker,
                period="5d",
                interval=interval,
                progress=False
            )

            if df is not None and not df.empty:
                serie = df["Close"].dropna()

                if len(serie) > 30:
                    return serie

        except:
            continue

    return None


# =========================
# MOVIMENTO ANORMAL
# =========================
def movimento_anormal(series):
    if series is None or len(series) < 50:
        return 0

    try:
        series = series.dropna()

        roll = series.rolling(50)

        atual = float(series.iloc[-1])
        media = float(roll.mean().iloc[-1])
        std = float(roll.std().iloc[-1])

        if std == 0 or np.isnan(std):
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

    score = movimento_anormal(serie)

    try:
        direcao = np.sign(float(serie.iloc[-1]) - float(serie.iloc[-2]))
    except:
        direcao = 0

    impacto = score * cfg["corr"] * direcao * 100

    if abs(impacto) < 1:
        continue

    resultados.append({
        "Ativo": nome,
        "Impacto": impacto,
    })

df = pd.DataFrame(resultados)

if df.empty:
    st.error("Sem dados suficientes — Yahoo falhou na coleta")
    st.stop()

# =========================
# PRESSÃO REAL
# =========================
df["Pressão"] = df["Impacto"]

compra = df[df["Pressão"] > 0]["Pressão"].sum()
venda = abs(df[df["Pressão"] < 0]["Pressão"].sum())

total = compra + venda

if total == 0:
    pct_compra = 0
    pct_venda = 0
else:
    pct_compra = compra / total
    pct_venda = venda / total

if pct_compra > 0.55:
    tendencia = "🟢 TENDÊNCIA DE COMPRA"
elif pct_venda > 0.55:
    tendencia = "🔴 TENDÊNCIA DE VENDA"
else:
    tendencia = "🟡 NEUTRO"

# =========================
# LÍDER
# =========================
df = df.sort_values("Impacto", ascending=False)
lider = df.iloc[0]["Ativo"]

# =========================
# UI
# =========================
col1, col2, col3 = st.columns(3)

col1.metric("Tendência do Mercado", tendencia)
col2.metric("Líder do Momento", lider)
col3.metric("Atualização", datetime.now().strftime("%H:%M:%S"))

st.divider()

st.subheader("Pressão Agregada")
st.write(f"🟢 Compra: {pct_compra:.2%}")
st.write(f"🔴 Venda: {pct_venda:.2%}")

st.divider()

st.subheader("Ranking de Liderança")

def cor(v):
    return "🟢" if v > 0 else "🔴" if v < 0 else "🟡"

df["Sinal"] = df["Impacto"].apply(cor)

st.dataframe(df, use_container_width=True)

st.divider()

st.subheader("Alertas")

alertas = df[abs(df["Impacto"]) > 70]

if alertas.empty:
    st.write("Sem movimentos extremos no momento.")
else:
    st.dataframe(alertas)

st.divider()

st.subheader("Regime de Mercado")

if pct_compra > 0.6:
    regime = "🟢 Direcional Altista"
elif pct_venda > 0.6:
    regime = "🔴 Direcional Baixista"
else:
    regime = "🟡 Neutro / Compressão"

st.write(regime)

st.caption("v1 | MACA-QUANTI")

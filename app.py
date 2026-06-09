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
# UNIVERSO DE ATIVOS
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
# DADOS
# =========================
@st.cache_data(ttl=60)
def baixar(ticker, period="5d", interval="1m"):
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        if df is None or df.empty:
            return None
        serie = df["Close"].dropna()
        if len(serie) < 5:
            return None
        return serie
    except:
        return None


# =========================
# MOVIMENTO ANORMAL (ROBUSTO)
# =========================
def movimento_anormal(series):
    try:
        if series is None:
            return 0

        series = series.dropna()

        if len(series) < 50:
            return 0

        roll = series.rolling(50)

        atual = series.iloc[-1]
        media = roll.mean().iloc[-1]
        std = roll.std().iloc[-1]

        if pd.isna(atual) or pd.isna(media) or pd.isna(std):
            return 0

        if std == 0 or std is None:
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

    # direção curta
    try:
        direcao = np.sign(float(serie.iloc[-1]) - float(serie.iloc[-2]))
    except:
        direcao = 0

    impacto = score * cfg["corr"] * direcao * 100

    resultados.append({
        "Ativo": nome,
        "Impacto": impacto,
        "Direção": direcao
    })

df = pd.DataFrame(resultados)

if df.empty:
    st.error("Sem dados suficientes no momento")
    st.stop()

# =========================
# PRESSÃO AGREGADA
# =========================
df["Pressão"] = df["Impacto"]

compra = df[df["Pressão"] > 0]["Pressão"].sum()
venda = abs(df[df["Pressão"] < 0]["Pressão"].sum())

total = compra + venda + 1e-9

pct_compra = compra / total
pct_venda = venda / total

if pct_compra > 0.55:
    tendencia = "🟢 TENDÊNCIA DE COMPRA"
elif pct_venda > 0.55:
    tendencia = "🔴 TENDÊNCIA DE VENDA"
else:
    tendencia = "🟡 NEUTRO"

# =========================
# ÍNDICE
# =========================
indice = baixar(indice_ref)

if indice is not None and len(indice) > 2:
    win_score = np.sign(indice.iloc[-1] - indice.iloc[-2])
else:
    win_score = 0

# =========================
# LIDERANÇA
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

# =========================
# PRESSÃO
# =========================
st.subheader("Pressão Agregada")

st.write(f"🟢 Compra: {pct_compra:.2%}")
st.write(f"🔴 Venda: {pct_venda:.2%}")

st.divider()

# =========================
# RANKING
# =========================
st.subheader("Ranking de Liderança")

def cor(v):
    if v > 0:
        return "🟢"
    elif v < 0:
        return "🔴"
    return "🟡"

df["Sinal"] = df["Impacto"].apply(cor)

st.dataframe(
    df[["Sinal", "Ativo", "Impacto"]].reset_index(drop=True),
    use_container_width=True
)

# =========================
# ALERTAS
# =========================
st.divider()
st.subheader("Alertas")

alertas = df[abs(df["Impacto"]) > 70]

if alertas.empty:
    st.write("Sem movimentos extremos no momento.")
else:
    st.dataframe(alertas[["Ativo", "Impacto"]])

# =========================
# REGIME
# =========================
st.divider()
st.subheader("Regime de Mercado")

if pct_compra > 0.6:
    regime = "🟢 Direcional Altista"
elif pct_venda > 0.6:
    regime = "🔴 Direcional Baixista"
else:
    regime = "🟡 Neutro / Compressão"

st.write(regime)

# =========================
# FOOTER
# =========================
st.caption("v1 | MACA-QUANTI | Radar de dominância e correlação intradiária")

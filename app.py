import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="MACA-QUANTI v10.1", layout="wide")

st.title("🏛️ MACA-QUANTI v10.1 | FLUXO INSTITUCIONAL")

# =========================
# ATIVOS
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
# ENGINE
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
            "Ativo": v["name"],
            "Impacto": impact
        })

    return pd.DataFrame(rows)

df = build()
if df.empty:
    st.stop()

# =========================
# METRICS
# =========================
total = df["Impacto"].abs().sum() + 1e-9

df["Peso"] = df["Impacto"].abs() / total
flow = (df["Impacto"] * df["Peso"]).sum()

driver = df.loc[df["Impacto"].abs().idxmax(), "Ativo"]

hhi = np.sum(df["Peso"] ** 2)

# =========================
# HEADER
# =========================
c1, c2, c3 = st.columns(3)

c1.metric("DRIVER DO MERCADO", driver)
c2.metric("FORÇA DO FLUXO", f"{flow:.3f}")
c3.metric("CONCENTRAÇÃO", f"{hhi:.2f}")

st.divider()

# =========================
# BÚSSOLA SIMPLES (PORTUGUÊS REAL)
# =========================
st.subheader("DIREÇÃO DO MERCADO")

if flow > 0.15:
    st.success("MERCADO COM PRESSÃO DE ALTA")
elif flow < -0.15:
    st.error("MERCADO COM PRESSÃO DE BAIXA")
else:
    st.warning("MERCADO SEM DIREÇÃO CLARA")

st.divider()

# =========================
# BARRA VISUAL (FOCO REAL)
# =========================
st.subheader("FORÇA DOS ATIVOS (EMPURRÃO NO WIN)")

def barra(valor):
    intensidade = min(abs(valor), 1)
    tamanho = int(intensidade * 20)

    if valor > 0:
        return "🟩" * tamanho
    else:
        return "🟥" * tamanho

view = df.sort_values("Impacto", ascending=False).copy()

view["FORÇA VISUAL"] = view["Impacto"].apply(barra)
view["Impacto"] = view["Impacto"].round(3)

st.dataframe(
    view[["Ativo", "FORÇA VISUAL", "Impacto"]],
    use_container_width=True,
    hide_index=True
)

# =========================
# GRÁFICO DE IMPACTO (LEITURA RÁPIDA)
# =========================
st.subheader("MAPA DE IMPACTO")

chart = df.set_index("Ativo")["Impacto"]
st.bar_chart(chart)

# =========================
# FOOTER
# =========================
st.caption(f"v10.1 | Flow={flow:.3f} | HHI={hhi:.2f}")

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="MACA-QUANTI v10.3", layout="wide")

st.title("🏛️ MACA-QUANTI v10.3 | FLUXO INSTITUCIONAL (DESK)")

# =========================
# ATIVOS (SEM SIGLAS)
# =========================
assets = {
    "FIXA11.SA": {"name": "JUROS", "corr": -1},
    "BRL=X":     {"name": "DÓLAR", "corr": -1},
    "FIND11.SA": {"name": "SETOR FINANCEIRO", "corr": 1},
    "EWZ":       {"name": "BOLSA BRASIL", "corr": 1},
    "ES=F":      {"name": "S&P 500", "corr": 1},
    "^VIX":      {"name": "VOLATILIDADE", "corr": -1},
    "NQ=F":      {"name": "NASDAQ", "corr": 1},
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
# MÉTRICAS
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
c1.metric("DRIVER", driver)
c2.metric("FLUXO", f"{flow:.3f}")
c3.metric("CONCENTRAÇÃO", f"{hhi:.2f}")

st.divider()

# =========================
# DIREÇÃO DO MERCADO
# =========================
st.subheader("DIREÇÃO DO MERCADO")

if flow > 0.15:
    st.success("MERCADO COM PRESSÃO DE ALTA")
elif flow < -0.15:
    st.error("MERCADO COM PRESSÃO DE BAIXA")
else:
    st.warning("MERCADO SEM DIREÇÃO DEFINIDA")

st.divider()

# =========================
# MAPA DE IMPACTO (LISTA PROFISSIONAL)
# =========================
st.subheader("MAPA DE IMPACTO (RANKING DE FLUXO)")

view = df.sort_values("Impacto", ascending=False).copy()

max_abs = view["Impacto"].abs().max() + 1e-9

def barra(x):
    n = int((abs(x) / max_abs) * 20)

    if x > 0:
        return "🟩" * n
    else:
        return "🟥" * n

view["FORÇA"] = view["Impacto"].apply(barra)
view["IMPACTO"] = view["Impacto"].round(3)

st.dataframe(
    view[["Ativo", "FORÇA", "IMPACTO"]],
    use_container_width=True,
    hide_index=True
)

# =========================
# RANKING SIMPLES (SEM GRÁFICO AZUL)
# =========================
st.subheader("RANKING DE DOMINÂNCIA")

rank = df.sort_values("Impacto", ascending=True).copy()

for i, row in rank.iterrows():
    cor = "🟢" if row["Impacto"] > 0 else "🔴"
    st.write(f"{cor} {row['Ativo']}  →  {row['Impacto']:.3f}")

# =========================
# FOOTER
# =========================
st.caption(f"v10.3 | Flow={flow:.3f} | HHI={hhi:.2f}")

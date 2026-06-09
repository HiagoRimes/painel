import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="MACA-QUANTI v11.0", layout="wide")

st.title("🏛️ MACA-QUANTI v11.0 | MESA INSTITUCIONAL")

# =========================
# UNIVERSO
# =========================
assets = {
    "FIXA11.SA": {"name": "JUROS", "corr": -1},
    "BRL=X":     {"name": "DÓLAR", "corr": -1},
    "FIND11.SA": {"name": "FINANCEIRO", "corr": 1},
    "EWZ":       {"name": "BOLSA BRASIL", "corr": 1},
    "ES=F":      {"name": "S&P 500", "corr": 1},
    "^VIX":      {"name": "VOLATILIDADE", "corr": -1},
    "NQ=F":      {"name": "NASDAQ", "corr": 1},
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

        mean = c.rolling(20).mean().iloc[-1]
        std = c.rolling(20).std().iloc[-1]

        z = (c.iloc[-1] - mean) / max(std, 1e-9)
        impact = np.tanh(z) * v["corr"]

        rows.append({
            "Ativo": v["name"],
            "Impacto": impact
        })

    return pd.DataFrame(rows)

df = engine()
if df.empty:
    st.stop()

# =========================
# METRICS CORE
# =========================
total_abs = df["Impacto"].abs().sum() + 1e-9

df["Peso"] = df["Impacto"].abs() / total_abs
flow = (df["Impacto"] * df["Peso"]).sum()

driver = df.loc[df["Impacto"].abs().idxmax(), "Ativo"]
hhi = np.sum(df["Peso"] ** 2)

# =========================
# HEADER (ESTILO MESA)
# =========================
c1, c2, c3 = st.columns(3)

c1.metric("DRIVER", driver)
c2.metric("FLUXO", f"{flow:.3f}")
c3.metric("CONCENTRAÇÃO", f"{hhi:.2f}")

st.divider()

# =========================
# BÚSSOLA SIMPLES
# =========================
st.subheader("DIREÇÃO DO MERCADO")

if flow > 0.15:
    st.markdown("### MERCADO COM VIÉS POSITIVO")
elif flow < -0.15:
    st.markdown("### MERCADO COM VIÉS NEGATIVO")
else:
    st.markdown("### MERCADO SEM DIREÇÃO")

st.divider()

# =========================
# TABELA LIMPA (MESA REAL)
# =========================
st.subheader("FLUXO INSTITUCIONAL")

view = df.sort_values("Impacto", ascending=False).copy()

def formatar(x):
    sinal = "▲" if x > 0 else "▼"
    return f"{sinal} {x:.3f}"

def cor(x):
    return "color:#00c853" if x > 0 else "color:#ff1744"

view["IMPACTO"] = view["Impacto"].apply(formatar)

styled = view.style.applymap(cor, subset=["Impacto"])

st.dataframe(
    styled[["Ativo", "IMPACTO"]],
    use_container_width=True,
    hide_index=True
)

# =========================
# RANKING SECO (LEITURA RÁPIDA)
# =========================
st.subheader("RANKING DE PRESSÃO")

for _, row in view.iterrows():
    if row["Impacto"].startswith("▲"):
        st.write(f"🟢 {row['Ativo']}  {row['IMPACTO']}")
    else:
        st.write(f"🔴 {row['Ativo']}  {row['IMPACTO']}")

# =========================
# FOOTER
# =========================
st.caption(f"v11.0 | FLOW={flow:.3f} | HHI={hhi:.2f}")

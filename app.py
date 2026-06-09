import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# =========================
# CONFIGURAÇÃO
# =========================
st.set_page_config(page_title="MACA-QUANTI v14.0", layout="wide")

st.markdown(
    "<h2 style='text-align:center;'>MACA-QUANTI | MESA INSTITUCIONAL</h2>",
    unsafe_allow_html=True
)

# =========================
# UNIVERSO (PORTUGUÊS TOTAL)
# =========================
ativos = {
    "FIXA11.SA": {"nome": "JUROS LONGOS", "grupo": "JUROS", "corr": -1},
    "BRL=X":     {"nome": "DÓLAR AMERICANO", "grupo": "CÂMBIO", "corr": -1},
    "FIND11.SA": {"nome": "SETOR FINANCEIRO", "grupo": "AÇÕES", "corr": 1},
    "EWZ":       {"nome": "BOLSA BRASIL", "grupo": "AÇÕES", "corr": 1},
    "ES=F":      {"nome": "BOLSA ESTADOS UNIDOS", "grupo": "AÇÕES", "corr": 1},
    "NQ=F":      {"nome": "TECNOLOGIA ESTADOS UNIDOS", "grupo": "AÇÕES", "corr": 1},
    "^VIX":      {"nome": "VOLATILIDADE DO MERCADO", "grupo": "RISCO", "corr": -1},
}

# =========================
# MOTOR
# =========================
@st.cache_data(ttl=60)
def motor():
    linhas = []

    for codigo, info in ativos.items():
        df = yf.download(codigo, period="60d", interval="1d", progress=False)
        if df.empty:
            continue

        serie = df["Close"]
        if isinstance(serie, pd.DataFrame):
            serie = serie.iloc[:, 0]

        media = serie.rolling(20).mean().iloc[-1]
        desvio = serie.rolling(20).std().iloc[-1]

        z = (serie.iloc[-1] - media) / max(desvio, 1e-9)
        impacto = np.tanh(z) * info["corr"]

        linhas.append({
            "Ativo": info["nome"],
            "Grupo": info["grupo"],
            "Impacto": impacto
        })

    return pd.DataFrame(linhas)

df = motor()
if df.empty:
    st.stop()

# =========================
# MÉTRICAS CENTRAIS
# =========================
df["Peso"] = df["Impacto"].abs() / (df["Impacto"].abs().sum() + 1e-9)

fluxo = (df["Impacto"] * df["Peso"]).sum()
concentracao = np.sum(df["Peso"] ** 2)

lider = df.loc[df["Impacto"].abs().idxmax(), "Ativo"]

vol = df[df["Ativo"] == "VOLATILIDADE DO MERCADO"]["Impacto"].values
vol = vol[0] if len(vol) else 0

# =========================
# REGIME DE MERCADO
# =========================
if vol > 0.6:
    regime = "ESTRESSE DE MERCADO"
elif fluxo > 0.2:
    regime = "TENDÊNCIA DE ALTA"
elif fluxo < -0.2:
    regime = "TENDÊNCIA DE BAIXA"
elif abs(fluxo) < 0.1:
    regime = "MERCADO SEM DIREÇÃO"
elif concentracao > 0.45:
    regime = "MERCADO CONCENTRADO"
else:
    regime = "MERCADO DIRECIONAL MODERADO"

# =========================
# CABEÇALHO
# =========================
c1, c2, c3, c4 = st.columns(4)

c1.metric("REGIME", regime)
c2.metric("LÍDER", lider)
c3.metric("FLUXO", f"{fluxo:.3f}")
c4.metric("CONCENTRAÇÃO", f"{concentracao:.2f}")

st.divider()

# =========================
# TABELA PRINCIPAL
# =========================
st.markdown("### FLUXO DO MERCADO")

tabela = df.sort_values("Impacto", ascending=False).copy()

def formatar(x):
    sinal = "POSITIVO" if x > 0 else "NEGATIVO"
    return f"{sinal} | {x:.3f}"

tabela["FORÇA"] = tabela["Impacto"].apply(formatar)

st.dataframe(
    tabela[["Grupo", "Ativo", "FORÇA"]],
    use_container_width=True,
    hide_index=True
)

st.divider()

# =========================
# LEITURA RÁPIDA
# =========================
st.markdown("### LEITURA OPERACIONAL")

for _, r in tabela.iterrows():
    if r["Impacto"] > 0:
        st.write(f"POSITIVO → {r['Ativo']} ({r['Grupo']}) {r['Impacto']:.3f}")
    else:
        st.write(f"NEGATIVO → {r['Ativo']} ({r['Grupo']}) {r['Impacto']:.3f}")

# =========================
# LEGENDA
# =========================
st.divider()

st.info("""
LEGENDA DO SISTEMA

FLUXO:
- positivo = pressão de alta no mercado
- negativo = pressão de baixa no mercado

CONCENTRAÇÃO:
- baixo valor = mercado distribuído
- alto valor = mercado dependente de poucos ativos

VOLATILIDADE:
- alta = instabilidade e risco elevado
- baixa = ambiente controlado
""")

# =========================
# FINAL
# =========================
st.caption(f"v14.0 | fluxo={fluxo:.3f} | concentração={concentracao:.2f}")

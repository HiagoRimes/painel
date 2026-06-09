import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Configuração de Layout
st.set_page_config(page_title="MACA-QUANTI ELITE v9.4", layout="wide")
st.title("🏛️ MACA-QUANTI ELITE v9.4 | Motor Institucional")

vies_ativos = {
    "FIXA11.SA": {"nome": "JUROS", "corr": -1.0, "peso": 1.2},
    "BRL=X":     {"nome": "DÓLAR", "corr": -1.0, "peso": 1.2},
    "FIND11.SA": {"nome": "IFNC",  "corr": 1.0,  "peso": 0.8},
    "EWZ":       {"nome": "EWZ",   "corr": 1.0,  "peso": 0.8},
    "ES=F":      {"nome": "S&P500", "corr": 1.0, "peso": 0.6},
    "^VIX":      {"nome": "VIX",   "corr": -1.0, "peso": 0.5},
    "NQ=F":      {"nome": "NASDAQ", "corr": 1.0, "peso": 0.4},
}

@st.cache_data(ttl=60)
def get_motor_profissional():
    res = []
    for cod, cfg in vies_ativos.items():
        try:
            df_y = yf.download(cod, period="60d", interval="1d", progress=False)
            if df_y is None or df_y.empty:
                continue

            c = df_y["Close"]
            if isinstance(c, pd.DataFrame):
                c = c.iloc[:, -1]

            z = (c.iloc[-1] - c.rolling(20).mean().iloc[-1]) / max(c.rolling(20).std().iloc[-1], 1e-9)
            score = np.tanh(z * 0.5) * 100

            res.append({
                "Ativo": cfg["nome"],
                "Impacto": score * cfg["corr"] * cfg["peso"]
            })

        except Exception:
            continue

    return pd.DataFrame(res)

df = get_motor_profissional()
if df.empty:
    st.stop()

# =========================
# 1. DOMINÂNCIA
# =========================
df["Abs_Impacto"] = df["Impacto"].abs()

total_abs = df["Abs_Impacto"].sum() + 1e-9
hhi_sum = np.sum((df["Abs_Impacto"] / total_abs) ** 2)

qualidade_regime = 1 - hhi_sum

# =========================
# 2. FORÇA TOTAL
# =========================
raw_forca = df["Impacto"].sum() / (total_abs + 1e-9)
forca_total = np.tanh(raw_forca)

intensidade_regime = abs(forca_total) * (1 - hhi_sum)

# =========================
# 3. DRIVER
# =========================
driver_lider = df.sort_values("Impacto", ascending=False).iloc[0]["Ativo"]

# =========================
# 4. CONFLITO MACRO
# =========================
vix_score = df.loc[df["Ativo"] == "VIX", "Impacto"].values[0] if "VIX" in df["Ativo"].values else 0
spx_score = df.loc[df["Ativo"] == "S&P500", "Impacto"].values[0] if "S&P500" in df["Ativo"].values else 0

tem_conflito = (
    vix_score > 10 and abs(spx_score) < 5
)

# =========================
# 5. REGIME
# =========================
if tem_conflito:
    regime = "🚨 Conflito Macro"
elif vix_score > 15 and spx_score < 0:
    regime = "Risk-Off Global"
elif hhi_sum > 0.4:
    regime = "Dominância Concentrada"
elif hhi_sum < 0.25:
    regime = "Compressão / Dispersão"
elif forca_total > 0.3:
    regime = "Risk-On"
else:
    regime = "Neutro Estrutural"

# =========================
# 6. CONSENSO
# =========================
consenso = 1 - hhi_sum if forca_total > 0 else hhi_sum

# =========================
# UI
# =========================
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Regime", regime)
col2.metric("Driver", driver_lider)
col3.metric("Concentração", f"{hhi_sum:.2f}")
col4.metric("Qualidade", f"{qualidade_regime:.2f}")
col5.metric("Intensidade", f"{intensidade_regime:.2f}")
col5.metric("Consenso", f"{consenso:.2f}")

st.divider()

col_left, col_right = st.columns([1, 2])

with col_left:
    st.subheader("Bússola WIN")

    if forca_total > 0.2:
        st.success(f"### 🟢 COMPRA ({forca_total:.2f})")
    elif forca_total < -0.2:
        st.error(f"### 🔴 VENDA ({abs(forca_total):.2f})")
    else:
        st.warning("### ⚠️ NEUTRO")

with col_right:
    st.subheader("Mapa de Calor Institucional")

    def formatar_tabela(data):
        return data.style.map(
            lambda x: "background-color: #ffcccc; color: #cc0000; font-weight: bold"
            if x < 0 else "background-color: #ccffcc; color: #006600; font-weight: bold",
            subset=["Impacto"]
        )

    st.dataframe(
        formatar_tabela(df[["Ativo", "Impacto"]].sort_values("Impacto", ascending=False)),
        use_container_width=True,
        hide_index=True
    )

with st.expander("📖 Legenda Institucional"):
    st.markdown("""
    * **Regime**: Risk-On, Risk-Off, Conflito Macro, Compressão, Dominância Concentrada.
    * **HHI**: mede concentração de fluxo institucional.
    * **Qualidade**: dispersão saudável do mercado.
    * **Intensidade**: força direcional ajustada pela concentração.
    * **Consenso**: alinhamento entre drivers.
    """)

st.caption(
    f"v9.4 | Qualidade: {qualidade_regime:.2f} | Intensidade: {intensidade_regime:.2f} | Consenso: {consenso:.2f} | HHI: {hhi_sum:.2f}"
)

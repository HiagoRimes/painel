import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="MACA-QUANTI ELITE v8.9", layout="centered")
st.title("🏛️ MACA-QUANTI ELITE v8.9")

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
            if df_y is None or df_y.empty: continue
            c = df_y['Close']
            if isinstance(c, pd.DataFrame): c = c.iloc[:, -1]
            z = (c.iloc[-1] - c.rolling(20).mean().iloc[-1]) / max(c.rolling(20).std().iloc[-1], 0.0001)
            score = np.tanh(z * 0.5) * 100
            res.append({"Ativo": cfg['nome'], "Impacto": score * cfg['corr'] * cfg['peso']})
        except Exception: continue
    return pd.DataFrame(res) if res else pd.DataFrame(columns=["Ativo", "Impacto"])

df = get_motor_profissional()
if df.empty: st.stop()

# 1. HHI (Concentração de fluxo)
df["Abs_Impacto"] = df["Impacto"].abs()
hhi = (df["Abs_Impacto"] / (df["Abs_Impacto"].sum() + 1e-9)) ** 2
hhi_sum = hhi.sum()

# 2. Força Total Normalizada
forca_total = df['Impacto'].sum() / (df["Abs_Impacto"].sum() + 1e-9)

# 3. Driver Líder
driver_lider = df.loc[df["Abs_Impacto"].idxmax(), "Ativo"]

# 4. Regime
vix_score = df.loc[df["Ativo"] == "VIX", "Impacto"].values[0] if "VIX" in df["Ativo"].values else 0
if vix_score > 10 and forca_total < 0:
    regime = "Risk-Off"
elif hhi_sum < 0.25:
    regime = "Compressão"
elif forca_total > 0:
    regime = "Direcional Altista"
else:
    regime = "Direcional Baixista"

# 5. UI (Bússola + Contexto Institucional)
st.subheader("Bússola Operacional")
col1, col2 = st.columns(2)
col1.metric("Regime", regime)
col2.metric("Driver", driver_lider)

if forca_total > 0: st.success(f"### 🟢 COMPRA | Força: {forca_total:.2f}")
else: st.error(f"### 🔴 VENDA | Força: {abs(forca_total):.2f}")

# Tabela Vertical de Forças
def formatar_tabela(df):
    return df.style.map(
        lambda x: 'background-color: #ffcccc; color: #cc0000; font-weight: bold' if x < 0 else 'background-color: #ccffcc; color: #006600; font-weight: bold', 
        subset=['Impacto']
    )

st.dataframe(
    formatar_tabela(df[['Ativo', 'Impacto']].sort_values('Impacto', ascending=False)),
    use_container_width=True,
    hide_index=True
)

# 6. Rodapé com HHI
st.caption(f"🟢 Verde: alta | 🔴 Vermelho: baixa | HHI: {hhi_sum:.2f}")

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="MACA-QUANTI ELITE v8.7", layout="centered")
st.title("🏛️ MACA-QUANTI ELITE v8.7")

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

forca_total = df['Impacto'].sum() / (df['Impacto'].abs().sum() + 1e-9)

# 1. Bússola
st.subheader("Bússola Operacional")
if forca_total > 0.3: st.success(f"### 🟢 COMPRA | Força Relativa: {forca_total:.2f}")
elif forca_total < -0.3: st.error(f"### 🔴 VENDA | Força Relativa: {abs(forca_total):.2f}")
else: st.warning(f"### ⚠️ NEUTRO | Força Relativa: {forca_total:.2f}")

# 2. Tabela Vertical Colorida (Vermelho/Verde)
st.subheader("Força dos Ativos (Impacto no WIN)")

def formatar_tabela(df):
    # Aplica formatação condicional: Vermelho para < 0, Verde para >= 0
    return df.style.map(
        lambda x: 'background-color: #ffcccc; color: #cc0000; font-weight: bold' if x < 0 else 'background-color: #ccffcc; color: #006600; font-weight: bold', 
        subset=['Impacto']
    )

st.dataframe(
    formatar_tabela(df.sort_values('Impacto', ascending=False)),
    use_container_width=True,
    hide_index=True
)

st.caption("🟢 Verde: Puxa o índice para cima | 🔴 Vermelho: Puxa o índice para baixo.")

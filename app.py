import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="MACA-QUANTI ELITE v8.3", layout="centered")
st.title("🏛️ MACA-QUANTI ELITE v8.3")

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
            res.append({"Ativo": cfg['nome'], "Impacto": score * cfg['corr'] * cfg['peso'], "Score": score})
        except Exception: continue
    return pd.DataFrame(res) if res else pd.DataFrame(columns=["Ativo", "Impacto", "Score"])

df = get_motor_profissional()
if df.empty: st.stop()

# Cálculos
df['Abs_Impacto'] = df['Impacto'].abs()
forca_total = df['Impacto'].sum() / (df['Abs_Impacto'].sum() + 1e-9)
vix = df.loc[df['Ativo']=='VIX', 'Score'].values[0] if 'VIX' in df['Ativo'].values else 0
spx = df.loc[df['Ativo']=='S&P500', 'Score'].values[0] if 'S&P500' in df['Ativo'].values else 0
is_risk_off = (vix > 20) and (spx < 0)
tem_conflito = (df['Impacto'].max() > 0) and (df['Impacto'].min() < 0)

# UI: Camada de Decisão (Foco)
col1, col2 = st.columns(2)
regime = "Risk-Off (Stress)" if is_risk_off else ("Compressão" if tem_conflito else "Direcional")
col1.metric("Regime Atual", regime)
col2.metric("Driver Líder", df.loc[df['Abs_Impacto'].idxmax(), 'Ativo'])

if forca_total > 0.3: st.success(f"### 🟢 COMPRA | Força: {forca_total:.2f}")
elif forca_total < -0.3: st.error(f"### 🔴 VENDA | Força: {abs(forca_total):.2f}")
else: st.warning(f"### ⚠️ NEUTRO | Força: {forca_total:.2f}")

# UI: Camada de Diagnóstico (O "Não estar cego")
with st.expander("🔍 Diagnóstico Macro Detalhado (Por que esta decisão?)"):
    st.write("Visualização de forças individuais (Quanto cada driver puxa o WIN):")
    st.bar_chart(df.set_index('Ativo')['Impacto'])
    st.table(df[['Ativo', 'Score']].sort_values('Score', ascending=False))
    st.caption("Score > 0 favorece alta do WIN | Score < 0 favorece baixa do WIN")

st.info("Atenção: Use a bússola para o sinal e o diagnóstico para a confirmação.")

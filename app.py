import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="MACA-QUANTI ELITE v8.5", layout="wide")
st.title("🏛️ MACA-QUANTI ELITE v8.5")

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

# 1. BLOCO: Bússola de Decisão (O veredito)
st.subheader("Bússola Operacional")
if forca_total > 0.3: st.success(f"### 🟢 COMPRA | Força: {forca_total:.2f}")
elif forca_total < -0.3: st.error(f"### 🔴 VENDA | Força: {abs(forca_total):.2f}")
else: st.warning(f"### ⚠️ NEUTRO | Força: {forca_total:.2f}")

# 2. BLOCO: Diagnóstico (Status do Regime)
st.subheader("Diagnóstico Macro")
c1, c2, c3 = st.columns(3)
regime = "Risk-Off (Stress)" if is_risk_off else ("Compressão" if tem_conflito else "Direcional")
c1.metric("Regime", regime)
c2.metric("Driver Líder", df.loc[df['Abs_Impacto'].idxmax(), 'Ativo'])
c3.metric("Conflito Macro", "Sim" if tem_conflito else "Não")

# 3. BLOCO: Mapa de Forças (O detalhe que faltava)
st.subheader("Mapa de Forças por Ativo")
st.bar_chart(df.set_index('Ativo')['Impacto'])

# 4. BLOCO: Tabela de Dados (Para você nunca ficar cego)
st.subheader("Dados Brutos (Validação)")
st.table(df[['Ativo', 'Impacto', 'Score']].sort_values('Impacto'))

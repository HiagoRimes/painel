import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(page_title="MACA-QUANTI ELITE v6.1", layout="centered")
st.title("🍎 MACA-QUANTI ELITE v6.1")

if 'historico_lideranca' not in st.session_state: st.session_state.historico_lideranca = []

vies_ativos = {
    "FIXA11.SA": {"nome": "JUROS LONGOS", "corr": -1.0, "peso": 1.0, "grupo": "JUROS"},
    "BRL=X":     {"nome": "DÓLAR",        "corr": -1.0, "peso": 0.9, "grupo": "DÓLAR"},
    "FIND11.SA": {"nome": "IFNC",         "corr":  1.0, "peso": 0.8, "grupo": "FLUXO INTERNO"},
    "EWZ":       {"nome": "EWZ",          "corr":  1.0, "peso": 0.7, "grupo": "FLUXO INTERNO"},
    "ES=F":      {"nome": "S&P500",       "corr":  1.0, "peso": 0.6, "grupo": "EXTERIOR"},
    "^VIX":      {"nome": "VIX",          "corr": -1.0, "peso": 0.5, "grupo": "EXTERIOR"},
    "NQ=F":      {"nome": "NASDAQ",       "corr":  1.0, "peso": 0.4, "grupo": "EXTERIOR"},
}

def get_stats(cod):
    df = yf.download(cod, period="60d", interval="1d", progress=False)
    if df.empty: return 0, 0
    c = pd.to_numeric(df['Close'].iloc[:, 0], errors='coerce').dropna()
    z = (c.iloc[-1] - c.rolling(20).mean().iloc[-1]) / max(c.rolling(20).std().iloc[-1], 0.0001)
    conv = np.clip((c.pct_change().rolling(5).std().iloc[-1] / max(c.pct_change().rolling(30).std().iloc[-1], 0.0001)) * 50, 10, 95)
    return z, conv

dados = []
for cod, cfg in vies_ativos.items():
    z, conv = get_stats(cod)
    score = 100 * np.tanh(z * cfg['corr'] * 0.5)
    dom = abs(z) * cfg['peso'] * (conv / 100)
    # Mantive todos os ativos, mas destaquei visualmente os neutros
    dados.append({"Ativo": cfg['nome'], "Grupo": cfg['grupo'], "Dominancia": dom, "Score": score})

df = pd.DataFrame(dados)
df['Pct_Dominancia'] = (df['Dominancia'] / df['Dominancia'].sum()) * 100

# 1. Consenso por Grupo (Exibindo tudo)
st.subheader("🌐 Consenso por Grupos")
df_macro = df.groupby("Grupo").agg({"Dominancia": "sum", "Score": "mean"})
st.dataframe(df_macro.style.format({"Dominancia": "{:.2f}", "Score": "{:.0f}"}))

# 2. Regime de Mercado (Mantido)
hhi = (df['Pct_Dominancia'] / 100).pow(2).sum() * 10000
alinh = np.average(df['Score'], weights=df['Dominancia'] * (abs(df['Score']) / 100 + 0.1))
regime = "🚀 Direcional" if (hhi > 2500 and abs(alinh) > 30) else ("↔️ Lateral" if (hhi < 1500 and abs(alinh) < 20) else "⚠️ Instável")
st.metric("Regime de Mercado", regime)

# 3. Driver Atual (Exibindo mesmo se o peso for baixo)
driver = df.sort_values("Dominancia", ascending=False).iloc[0]
classif = "Dominante" if driver['Pct_Dominancia'] > 50 else ("Forte" if driver['Pct_Dominancia'] > 35 else ("Relevante" if driver['Pct_Dominancia'] > 20 else "Fraco"))
st.metric(f"LÍDER: {driver['Ativo']} ({classif})", f"{driver['Pct_Dominancia']:.0f}%")

# 4. Histórico (Mantido)
if not st.session_state.historico_lideranca or st.session_state.historico_lideranca[-1]['Ativo'] != driver['Ativo']:
    st.session_state.historico_lideranca.append({'Hora': datetime.now().strftime("%H:%M"), 'Ativo': driver['Ativo'], 'Peso': driver['Pct_Dominancia']})

with st.expander("🕒 Histórico"):
    for log in reversed(st.session_state.historico_lideranca[-5:]):
        st.text(f"{log['Hora']} → {log['Ativo']} ({log['Peso']:.0f}%)")

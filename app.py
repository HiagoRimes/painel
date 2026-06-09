import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Configuração
st.set_page_config(page_title="MACA-QUANTI ELITE v4.0", layout="centered")
st.title("🍎 MACA-QUANTI ELITE v4.0")

vies_ativos = {
    "FIXA11.SA": {"nome": "DI FUTURO", "corr": -1.0, "peso": 1.0, "grupo": "JUROS"},
    "BRL=X":     {"nome": "DÓLAR",     "corr": -1.0, "peso": 0.9, "grupo": "DÓLAR"},
    "FIND11.SA": {"nome": "IFNC",      "corr":  1.0, "peso": 0.8, "grupo": "FLUXO INTERNO"},
    "EWZ":       {"nome": "EWZ",       "corr":  1.0, "peso": 0.7, "grupo": "FLUXO INTERNO"},
    "ES=F":      {"nome": "S&P500",    "corr":  1.0, "peso": 0.6, "grupo": "EXTERIOR"},
    "^VIX":      {"nome": "VIX",       "corr": -1.0, "peso": 0.5, "grupo": "EXTERIOR"},
    "NQ=F":      {"nome": "NASDAQ",    "corr":  1.0, "peso": 0.4, "grupo": "EXTERIOR"},
}

def get_stats(cod):
    df = yf.download(cod, period="60d", interval="1d", progress=False)
    if df.empty: return 0, 0, 0
    c = pd.to_numeric(df['Close'].iloc[:, 0], errors='coerce').dropna()
    ma20 = c.rolling(20).mean().iloc[-1]
    std20 = max(c.rolling(20).std().iloc[-1], 0.0001)
    z = (c.iloc[-1] - ma20) / std20
    vol_5d = c.pct_change().rolling(5).std()
    vol_30d = max(c.pct_change().rolling(30).std().iloc[-1], 0.0001)
    vol_rel = vol_5d.iloc[-1] / vol_30d
    persistencia = abs(c.iloc[-1] - c.shift(5).iloc[-1]) / std20
    aceleracao = (c.pct_change(1).iloc[-1]) / (c.pct_change(10).rolling(10).mean().iloc[-1] + 0.0001)
    conviccao = np.clip(((vol_rel * 0.3) + (persistencia * 0.4) + (abs(aceleracao) * 0.3)) * 100, 10, 95)
    ret5d = abs(c.pct_change(5).iloc[-1])
    return z, conviccao, ret5d

# Processamento
dados = []
for cod, cfg in vies_ativos.items():
    z, conv, r5 = get_stats(cod)
    score = 100 * np.tanh(z * cfg['corr'] * 0.5)
    dom = abs(z) * cfg['peso'] * (conv / 100) * (1 + r5)
    dados.append({"Ativo": cfg['nome'], "Grupo": cfg['grupo'], "Dominancia": dom, "Score": score, "Corr": cfg['corr']})

df = pd.DataFrame(dados)
df['Pct_Dominancia'] = (df['Dominancia'] / df['Dominancia'].sum()) * 100

# 1. Painel Macro com HHI (Concentração)
st.subheader("🌐 Forças Macro")
df_macro = df.groupby("Grupo").agg({"Dominancia": "sum", "Score": lambda x: np.average(x, weights=df.loc[x.index, 'Dominancia'])}).reset_index()
df_macro['Pct_Dominancia'] = (df_macro['Dominancia'] / df_macro['Dominancia'].sum()) * 100

# Cálculo HHI
hhi = (df['Pct_Dominancia'] / 100).pow(2).sum() * 10000
frag_hhi = (1 - (hhi/10000)) * 100

st.metric("DOMINÂNCIA MACRO 🎯", df_macro.sort_values("Dominancia", ascending=False).iloc[0]['Grupo'])
st.write(f"**Índice de Fragmentação (HHI):** {frag_hhi:.1f} | {'Concentrado' if hhi > 2500 else 'Disperso'}")

# 2. Painel de Consenso
st.subheader("⚖️ Consenso de Mercado")
c_alta = len(df[df['Score'] > 0])
c_baixa = len(df[df['Score'] < 0])
col_c1, col_c2 = st.columns(2)
col_c1.metric("Pressionando ALTA", c_alta)
col_c2.metric("Pressionando BAIXA", c_baixa)

# 3. Hierarquia e Mudança de Liderança
st.write("---")
st.subheader("🎯 Hierarquia de Drivers")
top_driver = df.sort_values("Dominancia", ascending=False).iloc[0]['Ativo']
st.write(f"**Driver Atual:** {top_driver}")

# 4. Alinhamento Ponderado
alinh = np.average(df['Score'], weights=df['Dominancia'])
st.write(f"### **📊 ALINHAMENTO: {abs(alinh):.1f}%**")
st.progress(min(abs(alinh) / 100, 1))

# 5. Tabela Detalhada
st.dataframe(df[['Ativo', 'Pct_Dominancia', 'Score']].style.format({"Pct_Dominancia": "{:.1f}%", "Score": "{:.0f}"}), hide_index=True)

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# Configuração
st.set_page_config(page_title="MACA-QUANTI ELITE v5.0", layout="centered")
st.title("🍎 MACA-QUANTI ELITE v5.0")

# Inicialização de memória para o Histórico de Liderança
if 'historico_lideranca' not in st.session_state:
    st.session_state.historico_lideranca = []

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
    ma20 = c.rolling(20).mean().iloc[-1]
    std20 = max(c.rolling(20).std().iloc[-1], 0.0001)
    z = (c.iloc[-1] - ma20) / std20
    vol_5d = c.pct_change().rolling(5).std()
    vol_30d = max(c.pct_change().rolling(30).std().iloc[-1], 0.0001)
    vol_rel = vol_5d.iloc[-1] / vol_30d
    persistencia = abs(c.iloc[-1] - c.shift(5).iloc[-1]) / std20
    aceleracao = (c.pct_change(1).iloc[-1]) / (c.pct_change(10).rolling(10).mean().iloc[-1] + 0.0001)
    conviccao = np.clip(((vol_rel * 0.3) + (persistencia * 0.4) + (abs(aceleracao) * 0.3)) * 100, 10, 95)
    return z, conviccao

# Processamento
dados = []
for cod, cfg in vies_ativos.items():
    z, conv = get_stats(cod)
    score = 100 * np.tanh(z * cfg['corr'] * 0.5)
    # Fórmula simplificada (Opção A)
    dom = abs(z) * cfg['peso'] * (conv / 100)
    dados.append({"Ativo": cfg['nome'], "Grupo": cfg['grupo'], "Dominancia": dom, "Score": score, "Corr": cfg['corr']})

df = pd.DataFrame(dados)
df['Pct_Dominancia'] = (df['Dominancia'] / df['Dominancia'].sum()) * 100

# 1. Painel Macro
st.subheader("🌐 Forças Macro")
df_macro = df.groupby("Grupo").agg({"Dominancia": "sum", "Score": lambda x: np.average(x, weights=df.loc[x.index, 'Dominancia'])}).reset_index()
df_macro['Pct_Dominancia

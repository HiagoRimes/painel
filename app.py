import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="MACA-QUANTI ELITE", layout="centered")
st.title("🍎 MACA-QUANTI ELITE")

# 1. Definição de Ativos
vies_ativos = {
    "FIXA11.SA": {"nome": "DI FUTURO", "corr": -1.0, "peso": 1.0},
    "BRL=X":     {"nome": "DÓLAR",     "corr": -1.0, "peso": 0.9},
    "FIND11.SA": {"nome": "IFNC",      "corr":  1.0, "peso": 0.8},
    "EWZ":       {"nome": "EWZ",       "corr":  1.0, "peso": 0.7},
}

# 2. Gráfico de Segurança (Não trava o app se falhar)
st.subheader("📊 Gráfico WIN (5min)")
try:
    df_win = yf.download("WIN=F", period="1d", interval="5m", progress=False)
    if not df_win.empty:
        st.line_chart(df_win['Close'])
    else:
        st.warning("Gráfico indisponível no momento.")
except Exception:
    st.error("Erro ao carregar gráfico WIN.")

# 3. Processamento dos Dados (Reutilizando a lógica anterior)
def get_stats(cod):
    df = yf.download(cod, period="30d", interval="1d", progress=False)
    if df.empty: return 0, 0
    c = df['Close'].iloc[:, 0] if isinstance(df['Close'], pd.DataFrame) else df['Close']
    c = pd.to_numeric(c, errors='coerce').dropna()
    z = (float(c.iloc[-1]) - float(c.rolling(20).mean().iloc[-1])) / float(c.rolling(20).std().iloc[-1])
    vol = float(c.pct_change().std())
    return z, vol

dados = []
for cod, cfg in vies_ativos.items():
    z, vol = get_stats(cod)
    conviccao = np.clip(vol * 1500, 10, 95)
    score_win = np.clip(z * cfg['corr'] * 33, -100, 100)
    dominancia = abs(z) * cfg['peso'] * (conviccao / 100)
    dados.append({"Ativo": cfg['nome'], "Dominancia": dominancia, "Conviccao": conviccao, "Score": score_win, "Corr": cfg['corr']})

# [ ... Restante do código de exibição da tabela e legendas ... ]

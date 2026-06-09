import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="MACA-QUANTI ELITE", layout="centered")
st.title("🍎 MACA-QUANTI ELITE")

# 1. Ativos (Adicione ou remova conforme sua necessidade)
vies_ativos = {
    "WIN=F":     {"nome": "WIN FUTURO", "corr":  1.0, "peso": 1.0}, # Adicionado para monitorar
    "FIXA11.SA": {"nome": "DI FUTURO", "corr": -1.0, "peso": 1.0},
    "BRL=X":     {"nome": "DÓLAR",     "corr": -1.0, "peso": 0.9},
    "FIND11.SA": {"nome": "IFNC",      "corr":  1.0, "peso": 0.8},
    "EWZ":       {"nome": "EWZ",       "corr":  1.0, "peso": 0.7},
}

# [ ... Mantenha as funções de processamento iguais ... ]

# 2. Exibição do Gráfico de 5min (INTRA-DIA)
st.subheader("📊 Gráfico WIN (5min)")
df_win = yf.download("WIN=F", period="1d", interval="5m", progress=False)
st.line_chart(df_win['Close'])

# [ ... Restante do seu código de Hierarquia e Leitura ... ]

# 3. Legendas ao final (Conforme solicitado)
st.write("---")
# ... (Seus Expanders de Legenda aqui)

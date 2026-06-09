import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="MACA-QUANTI ELITE v5.1", layout="centered")
st.title("🍎 MACA-QUANTI ELITE v5.1")

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
    sentido = "🟢 ALTA" if score > 0 else "🔴 BAIXA"
    dom = abs(z) * cfg['peso'] * (conv / 100)
    dados.append({"Ativo": cfg['nome'], "Grupo": cfg['grupo'], "Dominancia": dom, "Score": score, "Corr": cfg['corr'], "Sentido": sentido, "Conviccao": conv})

df = pd.DataFrame(dados)
df['Pct_Dominancia'] = (df['Dominancia'] / df['Dominancia'].sum()) * 100

# 1. Painel Macro
st.subheader("🌐 Forças Macro")
df_macro = df.groupby("Grupo").agg(
    Dominancia=('Dominancia', 'sum'),
    Score=('Score', lambda x: np.average(x, weights=df.loc[x.index, 'Dominancia']))
).reset_index()
df_macro['Pct_Dominancia'] = (df_macro['Dominancia'] / df_macro['Dominancia'].sum()) * 100
df_macro = df_macro.sort_values("Dominancia", ascending=False)

# Driver Atual
driver_atual = df.sort_values("Dominancia", ascending=False).iloc[0]
st.metric(f"DRIVER ATUAL: {driver_atual['Ativo']} ({driver_atual['Sentido']})", f"{driver_atual['Pct_Dominancia']:.0f}%")
st.dataframe(df_macro.style.format({"Pct_Dominancia": "{:.1f}%", "Score": "{:.0f}"}), hide_index=True)

# 2. HHI e Consenso
hhi = (df['Pct_Dominancia'] / 100).pow(2).sum() * 10000
status_hhi = "Muito Disperso" if hhi < 1500 else ("Equilibrado" if hhi < 2500 else ("Concentrado" if hhi < 4000 else "Dominância Extrema"))
f_alta = df[df['Score'] > 0]['Dominancia'].sum()
f_baixa = df[df['Score'] < 0]['Dominancia'].sum()
total_f = f_alta + f_baixa
pct_alta = 100 * f_alta / total_f if total_f > 0 else 50

st.subheader("⚖️ Consenso & Estrutura")
col1, col2 = st.columns(2)
col1.metric("Consenso ALTA (Ponderado)", f"{pct_alta:.0f}%")
col2.write(f"**Estrutura (HHI):** {status_hhi}")

# 3. Histórico de Liderança
if not st.session_state.historico_lideranca or st.session_state.historico_lideranca[-1]['Ativo'] != driver_atual['Ativo']:
    st.session_state.historico_lideranca.append({'Hora': datetime.now().strftime("%H:%M"), 'Ativo': driver_atual['Ativo']})

with st.expander("🕒 Histórico de Troca de Drivers"):
    for log in reversed(st.session_state.historico_lideranca[-5:]):
        st.text(f"{log['Hora']} → {log['Ativo']}")

# 4. Alinhamento
alinh = np.average(df['Score'], weights=df['Dominancia'])
st.write(f"### **📊 ALINHAMENTO: {abs(alinh):.1f}%**")
st.progress(min(abs(alinh) / 100, 1))

# 5. Tabela Detalhada (Preservando todas as colunas anteriores)
st.dataframe(df[['Ativo', 'Grupo', 'Pct_Dominancia', 'Conviccao', 'Sentido', 'Score']].rename(columns={'Pct_Dominancia': 'Dom %'}).style.format({"Dom %": "{:.1f}%", "Conviccao": "{:.0f}", "Score": "{:.0f}"}), hide_index=True)

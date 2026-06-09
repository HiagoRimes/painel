import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Configuração
st.set_page_config(page_title="MACA-QUANTI ELITE v3", layout="centered")
st.title("🍎 MACA-QUANTI ELITE v3")

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
    c = df['Close'].iloc[:, 0]
    c = pd.to_numeric(c, errors='coerce').dropna()
    
    ma20 = c.rolling(20).mean()
    std20 = c.rolling(20).std()
    z = (c.iloc[-1] - ma20.iloc[-1]) / std20.iloc[-1]
    
    vol_5d = c.pct_change().rolling(5).std()
    vol_30d = c.pct_change().rolling(30).std()
    vol_rel = vol_5d.iloc[-1] / vol_30d.iloc[-1]
    persistencia = abs(c.iloc[-1] - c.shift(5).iloc[-1]) / std20.iloc[-1]
    
    conviccao = np.clip(((vol_rel * 0.4) + (persistencia * 0.6)) * 100, 10, 95)
    retorno_5d = abs(c.pct_change(5).iloc[-1])
    
    return z, conviccao, retorno_5d

dados = []
for cod, cfg in vies_ativos.items():
    z, conviccao, ret5d = get_stats(cod)
    score_win = 100 * np.tanh(z * cfg['corr'] * 0.5)
    # Dominância ajustada pelo retorno percentual (Deslocamento Real)
    dominancia = abs(z) * cfg['peso'] * (conviccao / 100) * (1 + ret5d)
    dados.append({"Ativo": cfg['nome'], "Grupo": cfg['grupo'], "Dominancia": dominancia, 
                  "Conviccao": conviccao, "Score": score_win, "Corr": cfg['corr']})

df = pd.DataFrame(dados)
df['Pct_Dominancia'] = (df['Dominancia'] / df['Dominancia'].sum()) * 100

# 1. Painel Macro
st.subheader("🌐 Forças Macro")
df_macro = df.groupby("Grupo").agg({"Dominancia": "sum", "Score": "mean"}).reset_index()
df_macro['Pct_Dominancia'] = (df_macro['Dominancia'] / df_macro['Dominancia'].sum()) * 100
df_macro = df_macro.sort_values("Dominancia", ascending=False)
driver_macro = df_macro.iloc[0]['Grupo']
st.metric("DOMINÂNCIA MACRO", driver_macro)
st.dataframe(df_macro[['Grupo', 'Pct_Dominancia', 'Score']].style.format({"Pct_Dominancia": "{:.1f}%", "Score": "{:.0f}"}), hide_index=True, use_container_width=True)

# 2. Hierarquia e Alinhamento Ponderado
st.subheader("🎯 Hierarquia de Drivers")
alinh = np.average(df['Score'], weights=df['Dominancia'])
msg_sentido = "🟢 Tendência de Alta" if alinh > 10 else ("🔴 Tendência de Baixa" if alinh < -10 else "🟡 Lateralização")

st.write(f"### **ALINHAMENTO PONDERADO: {abs(alinh):.1f}%**")
st.write(f"Sentido: {msg_sentido}")
st.progress(min(abs(alinh) / 100, 1))

# 3. Quebras de Correlação
quebras = df[df.apply(lambda x: x['Score'] * x['Corr'] < -50, axis=1)]
if not quebras.empty:
    st.error(f"⚠️ QUEBRAS DE CORRELAÇÃO: {', '.join(quebras['Ativo'].tolist())}")

# 4. Tabela Detalhada
df['Status'] = df.apply(lambda x: "🟢 Conf" if x['Score'] * x['Corr'] > 0 else ("🔴 Quebra" if x['Score'] * x['Corr'] < -50 else "🟡 Div"), axis=1)
tabela_exibicao = df[['Ativo', 'Pct_Dominancia', 'Conviccao', 'Score', 'Status']].rename(columns={'Pct_Dominancia': 'Dom %'})
st.dataframe(tabela_exibicao.style.format({"Dom %": "{:.1f}%", "Conviccao": "{:.0f}", "Score": "{:.0f}"}), hide_index=True, use_container_width=True)
    

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Configuração da página
st.set_page_config(page_title="MACA-QUANTI ELITE v2", layout="centered")
st.title("🍎 MACA-QUANTI ELITE v2")

# 1. Definição dos ativos e seus grupos macro
vies_ativos = {
    "FIXA11.SA": {"nome": "DI FUTURO", "corr": -1.0, "peso": 1.0, "grupo": "JUROS"},
    "BRL=X":     {"nome": "DÓLAR",     "corr": -1.0, "peso": 0.9, "grupo": "DÓLAR"},
    "FIND11.SA": {"nome": "IFNC",      "corr":  1.0, "peso": 0.8, "grupo": "FLUXO INTERNO"},
    "EWZ":       {"nome": "EWZ",       "corr":  1.0, "peso": 0.7, "grupo": "FLUXO INTERNO"},
    "ES=F":      {"nome": "S&P500",    "corr":  1.0, "peso": 0.6, "grupo": "EXTERIOR"},
    "^VIX":      {"nome": "VIX",       "corr": -1.0, "peso": 0.5, "grupo": "EXTERIOR"},
    "NQ=F":      {"nome": "NASDAQ",    "corr":  1.0, "peso": 0.4, "grupo": "EXTERIOR"},
}

# 2. Processamento dos Dados (Lógica de Convicção Robusta)
def get_stats(cod):
    df = yf.download(cod, period="60d", interval="1d", progress=False)
    if df.empty: return 0, 0, 0
    c = df['Close'].iloc[:, 0]
    c = pd.to_numeric(c, errors='coerce').dropna()
    
    # Z-Score
    ma20 = c.rolling(20).mean()
    std20 = c.rolling(20).std()
    z = (c.iloc[-1] - ma20.iloc[-1]) / std20.iloc[-1]
    
    # Convicção: Volatilidade Relativa + Persistência (afastamento da média)
    vol_5d = c.pct_change().rolling(5).std()
    vol_30d = c.pct_change().rolling(30).std()
    vol_rel = vol_5d.iloc[-1] / vol_30d.iloc[-1]
    persistencia = abs(c.iloc[-1] - c.shift(5).iloc[-1]) / std20.iloc[-1]
    
    conviccao = np.clip(((vol_rel * 0.4) + (persistencia * 0.6)) * 100, 10, 95)
    return z, conviccao

dados = []
for cod, cfg in vies_ativos.items():
    z, conviccao = get_stats(cod)
    # Score com normalização suave via tanh
    score_win = 100 * np.tanh(z * cfg['corr'] * 0.5)
    dominancia = abs(z) * cfg['peso'] * (conviccao / 100)
    dados.append({"Ativo": cfg['nome'], "Grupo": cfg['grupo'], "Dominancia": dominancia, 
                  "Conviccao": conviccao, "Score": score_win, "Corr": cfg['corr']})

df = pd.DataFrame(dados)
df['Pct_Dominancia'] = (df['Dominancia'] / df['Dominancia'].sum()) * 100

# 3. Painel Macro
st.subheader("🌐 Forças Macro")
df_macro = df.groupby("Grupo").agg({"Dominancia": "sum", "Score": "mean"}).reset_index()
df_macro['Pct_Dominancia'] = (df_macro['Dominancia'] / df_macro['Dominancia'].sum()) * 100
df_macro = df_macro.sort_values("Dominancia", ascending=False)
st.dataframe(df_macro[['Grupo', 'Pct_Dominancia', 'Score']].style.format({"Pct_Dominancia": "{:.1f}%", "Score": "{:.0f}"}), hide_index=True, use_container_width=True)

st.write("---")

# 4. Hierarquia e Sentido
st.subheader("🎯 Hierarquia de Drivers")
col1, col2 = st.columns(2)
best_drivers = df.sort_values("Dominancia", ascending=False)
col1.metric("Primário", best_drivers.iloc[0]['Ativo'])
col2.metric("Secundário", best_drivers.iloc[1]['Ativo'])

alinh = df['Score'].mean()
msg_sentido = "🟢 Tendência de Alta" if alinh > 10 else ("🔴 Tendência de Baixa" if alinh < -10 else "🟡 Lateralização")

st.write(f"### **ALINHAMENTO GERAL: {abs(alinh):.1f}%**")
st.write(f"Sentido: {msg_sentido}")
st.progress(min(abs(alinh) / 100, 1))

# 5. Tabela Detalhada
df['Status'] = df.apply(lambda x: "🟢 Conf" if x['Score'] * x['Corr'] > 0 else ("🔴 Quebra" if x['Score'] * x['Corr'] < -50 else "🟡 Div"), axis=1)
tabela_exibicao = df[['Ativo', 'Pct_Dominancia', 'Conviccao', 'Score', 'Status']].rename(columns={'Pct_Dominancia': 'Dom %'})

# Estilização básica para o celular
st.dataframe(tabela_exibicao.style.format({"Dom %": "{:.1f}%", "Conviccao": "{:.0f}", "Score": "{:.0f}"}), hide_index=True, use_container_width=True)

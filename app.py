import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Configuração da página
st.set_page_config(page_title="MACA-QUANTI ELITE", layout="centered")
st.title("🍎 MACA-QUANTI ELITE")

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

# 2. Processamento dos Dados
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
    dados.append({"Ativo": cfg['nome'], "Grupo": cfg['grupo'], "Dominancia": dominancia, "Conviccao": conviccao, "Score": score_win, "Corr": cfg['corr']})

df = pd.DataFrame(dados)
df['Pct_Dominancia'] = (df['Dominancia'] / df['Dominancia'].sum()) * 100

# 3. Painel de Forças Macro (Nova Camada)
st.subheader("🌐 Forças Macro")
df_macro = df.groupby("Grupo").agg({"Dominancia": "sum", "Score": "mean"}).reset_index()
df_macro['Pct_Dominancia'] = (df_macro['Dominancia'] / df_macro['Dominancia'].sum()) * 100
df_macro = df_macro.sort_values("Dominancia", ascending=False)
df_macro['Score'] = df_macro['Score'].map('{:.0f}'.format)
df_macro['Pct_Dominancia'] = df_macro['Pct_Dominancia'].map('{:.1f}%'.format)
st.dataframe(df_macro[['Grupo', 'Pct_Dominancia', 'Score']], hide_index=True, use_container_width=True)

st.write("---")

# 4. Hierarquia de Drivers
st.subheader("🎯 Hierarquia de Drivers")
col1, col2 = st.columns(2)
col1.metric("Primário", df.sort_values("Dominancia", ascending=False).iloc[0]['Ativo'])
col2.metric("Secundário", df.sort_values("Dominancia", ascending=False).iloc[1]['Ativo'])

# 5. Alinhamento e Leitura do Momento
alinh = df['Score'].mean()
msg_sentido = "🟢 Tendência de Alta" if alinh > 0 else ("🔴 Tendência de Baixa" if alinh < 0 else "🟡 Lateralização")

st.write(f"### **ALINHAMENTO GERAL: {abs(alinh):.1f}%**")
st.write(f"Sentido: {msg_sentido}")
st.progress(min(abs(alinh) / 100, 1))

st.write("### 📝 Leitura do Momento")
st.success(f"O mercado é conduzido pelo {df.sort_values('Dominancia', ascending=False).iloc[0]['Ativo']}. Sentido: {msg_sentido}.")

# 6. Tabela Detalhada
df['Status'] = df.apply(lambda x: "🟢 Conf" if x['Score'] * x['Corr'] > 0 else ("🔴 Quebra" if x['Score'] * x['Corr'] < -50 else "🟡 Div"), axis=1)
tabela_exibicao = df[['Ativo', 'Pct_Dominancia', 'Conviccao', 'Score', 'Status']].copy()
tabela_exibicao['Pct_Dominancia'] = tabela_exibicao['Pct_Dominancia'].map('{:.1f}%'.format)
tabela_exibicao['Conviccao'] = tabela_exibicao['Conviccao'].map('{:.0f}'.format)
tabela_exibicao['Score'] = tabela_exibicao['Score'].map('{:.0f}'.format)
st.dataframe(tabela_exibicao.rename(columns={'Pct_Dominancia': 'Dom %'}), hide_index=True, use_container_width=True)

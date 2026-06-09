import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Configuração da página
st.set_page_config(page_title="MACA-QUANTI ELITE v3.1", layout="centered")
st.title("🍎 MACA-QUANTI ELITE v3.1")

# 1. Definição dos ativos
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
    # Obtém dados dos últimos 60 dias
    df = yf.download(cod, period="60d", interval="1d", progress=False)
    if df.empty: return 0, 0, 0
    c = pd.to_numeric(df['Close'].iloc[:, 0], errors='coerce').dropna()
    
    # Proteções contra Divisão por Zero
    ma20 = c.rolling(20).mean().iloc[-1]
    std20 = max(c.rolling(20).std().iloc[-1], 0.0001)
    z = (c.iloc[-1] - ma20) / std20
    
    vol_5d = c.pct_change().rolling(5).std()
    vol_30d = max(c.pct_change().rolling(30).std().iloc[-1], 0.0001)
    vol_rel = vol_5d.iloc[-1] / vol_30d
    
    persistencia = abs(c.iloc[-1] - c.shift(5).iloc[-1]) / std20
    # Cálculo de aceleração com proteção
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
    dados.append({"Ativo": cfg['nome'], "Grupo": cfg['grupo'], "Dominancia": dom, "Conviccao": conv, "Score": score, "Corr": cfg['corr']})

df = pd.DataFrame(dados)
df['Pct_Dominancia'] = (df['Dominancia'] / df['Dominancia'].sum()) * 100

# 2. Painel Macro (Ponderado e Corrigido)
st.subheader("🌐 Forças Macro")

def calculate_weighted_avg(df_group):
    return np.average(df_group['Score'], weights=df_group['Dominancia'])

df_macro = df.groupby("Grupo").apply(
    lambda x: pd.Series({
        'Dominancia': x['Dominancia'].sum(),
        'Score': calculate_weighted_avg(x)
    })
).reset_index()

df_macro['Pct_Dominancia'] = (df_macro['Dominancia'] / df_macro['Dominancia'].sum()) * 100
df_macro = df_macro.sort_values("Dominancia", ascending=False)

st.metric("DOMINÂNCIA MACRO", df_macro.iloc[0]['Grupo'])
st.dataframe(df_macro.style.format({"Pct_Dominancia": "{:.1f}%", "Score": "{:.0f}"}), hide_index=True, use_container_width=True)

# 3. Hierarquia e Fragmentação
st.write("---")
st.subheader("🎯 Hierarquia de Drivers")
top_3 = df.sort_values("Dominancia", ascending=False).head(3)
frag = 100 - top_3.iloc[0]['Pct_Dominancia']
st.write(f"**Fragmentação:** {frag:.1f}% | {'Alinhado' if frag < 40 else 'Confuso'}")

cols = st.columns(3)
for i, col in enumerate(cols):
    col.metric(f"{i+1}º {top_3.iloc[i]['Ativo']}", f"{top_3.iloc[i]['Pct_Dominancia']:.0f}%")

# 4. Alinhamento Ponderado
alinh = np.average(df['Score'], weights=df['Dominancia'])
st.write(f"### **ALINHAMENTO PONDERADO: {abs(alinh):.1f}%**")
st.progress(min(abs(alinh) / 100, 1))

# 5. Quebras de Correlação
quebras = df[df.apply(lambda x: x['Score'] * x['Corr'] < -50, axis=1)]
if not quebras.empty:
    st.error(f"⚠️ QUEBRAS: {', '.join(quebras['Ativo'].tolist())}")

# 6. Tabela Detalhada
st.dataframe(df[['Ativo', 'Pct_Dominancia', 'Conviccao', 'Score']].rename(columns={'Pct_Dominancia': 'Dom %'}).style.format({"Dom %": "{:.1f}%", "Conviccao": "{:.0f}", "Score": "{:.0f}"}), hide_index=True, use_container_width=True)

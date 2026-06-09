import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Configuração da página
st.set_page_config(page_title="MACA-QUANTI ELITE", layout="centered")
st.title("🍎 MACA-QUANTI ELITE")

# 1. Definição dos ativos
vies_ativos = {
    "FIXA11.SA": {"nome": "DI FUTURO", "corr": -1.0, "peso": 1.0},
    "BRL=X":     {"nome": "DÓLAR",     "corr": -1.0, "peso": 0.9},
    "FIND11.SA": {"nome": "IFNC",      "corr":  1.0, "peso": 0.8},
    "EWZ":       {"nome": "EWZ",       "corr":  1.0, "peso": 0.7},
    "ES=F":      {"nome": "S&P500",    "corr":  1.0, "peso": 0.6},
    "^VIX":      {"nome": "VIX",       "corr": -1.0, "peso": 0.5},
    "NQ=F":      {"nome": "NASDAQ",    "corr":  1.0, "peso": 0.4},
}

# 2. Gráfico Referência (IBOV - Proxy do Índice)
st.subheader("📊 Gráfico IBOV (Referência)")
try:
    df_chart = yf.download("^BVSP", period="1d", interval="5m", progress=False)
    if not df_chart.empty:
        st.line_chart(df_chart['Close'])
    else:
        st.info("Gráfico IBOV em processamento.")
except:
    st.info("Gráfico IBOV indisponível.")

# 3. Processamento dos Dados
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

df = pd.DataFrame(dados).sort_values("Dominancia", ascending=False)
df['Pct_Dominancia'] = (df['Dominancia'] / df['Dominancia'].sum()) * 100

# 4. Hierarquia e Leitura
st.write("---")
st.subheader("🎯 Hierarquia de Drivers")
col1, col2 = st.columns(2)
col1.metric("Primário", df.iloc[0]['Ativo'])
col2.metric("Secundário", df.iloc[1]['Ativo'])

alinh = df['Score'].mean()
st.write(f"### **ALINHAMENTO GERAL: {abs(alinh):.1f}%**")
st.progress(min(abs(alinh) / 100, 1))

# 5. Tabela Limpa (Sem numeração)
df['Status'] = df.apply(lambda x: "🟢 Conf" if x['Score'] * x['Corr'] > 0 else ("🔴 Quebra" if x['Score'] * x['Corr'] < -50 else "🟡 Div"), axis=1)
tabela_final = df[['Ativo', 'Pct_Dominancia', 'Conviccao', 'Score', 'Status']].rename(columns={'Pct_Dominancia': 'Dom %'})
# O comando hide_index remove a numeração lateral
st.dataframe(tabela_final, hide_index=True, use_container_width=True)

# 6. Rodapé
st.write("---")
with st.expander("📖 Guia de Leitura"):
    st.write("O gráfico acima usa o IBOV como referência estrutural.")
    st.write("Tabela: 🟢 Conf (Ajuda o movimento), 🟡 Div (Cautela), 🔴 Quebra (Possível reversão).")
    

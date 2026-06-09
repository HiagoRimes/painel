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
    dados.append({"Ativo": cfg['nome'], "Dominancia": dominancia, "Conviccao": conviccao, "Score": score_win, "Corr": cfg['corr']})

df = pd.DataFrame(dados).sort_values("Dominancia", ascending=False)
df['Pct_Dominancia'] = (df['Dominancia'] / df['Dominancia'].sum()) * 100

# 3. Hierarquia de Drivers
st.subheader("🎯 Hierarquia de Drivers")
col1, col2 = st.columns(2)
col1.metric("Primário", df.iloc[0]['Ativo'])
col2.metric("Secundário", df.iloc[1]['Ativo'])

# 4. Alinhamento e Leitura do Momento (Mensagens e Emojis)
alinh = df['Score'].mean()

if alinh > 0:
    msg_sentido = "🟢 Tendência de Alta"
elif alinh < 0:
    msg_sentido = "🔴 Tendência de Baixa"
else:
    msg_sentido = "🟡 Lateralização"

st.write(f"### **ALINHAMENTO GERAL: {abs(alinh):.1f}%**")
st.write(f"Sentido: {msg_sentido}")
st.progress(min(abs(alinh) / 100, 1))

st.write("### 📝 Leitura do Momento")
resumo = f"O mercado é conduzido pelo {df.iloc[0]['Ativo']}. A fragmentação é {'Alta' if abs(alinh) < 40 else 'Baixa'}. Sentido: {msg_sentido}."
st.success(resumo)

# 5. Tabela de Scores (Limpa e formatada)
df['Status'] = df.apply(lambda x: "🟢 Conf" if x['Score'] * x['Corr'] > 0 else ("🔴 Quebra" if x['Score'] * x['Corr'] < -50 else "🟡 Div"), axis=1)

tabela_exibicao = df[['Ativo', 'Pct_Dominancia', 'Conviccao', 'Score', 'Status']].copy()
tabela_exibicao['Pct_Dominancia'] = tabela_exibicao['Pct_Dominancia'].map('{:.1f}%'.format)
tabela_exibicao['Conviccao'] = tabela_exibicao['Conviccao'].map('{:.0f}'.format)
tabela_exibicao['Score'] = tabela_exibicao['Score'].map('{:.0f}'.format)
tabela_exibicao = tabela_exibicao.rename(columns={'Pct_Dominancia': 'Dom %'})

st.dataframe(tabela_exibicao, hide_index=True, use_container_width=True)

# 6. Guia de Leitura e Legendas
st.write("---")
st.write("### 📖 Guia de Leitura e Legendas")

with st.expander("📌 Legenda de Status de Correlação"):
    st.info("""
    - **🟢 Conf:** Ativo alinhado com o WIN. Ajuda o movimento.
    - **🟡 Div:** Ativo hesitante. Correlação falhando, cautela.
    - **🔴 Quebra:** O ativo empurra contra a natureza do WIN (Alerta de possível reversão).
    """)

with st.expander("📈 Como ler o nosso gráfico de Dominância"):
    st.write("""
    1. **Driver Primário:** É o ativo que, neste exato momento, detém o maior poder de puxar o preço do Mini Índice (WIN).
    2. **Dominância (%):** Indica o peso real de influência de cada ativo.
    3. **Convicção:** Mede a 'energia' por trás do movimento. Quanto maior, mais provável que o movimento tenha continuidade.
    4. **Score WIN (-100 a +100):** Pressão no índice. Acima de 0 pressiona para a alta, abaixo de 0 pressiona para a queda.
    """)

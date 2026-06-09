import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# 1. Configuração Inicial (Obrigatório vir antes de qualquer comando st.)
st.set_page_config(page_title="MACA-QUANTI ELITE", layout="centered")

st.title("🍎 MACA-QUANTI ELITE")

# 2. Configuração com Pesos Estruturais
vies_ativos = {
    "FIXA11.SA": {"nome": "DI FUTURO", "corr": -1.0, "peso": 1.0},
    "BRL=X":     {"nome": "DÓLAR",     "corr": -1.0, "peso": 0.9},
    "FIND11.SA": {"nome": "IFNC",      "corr":  1.0, "peso": 0.8},
    "EWZ":       {"nome": "EWZ",       "corr":  1.0, "peso": 0.7},
    "ES=F":      {"nome": "S&P500",    "corr":  1.0, "peso": 0.6},
    "^VIX":      {"nome": "VIX",       "corr": -1.0, "peso": 0.5},
    "NQ=F":      {"nome": "NASDAQ",    "corr":  1.0, "peso": 0.4},
}

def get_stats(cod):
    df = yf.download(cod, period="30d", interval="1d", progress=False)
    c = df['Close'].iloc[:, 0] if isinstance(df['Close'], pd.DataFrame) else df['Close']
    c = pd.to_numeric(c, errors='coerce').dropna()
    z = (float(c.iloc[-1]) - float(c.rolling(20).mean().iloc[-1])) / float(c.rolling(20).std().iloc[-1])
    vol = float(c.pct_change().std())
    return z, vol

# 3. Processamento
dados = []
for cod, cfg in vies_ativos.items():
    z, vol = get_stats(cod)
    conviccao = np.clip(vol * 1500, 10, 95)
    score_win = np.clip(z * cfg['corr'] * 33, -100, 100)
    dominancia = abs(z) * cfg['peso'] * (conviccao / 100)
    dados.append({"Ativo": cfg['nome'], "Dominancia": dominancia, "Conviccao": conviccao, "Score": score_win, "Corr": cfg['corr']})

df = pd.DataFrame(dados).sort_values("Dominancia", ascending=False)
df['Pct_Dominancia'] = (df['Dominancia'] / df['Dominancia'].sum()) * 100

# 4. Exibição do Painel
st.subheader("🎯 Hierarquia de Drivers")
col1, col2 = st.columns(2)
col1.metric("Primário", df.iloc[0]['Ativo'])
col2.metric("Secundário", df.iloc[1]['Ativo'])

st.write("---")
alinh = df['Score'].mean()
st.write(f"### **ALINHAMENTO GERAL: {abs(alinh):.1f}%**")
st.write(f"Sentido: {'🟢 Altista' if alinh > 0 else '🔴 Baixista'}")
st.progress(min(abs(alinh) / 100, 1))

st.write("### 📝 Leitura do Momento")
resumo = f"O mercado é conduzido principalmente pelo {df.iloc[0]['Ativo']}. "
resumo += f"A fragmentação é {'Alta' if alinh < 40 else 'Baixa'}. "
resumo += f"Viés predominante: {'Altista' if alinh > 0 else 'Baixista'}."
st.success(resumo)

df['Status'] = df.apply(lambda x: "🟢 Conf" if x['Score'] * x['Corr'] > 0 else ("🔴 Quebra" if x['Score'] * x['Corr'] < -50 else "🟡 Div"), axis=1)
st.table(df[['Ativo', 'Pct_Dominancia', 'Conviccao', 'Score', 'Status']].rename(columns={'Pct_Dominancia': 'Dom %'}))

# 5. Legendas no Rodapé
st.write("---")
st.write("### 📖 Guia de Leitura e Legendas")

with st.expander("📌 Legenda de Status de Correlação"):
    st.info("- **🟢 Conf:** Ativo alinhado com o WIN. **Ajuda o movimento.**\n- **🟡 Div:** Ativo hesitante. **Cautela.**\n- **🔴 Quebra:** Ativo empurra contra a natureza. **Possível reversão.**")

with st.expander("📈 Como ler o nosso gráfico de Dominância"):
    st.write("1. **Driver Primário:** Ativo com maior poder de puxar o preço do WIN agora.\n2. **Dominância (%):** Peso real de influência.\n3. **Convicção:** Energia do movimento.\n4. **Score WIN (-100 a 100):** Pressão no índice.")

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Configuração da página
st.set_page_config(page_title="MACA-QUANTI ELITE", layout="centered")
st.title("🍎 MACA-QUANTI ELITE")

# Definição dos ativos
vies_ativos = {
    "FIXA11.SA": {"nome": "DI FUTURO", "corr": -1.0, "peso": 1.0},
    "BRL=X":     {"nome": "DÓLAR",     "corr": -1.0, "peso": 0.9},
    "FIND11.SA": {"nome": "IFNC",      "corr":  1.0, "peso": 0.8},
    "EWZ":       {"nome": "EWZ",       "corr":  1.0, "peso": 0.7},
}

# 1. Gráfico (Protegido por try-except)
st.subheader("📊 Gráfico WIN (5min)")
try:
    # Tentativa de carregar o WIN. Se falhar, exibe apenas aviso, sem erro fatal.
    df_win = yf.download("WIN=F", period="1d", interval="5m", progress=False)
    if not df_win.empty:
        st.line_chart(df_win['Close'])
    else:
        st.info("Gráfico WIN indisponível (Mercado fechado ou sem dados).")
except:
    st.info("Gráfico WIN não carregado.")

# 2. Processamento Principal
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
    # Normalização Logística para evitar que convicção trave em 100
    conviccao = np.clip(vol * 1500, 10, 95)
    score_win = np.clip(z * cfg['corr'] * 33, -100, 100)
    dominancia = abs(z) * cfg['peso'] * (conviccao / 100)
    dados.append({"Ativo": cfg['nome'], "Dominancia": dominancia, "Conviccao": conviccao, "Score": score_win, "Corr": cfg['corr']})

df = pd.DataFrame(dados).sort_values("Dominancia", ascending=False)
df['Pct_Dominancia'] = (df['Dominancia'] / df['Dominancia'].sum()) * 100

# 3. Exibição da Hierarquia
st.write("---")
st.subheader("🎯 Hierarquia de Drivers")
col1, col2 = st.columns(2)
col1.metric("Primário", df.iloc[0]['Ativo'])
col2.metric("Secundário", df.iloc[1]['Ativo'])

# 4. Alinhamento e Leitura
alinh = df['Score'].mean()
st.write(f"### **ALINHAMENTO GERAL: {abs(alinh):.1f}%**")
st.write(f"Sentido: {'🟢 Altista' if alinh > 0 else '🔴 Baixista'}")

st.write("### 📝 Leitura do Momento")
resumo = f"O mercado é conduzido pelo {df.iloc[0]['Ativo']}. A fragmentação é {'Alta' if alinh < 40 else 'Baixa'}. Viés: {'Altista' if alinh > 0 else 'Baixista'}."
st.success(resumo)

# 5. Tabela de Scores
df['Status'] = df.apply(lambda x: "🟢 Conf" if x['Score'] * x['Corr'] > 0 else ("🔴 Quebra" if x['Score'] * x['Corr'] < -50 else "🟡 Div"), axis=1)
st.table(df[['Ativo', 'Pct_Dominancia', 'Conviccao', 'Score', 'Status']])

# 6. Rodapé com Legendas
st.write("---")
with st.expander("📌 Legenda de Status de Correlação"):
    st.info("- **🟢 Conf:** Ajuda o movimento do WIN.\n- **🟡 Div:** Cautela, correlação falhando.\n- **🔴 Quebra:** O ativo empurra contra o WIN (Alerta de possível reversão).")
with st.expander("📈 Como ler este Painel"):
    st.write("O painel mostra quem está ditando o preço (Driver Primário). Se o driver principal estiver em **Quebra Estrutural**, priorize sair do trade atual.")

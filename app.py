import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="MACA-QUANTI", layout="wide")

st.title("🍎 MACA-QUANTI")

macro_ativos = {
    "^BVSP": "IBOVESPA", "BRL=X": "DÓLAR", "FIXA11.SA": "JUROS",
    "MATB11.SA": "IMAT", "FIND11.SA": "IFNC", "B3SA3.SA": "B3SA3",
    "EWZ": "EWZ", "^VIX": "VIX", "ES=F": "S&P 500", "NQ=F": "NASDAQ"
}

ativos_dados = []
series_z = {}

with st.spinner("Calculando..."):
    for cod, nome in macro_ativos.items():
        try:
            df = yf.download(cod, period="60d", interval="1d", progress=False)
            if not df.empty:
                fechamento = df['Close'].iloc[:, 0] if isinstance(df['Close'], pd.DataFrame) else df['Close']
                z_serie = (fechamento - fechamento.rolling(20).mean()) / fechamento.rolling(20).std()
                series_z[nome] = z_serie.tail(15)
                z = z_serie.iloc[-1]
                # Definimos a cor por emoji, que é o que o Streamlit nunca falha em renderizar
                cor_emoji = "🔴" if z > 1.5 else ("🟢" if z < -1.5 else "⚪")
                ativos_dados.append({"nome": nome, "z": z, "emoji": cor_emoji})
        except: continue

# Usando colunas nativas sem HTML complexo para garantir que apareça
cols = st.columns(3)
for i, item in enumerate(ativos_dados):
    with cols[i % 3]:
        # Criamos o bloco sem CSS injetado, usando apenas componentes do Streamlit
        st.subheader(f"{item['emoji']} {item['nome']}")
        st.metric(label="Z-Score", value=f"{item['z']:.2f}")
        st.divider()

# Gráfico
st.subheader("📊 Rastro (15 dias)")
fig = go.Figure()
for nome, serie in series_z.items():
    fig.add_trace(go.Scatter(x=serie.index.strftime('%d/%m'), y=serie.values, mode='lines', name=nome))
fig.update_layout(height=350, font_color="#fff", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig, use_container_width=True)
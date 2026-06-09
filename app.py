import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Configuração de interface limpa para mobile
st.set_page_config(page_title="MACA-QUANTI", layout="centered")

st.title("🍎 MACA-QUANTI")

macro_ativos = {
    "^BVSP": "IBOVESPA", "BRL=X": "DÓLAR", "FIXA11.SA": "JUROS",
    "MATB11.SA": "IMAT", "FIND11.SA": "IFNC", "B3SA3.SA": "B3SA3",
    "EWZ": "EWZ", "^VIX": "VIX", "ES=F": "S&P 500", "NQ=F": "NASDAQ"
}

ativos_dados = []
series_z = {}

# Processamento dos dados
with st.spinner("Calculando..."):
    for cod, nome in macro_ativos.items():
        try:
            df = yf.download(cod, period="60d", interval="1d", progress=False)
            if not df.empty:
                fechamento = df['Close'].iloc[:, 0] if isinstance(df['Close'], pd.DataFrame) else df['Close']
                z_serie = (fechamento - fechamento.rolling(20).mean()) / fechamento.rolling(20).std()
                series_z[nome] = z_serie.tail(15)
                z = z_serie.iloc[-1]
                ativos_dados.append({"nome": nome, "z": z})
        except: continue

# Grid em 2 colunas nativo (o sistema aceita 100% e não quebra no mobile)
cols = st.columns(2)
for i, item in enumerate(ativos_dados):
    with cols[i % 2]:
        # Lógica de cores nativa usando delta_color
        # Z > 1.5 = VENDA (Vermelho), Z < -1.5 = COMPRA (Verde), Neutro = Branco
        if item['z'] > 1.5:
            st.metric(label=item['nome'], value=f"{item['z']:.2f}", delta="VENDA", delta_color="inverse")
        elif item['z'] < -1.5:
            st.metric(label=item['nome'], value=f"{item['z']:.2f}", delta="COMPRA", delta_color="normal")
        else:
            st.metric(label=item['nome'], value=f"{item['z']:.2f}", delta="NEUTRO", delta_color="off")

# Gráfico otimizado
st.subheader("📊 Rastro (15 dias)")
fig = go.Figure()
for nome, serie in series_z.items():
    fig.add_trace(go.Scatter(x=serie.index.strftime('%d/%m'), y=serie.values, mode='lines', name=nome))

fig.update_layout(
    height=300, 
    margin=dict(l=10, r=10, t=10, b=10),
    paper_bgcolor="rgba(0,0,0,0)", 
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="#fff",
    legend=dict(orientation="h", yanchor="top", y=-0.2)
)
st.plotly_chart(fig, use_container_width=True)

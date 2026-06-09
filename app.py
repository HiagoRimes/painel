import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Configuração de página
st.set_page_config(page_title="MACA-QUANTI", layout="centered")

st.title("🍎 MACA-QUANTI")

# Dicionário de ativos
macro_ativos = {
    "^BVSP": "IBOVESPA", "BRL=X": "DÓLAR", "FIXA11.SA": "JUROS",
    "MATB11.SA": "IMAT", "FIND11.SA": "IFNC", "B3SA3.SA": "B3SA3",
    "EWZ": "EWZ", "^VIX": "VIX", "ES=F": "S&P 500", "NQ=F": "NASDAQ"
}

ativos_dados = []
series_z = {}

# Processamento com tratamento de erro
with st.spinner("Calculando dados em tempo real..."):
    for cod, nome in macro_ativos.items():
        try:
            df = yf.download(cod, period="60d", interval="1d", progress=False)
            if not df.empty:
                fechamento = float(df['Close'].iloc[-1])
                media = float(df['Close'].rolling(20).mean().iloc[-1])
                std = float(df['Close'].rolling(20).std().iloc[-1])
                
                # Cálculo do Z-Score
                z = (fechamento - media) / std
                
                # Guardando os dados para o gráfico
                series = (df['Close'] - df['Close'].rolling(20).mean()) / df['Close'].rolling(20).std()
                series_z[nome] = series.tail(15)
                
                ativos_dados.append({"nome": nome, "z": z})
        except Exception:
            continue

# Grid de colunas (o Streamlit gerencia a responsividade)
if ativos_dados:
    cols = st.columns(2)
    for i, item in enumerate(ativos_dados):
        with cols[i % 2]:
            if item['z'] > 1.5:
                st.metric(label=item['nome'], value=f"{item['z']:.2f}", delta="VENDA", delta_color="inverse")
            elif item['z'] < -1.5:
                st.metric(label=item['nome'], value=f"{item['z']:.2f}", delta="COMPRA", delta_color="normal")
            else:
                st.metric(label=item['nome'], value=f"{item['z']:.2f}", delta="NEUTRO", delta_color="off")

    # Gráfico de Rastro
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
else:
    st.error("Erro ao processar os dados. Verifique a internet ou o arquivo requirements.txt.")

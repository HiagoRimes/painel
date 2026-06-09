import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Configuração simples para mobile (sem o 'wide')
st.set_page_config(page_title="MACA-QUANTI", layout="centered")

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
                ativos_dados.append({"nome": nome, "z": z})
        except: continue

# EXIBIÇÃO EM UMA COLUNA (Estável para Mobile)
for item in ativos_dados:
    # Usamos o st.metric dentro de um container para garantir o isolamento visual
    with st.container():
        st.metric(label=item['nome'], value=f"Z: {item['z']:.2f}")
        st.divider() # Linha divisória simples para organizar

# GRÁFICO (Configurado para largura do celular)
st.subheader("📊 Rastro (15 dias)")
fig = go.Figure()
for nome, serie in series_z.items():
    fig.add_trace(go.Scatter(x=serie.index.strftime('%d/%m'), y=serie.values, mode='lines', name=nome))

# Ajustes específicos para o gráfico não ficar gigante no celular
fig.update_layout(
    height=300, 
    margin=dict(l=20, r=20, t=20, b=20),
    font_color="#fff", 
    paper_bgcolor="rgba(0,0,0,0)", 
    plot_bgcolor="rgba(0,0,0,0)",
    legend=dict(orientation="h", yanchor="top", y=-0.2)
)
st.plotly_chart(fig, use_container_width=True)
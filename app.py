import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="MACA-QUANTI", layout="wide")

st.markdown("""
    <style>
        .metric-card { background-color: #262730; padding: 10px; border-radius: 8px; 
                      text-align: center; border-left: 5px solid #444; margin-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

st.title("🍎 MACA-QUANTI")

macro_ativos = {
    "^BVSP": "IBOVESPA", "BRL=X": "DÓLAR", "FIXA11.SA": "JUROS",
    "MATB11.SA": "IMAT", "FIND11.SA": "IFNC", "B3SA3.SA": "B3SA3",
    "EWZ": "EWZ", "^VIX": "VIX", "ES=F": "S&P 500", "NQ=F": "NASDAQ"
}

series_z = {}
lista_ativos = []

with st.spinner("Calculando..."):
    for cod, nome in macro_ativos.items():
        try:
            df = yf.download(cod, period="60d", interval="1d", progress=False)
            if not df.empty:
                fechamento = df['Close'].iloc[:, 0] if isinstance(df['Close'], pd.DataFrame) else df['Close']
                z_serie = (fechamento - fechamento.rolling(20).mean()) / fechamento.rolling(20).std()
                series_z[nome] = z_serie.tail(15)
                z = z_serie.iloc[-1]
                lista_ativos.append({"nome": nome, "z": z})
        except: continue

# Grid de Cartões (Otimizado para Mobile)
cols = st.columns(2)
for i, item in enumerate(lista_ativos):
    cor = "#FF4B4B" if item['z'] > 1.5 else ("#00CC96" if item['z'] < -1.5 else "#888")
    with cols[i % 2]:
        st.markdown(f"""
            <div class="metric-card" style="border-left-color: {cor};">
                <div style="font-weight:bold;">{item['nome']}</div>
                <div style="font-size:16px;">Z: {item['z']:.2f}</div>
            </div>
        """, unsafe_allow_html=True)

# Gráfico de Linha (O Rastro)
st.subheader("📊 Rastro dos Últimos 15 Dias")
fig = go.Figure()
for nome, serie in series_z.items():
    fig.add_trace(go.Scatter(x=serie.index.strftime('%d/%m'), y=serie.values, mode='lines', name=nome))

fig.update_layout(height=300, margin=dict(l=0, r=0, t=30, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#fff")
st.plotly_chart(fig, use_container_width=True)

st.caption("🟢 Z < -1.5 (Compra) | 🔴 Z > 1.5 (Venda)")
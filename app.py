import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Configuração de layout
st.set_page_config(page_title="MACA-QUANTI", layout="wide")

# CSS para estilizar os containers nativos do Streamlit
st.markdown("""
    <style>
        .metric-box {
            background-color: #262730;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            border-left: 6px solid #444;
            margin-bottom: 10px;
        }
        .metric-title { font-weight: bold; font-size: 14px; margin-bottom: 5px; color: white; }
        .metric-value { font-size: 18px; color: #ddd; }
    </style>
""", unsafe_allow_html=True)

st.title("🍎 MACA-QUANTI")

macro_ativos = {
    "^BVSP": "IBOVESPA", "BRL=X": "DÓLAR", "FIXA11.SA": "JUROS",
    "MATB11.SA": "IMAT", "FIND11.SA": "IFNC", "B3SA3.SA": "B3SA3",
    "EWZ": "EWZ", "^VIX": "VIX", "ES=F": "S&P 500", "NQ=F": "NASDAQ"
}

series_z = {}
ativos_dados = []

with st.spinner("Calculando..."):
    for cod, nome in macro_ativos.items():
        try:
            df = yf.download(cod, period="60d", interval="1d", progress=False)
            if not df.empty:
                fechamento = df['Close'].iloc[:, 0] if isinstance(df['Close'], pd.DataFrame) else df['Close']
                z_serie = (fechamento - fechamento.rolling(20).mean()) / fechamento.rolling(20).std()
                series_z[nome] = z_serie.tail(15)
                z = z_serie.iloc[-1]
                
                # Define cor da borda
                cor = "#FF4B4B" if z > 1.5 else ("#00CC96" if z < -1.5 else "#888")
                ativos_dados.append({"nome": nome, "z": z, "cor": cor})
        except: continue

# Grid inteligente: Ajusta colunas automaticamente
# O Streamlit gerencia o layout para não quebrar
cols = st.columns(3)
for i, item in enumerate(ativos_dados):
    with cols[i % 3]:
        st.markdown(f"""
            <div class="metric-box" style="border-left-color: {item['cor']};">
                <div class="metric-title">{item['nome']}</div>
                <div class="metric-value">Z: {item['z']:.2f}</div>
            </div>
        """, unsafe_allow_html=True)

# Gráfico de Linha
st.subheader("📊 Rastro (15 dias)")
fig = go.Figure()
for nome, serie in series_z.items():
    fig.add_trace(go.Scatter(x=serie.index.strftime('%d/%m'), y=serie.values, mode='lines', name=nome))

fig.update_layout(
    height=350, margin=dict(l=0, r=0, t=20, b=0),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font_color="#fff",
    legend=dict(orientation="h", yanchor="top", y=-0.3, xanchor="center", x=0.5)
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.write("🟢 Z < -1.5 (Compra) | 🔴 Z > 1.5 (Venda)")
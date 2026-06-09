import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Configuração de layout
st.set_page_config(page_title="MACA-QUANTI", layout="wide")

# Estilo para o título ser responsivo
st.markdown("""
    <style>
        .main-title { font-size: 28px; font-weight: bold; }
        @media (max-width: 600px) { .main-title { font-size: 20px !important; } }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🍎 MACA-QUANTI</div>', unsafe_allow_html=True)

macro_ativos = {
    "^BVSP": "IBOVESPA", "BRL=X": "DÓLAR", "FIXA11.SA": "JUROS",
    "MATB11.SA": "IMAT", "FIND11.SA": "IFNC", "B3SA3.SA": "B3SA3",
    "EWZ": "EWZ", "^VIX": "VIX", "ES=F": "S&P 500", "NQ=F": "NASDAQ"
}

series_z = {}
ativos_processados = []

with st.spinner("Calculando..."):
    for cod, nome in macro_ativos.items():
        try:
            df = yf.download(cod, period="60d", interval="1d", progress=False)
            if not df.empty:
                fechamento = df['Close'].iloc[:, 0] if isinstance(df['Close'], pd.DataFrame) else df['Close']
                z_serie = (fechamento - fechamento.rolling(20).mean()) / fechamento.rolling(20).std()
                series_z[nome] = z_serie.tail(15)
                z = z_serie.iloc[-1]
                ativos_processados.append({"nome": nome, "z": z})
        except: continue

# Grid usando colunas nativas do Streamlit (Muito mais estável)
# Vamos definir 3 colunas para PC e 2 para mobile
cols = st.columns([1, 1, 1]) 
for i, item in enumerate(ativos_processados):
    with cols[i % 3]:
        # Define a cor de destaque baseada no Z-Score
        cor = "normal"
        if item['z'] > 1.5: cor = "inverse" # Vermelho para Venda
        elif item['z'] < -1.5: cor = "normal" # Verde para Compra
        
        # O st.metric cria a caixa automaticamente e é nativo do Streamlit
        st.metric(label=item['nome'], value=f"{item['z']:.2f}")

# Gráfico de Linha
st.subheader("📊 Rastro (15 dias)")
fig = go.Figure()
for nome, serie in series_z.items():
    fig.add_trace(go.Scatter(x=serie.index.strftime('%d/%m'), y=serie.values, mode='lines', name=nome))

fig.update_layout(
    height=350, margin=dict(l=0, r=0, t=20, b=0),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font_color="#fff",
    legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5)
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.write("🟢 Z < -1.5 (Compra) | 🔴 Z > 1.5 (Venda)")
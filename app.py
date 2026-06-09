import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="MACA-QUANTI", layout="wide")

# CSS Otimizado: Grid responsivo e bordas totais
st.markdown("""
    <style>
        .grid-container { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 10px; margin-bottom: 20px; }
        .card { background-color: #262730; padding: 12px; border-radius: 8px; text-align: center; 
                border-left: 6px solid #444; height: 100%; }
        .card-name { font-weight: bold; font-size: 14px; }
        .card-val { font-size: 16px; margin-top: 5px; }
    </style>
""", unsafe_allow_html=True)

st.title("🍎 MACA-QUANTI")

macro_ativos = {
    "^BVSP": "IBOVESPA", "BRL=X": "DÓLAR", "FIXA11.SA": "JUROS",
    "MATB11.SA": "IMAT", "FIND11.SA": "IFNC", "B3SA3.SA": "B3SA3",
    "EWZ": "EWZ", "^VIX": "VIX", "ES=F": "S&P 500", "NQ=F": "NASDAQ"
}

series_z = {}
cards_html = '<div class="grid-container">'

with st.spinner("Calculando..."):
    for cod, nome in macro_ativos.items():
        try:
            df = yf.download(cod, period="60d", interval="1d", progress=False)
            if not df.empty:
                fechamento = df['Close'].iloc[:, 0] if isinstance(df['Close'], pd.DataFrame) else df['Close']
                z_serie = (fechamento - fechamento.rolling(20).mean()) / fechamento.rolling(20).std()
                series_z[nome] = z_serie.tail(15)
                z = z_serie.iloc[-1]
                cor = "#FF4B4B" if z > 1.5 else ("#00CC96" if z < -1.5 else "#888")
                cards_html += f'''<div class="card" style="border-left-color:{cor};">
                                    <div class="card-name">{nome}</div>
                                    <div class="card-val">Z: {z:.2f}</div>
                                  </div>'''
        except: continue
cards_html += '</div>'
st.markdown(cards_html, unsafe_allow_html=True)

# Gráfico de Linha
st.subheader("📊 Rastro (15 dias)")
fig = go.Figure()
for nome, serie in series_z.items():
    fig.add_trace(go.Scatter(x=serie.index.strftime('%d/%m'), y=serie.values, mode='lines', name=nome))

fig.update_layout(
    height=400, margin=dict(l=0, r=0, t=20, b=0), 
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", 
    font_color="#fff",
    legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5) # Legenda abaixo
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("🟢 **Z < -1.5 (Compra)** | 🔴 **Z > 1.5 (Venda)**")
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Configuração adaptativa do Streamlit com injeção de CSS para telas pequenas e grandes
st.set_page_config(page_title="MACA-QUANTI - Mobile Pro", layout="wide")

# Força o título principal e as margens a se adaptarem perfeitamente
st.markdown("""
    <style>
        .block-container { padding-top: 4rem; padding-bottom: 1rem; padding-left: 0.5rem; padding-right: 0.5rem; }
        .main-title { 
            font-size: 22px !important; 
            font-weight: bold; 
            line-height: 1.2 !important; 
            margin-top: 10px !important;
            margin-bottom: 4px; 
            padding-bottom: 0px;
            white-space: normal; 
        }
        .caption-text { font-size: 12px !important; color: #aaa; margin-top: 0px; line-height: 1.2 !important; }
        .legenda-box {
            background-color: #252526;
            border-radius: 8px;
            padding: 10px;
            margin-top: 10px;
            margin-bottom: 15px;
            border-left: 4px solid #888;
        }
        .legenda-item { font-size: 12px !important; margin-bottom: 4px; color: #e0e0e0; }
        
        @media (min-width: 992px) {
            .block-container { padding-top: 5.5rem !important; }
            .main-title { font-size: 32px !important; margin-top: 0px !important; }
            .caption-text { font-size: 14px !important; }
            .legenda-item { font-size: 13px !important; }
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">🍎 MACA-QUANTI - Painel Quantitativo</p>', unsafe_allow_html=True)
st.markdown('<p class="caption-text">Afastamento Estatístico de Preços (Média de 20 Períodos)</p>', unsafe_allow_html=True)

st.markdown("""
    <div class="legenda-box">
        <div class="legenda-item">🟢 <b>Z-Score abaixo de -2.0 (Barato):</b> Procura-se Compra</div>
        <div class="legenda-item">⚫ <b>Z-Score próximo de 0.0 (Neutro):</b> Sem Operação</div>
        <div class="legenda-item">🔴 <b>Z-Score acima de +2.0 (Caro):</b> Procura-se Venda</div>
    </div>
""", unsafe_allow_html=True)

macro_ativos = {
    "^BVSP": "IBOVESPA",
    "BRL=X": "DÓLAR COMERCIAL",
    "FIXA11.SA": "JUROS DI",
    "MATB11.SA": "IMAT",
    "FIND11.SA": "IFNC",
    "B3SA3.SA": "B3SA3",
    "EWZ": "EWZ",
    "^VIX": "VIX",
    "ES=F": "S&P 500",
    "NQ=F": "NASDAQ"
}

dados_finais = []
series_z_score = {}

with st.spinner("Calculando..."):
    for codigo, nome_real in macro_ativos.items():
        try:
            df = yf.download(codigo, period="60d", interval="1d", progress=False)
            if not df.empty and 'Close' in df.columns:
                fechamento = df['Close'].iloc[:, 0] if isinstance(df['Close'], pd.DataFrame) else df['Close']
                fechamento = fechamento.dropna()
                
                if len(fechamento) >= 20:
                    media = fechamento.rolling(window=20).mean()
                    desvio = fechamento.rolling(window=20).std()
                    z_score_serie = (fechamento - media) / desvio
                    
                    series_z_score[nome_real] = z_score_serie.tail(15) 
                    ultimo_z = float(z_score_serie.iloc[-1])
                    
                    dados_finais.append({
                        "Ativo": nome_real,
                        "Cotação": f"{float(fechamento.iloc[-1]):.2f}",
                        "Z-Score": ultimo_z if not pd.isna(ultimo_z) else 0.0
                    })
        except:
            continue

if dados_finais:
    df_painel = pd.DataFrame(dados_finais)
    
    fig_mapa = px.treemap(
        df_painel,
        path=["Ativo"],
        values=np.ones(len(df_painel)),
        color="Z-Score",
        color_continuous_scale=["#00CC66", "#252526", "#FF3333"],
        range_color=[-2.5, 2.5]
    )
    fig_mapa.update_layout(margin=dict(t=55, l=5, r=5, b=5), height=500)
    st.plotly_chart(fig_mapa, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown("### 📊 Rastro dos Últimos 15 Dias")
    if series_z_score:
        fig_linhas = go.Figure()
        for nome_ativo, serie in series_z_score.items():
            fig_linhas.add_trace(go.Scatter(
                x=serie.index.strftime('%d/%m'),
                y=serie.values,
                mode='lines',
                name=nome_ativo,
                line=dict(width=2)
            ))
        
        fig_linhas.update_layout(
            paper_bgcolor="#1e1e1e", plot_bgcolor="#1e1e1e",
            font=dict(color="#FFFFFF", size=10),
            margin=dict(t=10, l=5, r=5, b=5), height=380,
            xaxis=dict(gridcolor="#333333"), yaxis=dict(gridcolor="#333333", range=[-3.1, 3.1])
        )
        st.plotly_chart(fig_linhas, use_container_width=True, config={'displayModeBar': False})
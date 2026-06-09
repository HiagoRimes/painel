import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Configuração adaptativa do Streamlit com injeção de CSS para telas pequenas e grandes
st.set_page_config(page_title="MACA-QUANTI - Mobile Pro", layout="wide")

# Força o título principal e as margens a se adaptarem perfeitamente sem cortar em nenhuma tela
st.markdown("""
    <style>
        /* Celular: Margem generosa no topo para o navegador mobile */
        .block-container { padding-top: 4rem; padding-bottom: 1rem; padding-left: 0.5rem; padding-right: 0.5rem; }
        
        /* Ajusta o tamanho do título e adiciona margem superior de segurança */
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
        
        /* Estilização da Legenda Dinâmica */
        .legenda-box {
            background-color: #252526;
            border-radius: 8px;
            padding: 10px;
            margin-top: 10px;
            margin-bottom: 15px;
            border-left: 4px solid #888;
        }
        .legenda-item { font-size: 12px !important; margin-bottom: 4px; color: #e0e0e0; }
        
        /* --- CORREÇÃO COMPUTADOR (Telas Grandes) --- */
        @media (min-width: 992px) {
            /* Aumentado para 5.5rem para empurrar o layout abaixo do menu do Streamlit no PC */
            .block-container { padding-top: 5.5rem !important; }
            .main-title { font-size: 32px !important; margin-top: 0px !important; }
            .caption-text { font-size: 14px !important; }
            .legenda-item { font-size: 13px !important; }
        }
    </style>
""", unsafe_allow_html=True)

# Título limpo e responsivo
st.markdown('<p class="main-title">🍎 MACA-QUANTI - Painel Quantitativo</p>', unsafe_allow_html=True)
st.markdown('<p class="caption-text">Afastamento Estatístico de Preços (Média de 20 Períodos)</p>', unsafe_allow_html=True)

# Bloco de Legenda Operacional do Z-Score
st.markdown("""
    <div class="legenda-box">
        <div class="legenda-item">🟢 <b>Z-Score abaixo de -2.0 (Barato):</b> Ativo muito afastado para baixo da média. Zona de exaustão de venda. <b>(Procura-se Compra)</b></div>
        <div class="legenda-item">⚫ <b>Z-Score próximo de 0.0 (Neutro):</b> Preço em equilíbrio, trabalhando exatamente na média. Sem distorção. <b>(Sem Operação)</b></div>
        <div class="legenda-item">🔴 <b>Z-Score acima de +2.0 (Caro):</b> Ativo muito esticado para cima em relação à média. Zona de exaustão de compra. <b>(Risco de Topo / Procura-se Venda)</b></div>
    </div>
""", unsafe_allow_html=True)

# Grade de ativos com quebras de linha manuais
macro_ativos = {
    "^BVSP": "IBOVESPA",
    "BRL=X": "DÓLAR COMERCIAL",
    "FIXA11.SA": "JUROS DI",
    "MATB11.SA": "IMAT<br>(Commodities)",
    "FIND11.SA": "IFNC<br>(Bancos)",
    "B3SA3.SA": "B3SA3<br>(Bolsa)",
    "EWZ": "EWZ<br>(Ibov em USD)",
    "^VIX": "VIX<br>(Índice do Medo)",
    "ES=F": "S&P 500<br>Futuro",
    "NQ=F": "NASDAQ<br>Futuro"
}

dados_finais = []
series_z_score = {}

with st.spinner("Calculando distorções matemáticas do mercado..."):
    for codigo, nome_real in macro_ativos.items():
        try:
            df = yf.download(codigo, period="60d", interval="1d", progress=False)
            if not df.empty and 'Close' in df.columns:
                fechamento = df['Close']
                if isinstance(fechamento, pd.DataFrame):
                    fechamento = fechamento.iloc[:, 0]
                fechamento = fechamento.dropna()
                
                if len(fechamento) >= 20:
                    media = fechamento.rolling(window=20).mean()
                    desvio = fechamento.rolling(window=20).std()
                    z_score_serie = (fechamento - media) / desvio
                    
                    series_z_score[nome_real.replace("<br>", " ")] = z_score_serie.tail(15) 
                    
                    ultima_cotacao = float(fechamento.iloc[-1])
                    cotacao_anterior = float(fechamento.iloc[-2])
                    variacao_dia = ((ultima_cotacao / cotacao_anterior) - 1) * 100
                    ultimo_z = float(z_score_serie.iloc[-1])
                    
                    if pd.isna(ultimo_z) or np.isinf(ultimo_z):
                        ultimo_z = 0.0
                        
                    if codigo == "^BVSP":
                        preco_txt = f"{int(ultima_cotacao)} pts"
                    elif "BRL=" in codigo:
                        preco_txt = f"R$ {ultima_cotacao:.4f}"
                    else:
                        preco_txt = f"R$ {ultima_cotacao:.2f}" if ".SA" in codigo else f"{ultima_cotacao:.2f}"
                        
                    dados_finais.append({
                        "Ativo": nome_real,
                        "Cotação": preco_txt,
                        "Variação Diária": float(variacao_dia),
                        "Z-Score": ultimo_z
                    })
        except:
            continue

if dados_finais:
    df_painel = pd.DataFrame(dados_finais)
    
    # 1. MAPA DE CALOR
    fig_mapa = px.treemap(
        df_painel,
        path=["Ativo"],
        values=np.ones(len(df_painel)),
        color="Z-Score",
        color_continuous_scale=["#00CC66", "#252526", "#FF3333"],
        color_continuous_midpoint=0,
        range_color=[-2.5, 2.5],
        custom_data=["Cotação", "Variação Diária", "Z-Score"]
    )
    
    fig_mapa.update_traces(
        texttemplate="<b style='font-size:14px;'>%{label}</b><br><span style='font-size:11px;'>%{customdata[0]}</span><br><span style='font-size:11px;'>Var: %{customdata[1]:.2f}%</span><br><b style='font-size:13px;'>Z: %{customdata[2]:.2f}</b>",
        textposition="middle center",
        tiling=dict(pad=3)
    )
    
    fig_mapa.update_layout(
        coloraxis_colorbar=dict(
            title="Escala Z-Score",
            title_font=dict(size=12, color="#FFFFFF", family="Arial"),
            title_side="top",     
            tickfont=dict(size=10, color="#FFFFFF"),
            orientation="h",       
            yanchor="bottom",
            y=1.05,               
            xanchor="center",
            x=0.5,                
            thickness=13,         
            len=0.85,             
            tickvals=[-2, -1, 0, 1, 2],       
            ticktext=["-2", "-1", "0", "+1", "+2"] 
        ),
        margin=dict(t=55, l=5, r=5, b=5), 
        height=500 
    )
    # CORREÇÃO: use_container_width=True substitui o width='stretch'
    st.plotly_chart(fig_mapa, use_container_width=True, config={'displayModeBar': False})
    
    # 2. HISTÓRICO DE TENDÊNCIA
    st.markdown("### 📊 Rastro dos Últimos 15 Dias")
    if series_z_score:
        fig_linhas = go.Figure()
        for nome_ativo, serie in series_z_score.items():
            fig_linhas.add_trace(go.Scatter(
                x=serie.index.strftime('%d
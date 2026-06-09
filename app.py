import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time

st.set_page_config(page_title="MACA-QUANTI PRO", layout="centered")
st.title("🍎 MACA-QUANTI PRO")

# Dicionário atualizado com o DI Futuro (FIXA11.SA como proxy)
vies_ativos = {
    "^BVSP": ("IBOV", 1.0, 0.2), 
    "BRL=X": ("DÓLAR", -1.0, 0.3),
    "FIXA11.SA": ("DI FUTURO", -1.0, 0.25), # DI Adicionado com peso alto
    "EWZ": ("EWZ", 1.0, 0.05), 
    "ES=F": ("S&P500", 1.0, 0.1), 
    "NQ=F": ("NASDAQ", 1.0, 0.1), 
    "^VIX": ("VIX", -1.0, 0.0)
}

def get_data(cod):
    df = yf.download(cod, period="30d", interval="1d", progress=False)
    # Correção para tratar o retorno do yfinance conforme versões recentes
    c = df['Close']
    if isinstance(c, pd.DataFrame):
        c = c.iloc[:, 0]
    
    # Tratamento para garantir que c é Series numérica
    c = pd.to_numeric(c, errors='coerce').dropna()
    
    if len(c) < 20: return 0, 0
    
    z = (float(c.iloc[-1]) - float(c.rolling(20).mean().iloc[-1])) / float(c.rolling(20).std().iloc[-1])
    return float(c.iloc[-1]), z

# Processamento
dados_win = []
for cod, (nome, mult, peso) in vies_ativos.items():
    preco, z = get_data(cod)
    forca = z * mult
    dados_win.append({"Ativo": nome, "Preço": preco, "Forca": forca, "Peso": peso})
    time.sleep(0.2)

df_win = pd.DataFrame(dados_win)
vies_ponderado = (df_win['Forca'] * df_win['Peso']).sum()

# Exibição
st.subheader("🎯 Viés para o WIN")
if vies_ponderado > 0.1: st.success(f"VIÉS ALTISTA (Força Ponderada: {vies_ponderado:.2f})")
elif vies_ponderado < -0.1: st.error(f"VIÉS BAIXISTA (Força Ponderada: {vies_ponderado:.2f})")
else: st.info("MERCADO NEUTRO")

st.table(df_win[['Ativo', 'Preço', 'Forca']])

# Carteira
st.subheader("💼 Carteira")
carteira = {"B3SA3.SA": "B3SA3", "FIND11.SA": "IFNC", "MATB11.SA": "IMAT"}
df_cart = []
for cod, nome in carteira.items():
    p, z = get_data(cod)
    df_cart.append({"Ativo": nome, "Preço": p, "Z": z})
st.table(pd.DataFrame(df_cart))

# Gráfico
st.subheader("📈 IBOV (30d)")
df_g = yf.download("^BVSP", period="30d", interval="1d", progress=False)
c_g = df_g['Close'].iloc[:, 0] if isinstance(df_g['Close'], pd.DataFrame) else df_g['Close']

fig = go.Figure()
fig.add_trace(go.Scatter(x=df_g.index, y=c_g, name="Preço", line=dict(color='#00ff00')))
fig.add_trace(go.Scatter(x=df_g.index, y=c_g.rolling(5).mean(), name="Média 5", line=dict(color='yellow')))
fig.update_layout(height=250, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig, use_container_width=True)

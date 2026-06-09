import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time

st.set_page_config(page_title="MACA-QUANTI", layout="centered")
st.title("🍎 MACA-QUANTI")

# Dicionários separados
vies_ativos = {"^BVSP": ("IBOV", 1), "BRL=X": ("DÓLAR", -1), "EWZ": ("EWZ", 1), 
               "ES=F": ("S&P500", 1), "NQ=F": ("NASDAQ", 1), "^VIX": ("VIX", -1)}
carteira = {"B3SA3.SA": "B3SA3", "FIND11.SA": "IFNC", "MATB11.SA": "IMAT"}

def get_dados(ativos):
    lista = []
    for cod, nome in ativos.items():
        try:
            df = yf.download(cod, period="30d", interval="1d", progress=False)
            c = df['Close'].iloc[:, 0] if isinstance(df['Close'], pd.DataFrame) else df['Close']
            z = (float(c.iloc[-1]) - float(c.rolling(20).mean().iloc[-1])) / float(c.rolling(20).std().iloc[-1])
            lista.append({"Ativo": nome, "Preço": float(c.iloc[-1]), "Z": z})
            time.sleep(0.2)
        except: continue
    return pd.DataFrame(lista)

# Processamento
df_v = get_dados({k: v[0] for k, v in vies_ativos.items()})
df_v['Forca'] = [z * vies_ativos[list(vies_ativos.keys())[i]][1] for i, z in enumerate(df_v['Z'])]
df_c = get_dados(carteira)

# 1. Painel de Viés
st.subheader("🎯 Viés para o WIN")
vies = df_v['Forca'].mean()
if vies > 0.3: st.success(f"VIÉS ALTISTA (Força: {vies:.2f})")
elif vies < -0.3: st.error(f"VIÉS BAIXISTA (Força: {vies:.2f})")
else: st.info("MERCADO NEUTRO")

# 2. Tabelas separadas para não bagunçar
st.write("**Monitoramento WIN:**")
st.table(df_v[['Ativo', 'Preço', 'Forca']])
st.write("**Minha Carteira:**")
st.table(df_c[['Ativo', 'Preço', 'Z']])

# 3. Gráfico Consertado
st.subheader("📈 IBOV (30d)")
df_g = yf.download("^BVSP", period="30d", interval="1d", progress=False)
fig = go.Figure()
fig.add_trace(go.Scatter(x=df_g.index, y=df_g['Close'], name="IBOV", line=dict(color='#00ff00')))
fig.update_layout(height=250, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig, use_container_width=True)

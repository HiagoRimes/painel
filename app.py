import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time

st.set_page_config(page_title="MACA-QUANTI", layout="centered")
st.title("🍎 MACA-QUANTI")

# 1. Ativos de correlação do WIN (calculam viés)
vies_ativos = {
    "^BVSP": ("IBOV", 1), "BRL=X": ("DÓLAR", -1), "EWZ": ("EWZ", 1), 
    "ES=F": ("S&P500", 1), "NQ=F": ("NASDAQ", 1), "^VIX": ("VIX", -1)
}

# 2. Seus ativos da carteira (apenas monitoramento)
carteira = {"B3SA3.SA": "B3SA3", "FIND11.SA": "IFNC", "MATB11.SA": "IMAT"}

def get_dados(ativos):
    lista = []
    for cod, nome in ativos.items():
        try:
            df = yf.download(cod, period="30d", interval="1d", progress=False)
            c = df['Close'].iloc[:, 0] if isinstance(df['Close'], pd.DataFrame) else df['Close']
            z = (float(c.iloc[-1]) - float(c.rolling(20).mean().iloc[-1])) / float(c.rolling(20).std().iloc[-1])
            lista.append({"Ativo": nome, "Z": z, "Preço": float(c.iloc[-1])})
            time.sleep(0.2)
        except: continue
    return pd.DataFrame(lista)

# Processamento
df_vies = get_dados({k: v[0] for k, v in vies_ativos.items()})
df_vies['Forca'] = [z * vies_ativos[list(vies_ativos.keys())[i]][1] for i, z in enumerate(df_vies['Z'])]
df_carteira = get_dados(carteira)

# Exibição do Viés
vies_global = df_vies['Forca'].mean()
st.subheader("🎯 Viés para o WIN")
if vies_global > 0.3: st.success(f"VIÉS ALTISTA (Força: {vies_global:.2f})")
elif vies_global < -0.3: st.error(f"VIÉS BAIXISTA (Força: {vies_global:.2f})")
else: st.info("MERCADO NEUTRO")

# Tabela Única
df_final = pd.concat([df_vies[['Ativo', 'Preço', 'Z', 'Forca']], df_carteira[['Ativo', 'Preço', 'Z']]])
df_final['Sinal'] = df_final['Ativo'].apply(lambda x: "IBOV" if x == "IBOV" else "")
st.table(df_final.fillna("-"))

# Gráfico IBOV + Média
st.subheader("📈 IBOV (Últimos 30 dias)")
df_grafico = yf.download("^BVSP", period="30d", interval="1d", progress=False)
fig = go.Figure()
fig.add_trace(go.Scatter(x=df_grafico.index, y=df_grafico['Close'], name="Preço", line=dict(color='white')))
fig.add_trace(go.Scatter(x=df_grafico.index, y=df_grafico['Close'].rolling(5).mean(), name="Média 5", line=dict(color='yellow')))
fig.update_layout(height=300, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig, use_container_width=True)

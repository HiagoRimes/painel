import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="MACA-QUANTI ELITE", layout="centered")
st.title("🍎 MACA-QUANTI ELITE")

# 1. Configuração com Pesos Estruturais (Item 1 e 6)
vies_ativos = {
    "FIXA11.SA": {"nome": "DI FUTURO", "corr": -1.0, "peso": 1.00},
    "BRL=X":     {"nome": "DÓLAR",     "corr": -1.0, "peso": 0.90},
    "FIND11.SA": {"nome": "IFNC",      "corr":  1.0, "peso": 0.80},
    "EWZ":       {"nome": "EWZ",       "corr":  1.0, "peso": 0.70},
    "ES=F":      {"nome": "S&P500",    "corr":  1.0, "peso": 0.60},
    "^VIX":      {"nome": "VIX",       "corr": -1.0, "peso": 0.50},
    "NQ=F":      {"nome": "NASDAQ",    "corr":  1.0, "peso": 0.40},
}

def get_stats(cod):
    df = yf.download(cod, period="30d", interval="1d", progress=False)
    c = df['Close'].iloc[:, 0] if isinstance(df['Close'], pd.DataFrame) else df['Close']
    c = pd.to_numeric(c, errors='coerce').dropna()
    # Z-Score
    z = (float(c.iloc[-1]) - float(c.rolling(20).mean().iloc[-1])) / float(c.rolling(20).std().iloc[-1])
    # Convicção (proxy: Volatilidade recente)
    conviccao = float(c.pct_change().std() * 1000) 
    return float(c.iloc[-1]), z, conviccao

# Processamento
dados = []
for cod, cfg in vies_ativos.items():
    preco, z, conv = get_stats(cod)
    
    # Domínio: Força Estatística x Peso x Correlação Absoluta
    forca_direcional = z * cfg['corr']
    dominancia = abs(z) * cfg['peso'] * abs(cfg['corr'])
    
    dados.append({
        "Ativo": cfg['nome'],
        "Preço": preco,
        "Direcao": forca_direcional * 100, # Score Direcional (-100 a +100)
        "Conviccao": min(conv * 20, 100),  # Score 0-100
        "Dominancia": dominancia,
        "Corr_Status": "🟢 Confirmando" if forca_direcional > 0 else "🔴 Quebra"
    })

df = pd.DataFrame(dados)

# 2. Módulo de Dominância (Item 1 e 2)
total_dom = df['Dominancia'].sum()
df['Pct_Dominancia'] = (df['Dominancia'] / total_dom) * 100

st.subheader("🎯 Driver Dominante")
lider = df.loc[df['Dominancia'].idxmax()]
st.write(f"### **{lider['Ativo']}**")
st.write(f"**Dominância:** {lider['Pct_Dominancia']:.1f}% | **Confiança:** {'Alta' if lider['Pct_Dominancia'] > 30 else 'Moderada'}")

# 3. Painel de Alinhamento (Item 5)
alinhamento = df['Direcao'].mean()
st.write("---")
st.write(f"**ALINHAMENTO GERAL:** {alinhamento:.1f}%")
st.progress(min(max((alinhamento + 100) / 200, 0), 1))

# 4. Tabela de Scores
st.write("### 📊 Ranking Estrutural")
st.table(df[['Ativo', 'Pct_Dominancia', 'Conviccao', 'Direcao', 'Corr_Status']]
         .rename(columns={'Pct_Dominancia': 'Dominância', 'Direcao': 'Score WIN'}))

# Regime de mercado simples (Item 3)
st.write("### 🏷️ Regime de Mercado")
if abs(alinhamento) > 50: st.success("🟢 Tendência Forte")
elif abs(alinhamento) > 20: st.warning("🟡 Tendência Moderada")
else: st.info("⚪ Lateral / Compressão")

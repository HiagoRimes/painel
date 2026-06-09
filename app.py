import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.set_page_config(page_title="MACA-QUANTI PRO", layout="centered")
st.title("🍎 MACA-QUANTI PRO")

# Dicionário de ativos: Nome, Correlação com WIN, Peso
vies_ativos = {
    "^BVSP":   {"nome": "IBOV",      "mult":  1.0, "peso": 0.15},
    "BRL=X":   {"nome": "DÓLAR",     "mult": -1.0, "peso": 0.30},
    "FIXA11.SA":{"nome": "DI FUTURO", "mult": -1.0, "peso": 0.35},
    "EWZ":     {"nome": "EWZ",       "mult":  1.0, "peso": 0.05},
    "ES=F":    {"nome": "S&P500",    "mult":  1.0, "peso": 0.10},
    "NQ=F":    {"nome": "NASDAQ",    "mult":  1.0, "peso": 0.05},
}

def get_stats(cod):
    df = yf.download(cod, period="30d", interval="1d", progress=False)
    c = df['Close'].iloc[:, 0] if isinstance(df['Close'], pd.DataFrame) else df['Close']
    c = pd.to_numeric(c, errors='coerce').dropna()
    z = (float(c.iloc[-1]) - float(c.rolling(20).mean().iloc[-1])) / float(c.rolling(20).std().iloc[-1])
    return float(c.iloc[-1]), z

# Processamento
dados = []
for cod, config in vies_ativos.items():
    preco, z = get_stats(cod)
    forca_bruta = z * config['mult']
    forca_ponderada = forca_bruta * config['peso']
    # Lógica de correlação simples: Se Z do ativo e Z do IBOV estão em direções compatíveis com a correlação
    status = "🟢 Confirmando" if (z * config['mult']) > 0 else "🟡 Divergente"
    dados.append({
        "Ativo": config['nome'],
        "Preço": preco,
        "Forca": forca_bruta,
        "Contrib": abs(forca_ponderada),
        "Status": status
    })

df = pd.DataFrame(dados)
total_abs = df['Contrib'].sum()
df['Dominancia'] = (df['Contrib'] / total_abs) * 100

# Painel Superior
st.subheader("🎯 Viés para o WIN")
vies_total = (df['Forca'] * [v['peso'] for v in vies_ativos.values()]).sum()
if vies_total > 0.1: st.success(f"VIÉS ALTISTA (Força: {vies_total:.2f})")
elif vies_total < -0.1: st.error(f"VIÉS BAIXISTA (Força: {vies_total:.2f})")
else: st.info("MERCADO NEUTRO")

# Tabela Integrada de Dominância e Correlação
st.write("### 🏆 Ranking de Dominância & Correlação")
st.table(df[['Ativo', 'Dominancia', 'Status']].assign(Dominancia=df['Dominancia'].map('{:.1f}%'.format)))

# Carteira
st.write("### 💼 Minha Carteira")
carteira = {"B3SA3.SA": "B3SA3", "FIND11.SA": "IFNC", "MATB11.SA": "IMAT"}
df_cart = []
for cod, nome in carteira.items():
    p, z = get_stats(cod)
    df_cart.append({"Ativo": nome, "Preço": p, "Z-Score": round(z, 2)})
st.table(pd.DataFrame(df_cart))

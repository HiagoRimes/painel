import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="MACA-QUANTI", layout="centered")

st.title("🍎 MACA-QUANTI")
st.caption("Afastamento Estatístico (Média 20 períodos)")

macro_ativos = {
    "^BVSP": "IBOVESPA", "BRL=X": "DÓLAR", "FIXA11.SA": "JUROS",
    "MATB11.SA": "IMAT", "FIND11.SA": "IFNC", "B3SA3.SA": "B3SA3"
}

# Função para definir cor do container
def get_color(z):
    if z < -1.5: return "green"
    if z > 1.5: return "red"
    return "grey"

# Processamento
dados = []
for cod, nome in macro_ativos.items():
    try:
        df = yf.download(cod, period="60d", interval="1d", progress=False)
        fechamento = df['Close'].iloc[-1]
        z = (fechamento - df['Close'].rolling(20).mean().iloc[-1]) / df['Close'].rolling(20).std().iloc[-1]
        dados.append({"nome": nome, "z": z})
    except: continue

# Criando o painel em colunas (o máximo que o mobile permite sem quebrar)
cols = st.columns(2)

for i, item in enumerate(dados):
    with cols[i % 2]:
        color = get_color(item['z'])
        # Usamos os blocos nativos coloridos do Streamlit
        if color == "green":
            with st.container(border=True):
                st.success(f"{item['nome']}\n\nZ: {item['z']:.2f}")
        elif color == "red":
            with st.container(border=True):
                st.error(f"{item['nome']}\n\nZ: {item['z']:.2f}")
        else:
            with st.container(border=True):
                st.write(f"{item['nome']}\n\nZ: {item['z']:.2f}")

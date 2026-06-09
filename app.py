import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.set_page_config(page_title="MACA-QUANTI", layout="centered")
st.title("🍎 MACA-QUANTI")

# Dicionário de ativos
macro_ativos = {
    "^BVSP": "IBOVESPA", "BRL=X": "DÓLAR", "FIXA11.SA": "JUROS",
    "MATB11.SA": "IMAT", "FIND11.SA": "IFNC", "B3SA3.SA": "B3SA3"
}

dados_finais = []

# Processamento individualizado para evitar bloqueio do Yahoo
with st.spinner("Conectando e baixando dados..."):
    for cod, nome in macro_ativos.items():
        try:
            # Baixa um de cada vez
            df = yf.download(cod, period="60d", interval="1d", progress=False)
            if not df.empty:
                fechamento = float(df['Close'].iloc[-1])
                media = float(df['Close'].rolling(20).mean().iloc[-1])
                std = float(df['Close'].rolling(20).std().iloc[-1])
                z = (fechamento - media) / std
                
                sinal = "🔴 VENDA" if z > 1.5 else ("🟢 COMPRA" if z < -1.5 else "⚪ NEUTRO")
                dados_finais.append({"Ativo": nome, "Z": f"{z:.2f}", "Sinal": sinal})
            
            # Pausa de 0.5s para não sobrecarregar a conexão
            time.sleep(0.5)
        except Exception as e:
            st.error(f"Erro no ativo {nome}: {e}")

# Exibição
if dados_finais:
    st.table(pd.DataFrame(dados_finais))
else:
    st.warning("Nenhum dado foi baixado. Verifique os Logs do Streamlit (botão 'Manage app' -> 'Logs').")

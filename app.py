import streamlit as st
import google.generativeai as genai
import requests
from datetime import datetime

# Configuração da Página
st.set_page_config(page_title="Mentor Institucional WIN", layout="wide")

# --- SENHA E CONFIG ---
SENHA_ACESSO = "aprender"
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# --- FUNÇÃO DE BUSCA ROBUSTA ---
def buscar_dados_mercado():
    token = "T95TARf3vRa3adDmBwCJAZ"
    # Sua grade de estudo completa
    tickers = ["WIN1!", "WDO1!", "DI1F27", "PETR4", "VALE3", "B3SA3", "ES1!", "NQ1!", "VIX"]
    resultados = []
    
    for ticker in tickers:
        try:
            # Tenta buscar na Brapi
            url = f"https://brapi.dev/api/quote/{ticker}?token={token}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'results' in data and len(data['results']) > 0:
                    res = data['results'][0]
                    preco = res.get('regularMarketPrice', 0)
                    var = res.get('regularMarketChangePercent', 0)
                    resultados.append(f"{ticker}: R${preco:.2f} ({var:.2f}%)")
        except:
            pass # Ignora erros de ativos específicos para não parar a análise
    return "\n".join(resultados) if resultados else "Dados momentaneamente indisponíveis."

# --- INTERFACE ---
password = st.text_input("🔑 Digite a senha para liberar seu estudo:", type="password")

if password == SENHA_ACESSO:
    st.title("🎓 Mentor Institucional: Análise de Correlação")
    
    if st.button("🚀 Processar Análise de Correlação"):
        with st.spinner("Mesa de operações em conexão..."):
            dados = buscar_dados_mercado()
            
            prompt = f"""
            Você é um Estrategista de Mesa e Mestre em Educação Financeira.
            Analise os dados abaixo focando estritamente na CORRELAÇÃO entre eles:
            
            DADOS DE MERCADO:
            {dados}
            
            REGRAS DE ANÁLISE:
            1. WIN é consequência. Explique a correlação com WDO, DI e ativos globais (ES1!, NQ1!).
            2. Fluxo real sempre vence. Identifique pressões vendedoras ou compradoras nos ativos de peso.
            3. Como o VIX e os juros (DI) estão influenciando o apetite ao risco brasileiro?
            4. Seja didático. O usuário estuda correlação, então conecte os pontos.
            """
            
            try:
                response = model.generate_content(prompt)
                st.markdown("### 📊 Relatório Institucional")
                st.write(response.text)
            except Exception as e:
                st.error(f"Erro na IA: {e}")
elif password != "":
    st.error("Senha incorreta.")
        

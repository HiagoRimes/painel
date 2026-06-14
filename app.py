import streamlit as st
import google.generativeai as genai
import requests
import pandas as pd
import time

# Configuração da Página
st.set_page_config(page_title="Mentor Institucional", layout="wide")

# --- CONFIGURAÇÃO ---
SENHA_ACESSO = "aprender"
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

def get_model():
    """Retorna o modelo de IA disponível."""
    return genai.GenerativeModel('gemini-pro')

# Sua grade completa de estudo
TICKERS = ["WIN1!", "WDO1!", "DI1N2029", "PETR4", "IMAT", "IFNC", "ES1!", "NQ1!", "B3SA3", "EWZ", "VIX"]

def buscar_dados():
    token = "T95TARf3vRa3adDmBwCJAZ"
    dados = []
    
    for ticker in TICKERS:
        # Tenta a busca com um pequeno delay para respeitar o limite da API
        url = f"https://brapi.dev/api/quote/{ticker}?token={token}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'results' in data and len(data['results']) > 0:
                    res = data['results'][0]
                    dados.append({
                        "Ativo": ticker, 
                        "Preço": res.get('regularMarketPrice', 0), 
                        "Var (%)": res.get('regularMarketChangePercent', 0)
                    })
            # Delay de 0.5s para não disparar o bloqueio de spam da API
            time.sleep(0.5) 
        except:
            continue
    return pd.DataFrame(dados)

# --- INTERFACE ---
password = st.text_input("🔑 Digite a senha:", type="password")

if password == SENHA_ACESSO:
    st.title("🎓 Mentor Institucional: Análise Sistêmica")
    
    if st.button("🚀 Processar Análise"):
        with st.spinner("Conectando à grade completa..."):
            df = buscar_dados()
            
            if not df.empty:
                st.table(df)
                
                # Análise da IA
                model = get_model()
                prompt = f"""
                Você é um Estrategista de Mesa. Analise a correlação entre estes ativos:
                {df.to_string(index=False)}
                
                Instruções:
                1. WIN1! e WDO1! são a ponta da lança. Relacione-os com DI, ativos globais (ES1!, NQ1!, VIX) e o fluxo dos setores (IMAT, IFNC).
                2. Use os dados da tabela para justificar a correlação.
                3. Seja direto e profissional, como um head de mesa de operações.
                """
                
                try:
                    response = model.generate_content(prompt)
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Erro na IA: {e}")
            else:
                st.error("Falha ao carregar ativos. Verifique sua conexão.")
                

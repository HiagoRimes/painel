import streamlit as st
import google.generativeai as genai
import requests
import pandas as pd
from datetime import datetime

# Configuração da Página
st.set_page_config(page_title="Mentor Institucional WIN", layout="wide")

# --- SENHA E CONFIG ---
SENHA_ACESSO = "aprender"
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

def get_best_model():
    try:
        models = genai.list_models()
        for m in models:
            if 'generateContent' in m.supported_generation_methods:
                return genai.GenerativeModel(m.name)
        return None
    except: return None

# --- FUNÇÃO DE BUSCA PARA TABELA ---
def buscar_dados_para_tabela():
    token = "T95TARf3vRa3adDmBwCJAZ"
    tickers = ["WIN1!", "WDO1!", "DI1F27", "PETR4", "VALE3", "B3SA3", "ES1!", "NQ1!", "VIX"]
    dados_formatados = []
    
    for ticker in tickers:
        try:
            url = f"https://brapi.dev/api/quote/{ticker}?token={token}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'results' in data and len(data['results']) > 0:
                    res = data['results'][0]
                    dados_formatados.append({
                        "Ativo": ticker,
                        "Preço (R$)": res.get('regularMarketPrice', 0),
                        "Variação (%)": res.get('regularMarketChangePercent', 0)
                    })
        except: continue
    return pd.DataFrame(dados_formatados)

# --- INTERFACE ---
password = st.text_input("🔑 Digite a senha para liberar seu estudo:", type="password")

if password == SENHA_ACESSO:
    st.title("🎓 Mentor Institucional: Análise de Correlação")
    
    if st.button("🚀 Processar Análise de Correlação"):
        model = get_best_model()
        
        if model is None:
            st.error("Erro ao conectar com a IA.")
        else:
            with st.spinner("Mesa de operações em conexão..."):
                df = buscar_dados_para_tabela()
                
                # --- EXIBIÇÃO DA TABELA ---
                st.markdown("### 📋 Painel de Monitoramento")
                st.table(df)
                
                # --- ANÁLISE IA ---
                dados_texto = df.to_string(index=False)
                prompt = f"""
                Você é um Estrategista de Mesa. Analise os dados abaixo focando na correlação:
                {dados_texto}
                
                Instruções:
                1. O WIN é consequência. Relacione com WDO, DI e ativos globais.
                2. Identifique fluxos e pressões.
                3. Seja didático e profissional.
                """
                
                try:
                    response = model.generate_content(prompt)
                    st.markdown("### 📊 Relatório Institucional")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Erro ao gerar conteúdo: {e}")
elif password != "":
    st.error("Senha incorreta.")
        

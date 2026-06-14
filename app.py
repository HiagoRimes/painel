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

# --- FUNÇÃO DE BUSCA DE TODOS OS ATIVOS ---
def buscar_dados_completos():
    token = "T95TARf3vRa3adDmBwCJAZ"
    # Grade completa original
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
                else:
                    # Adiciona mesmo sem dado para manter a consistência da tabela
                    dados_formatados.append({"Ativo": ticker, "Preço (R$)": "N/D", "Variação (%)": "N/D"})
        except:
            dados_formatados.append({"Ativo": ticker, "Preço (R$)": "Erro", "Variação (%)": "Erro"})
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
                df = buscar_dados_completos()
                
                # --- EXIBIÇÃO DA TABELA ---
                st.markdown("### 📋 Painel de Monitoramento (Carteira Completa)")
                st.table(df)
                
                # --- ANÁLISE IA ---
                dados_texto = df.to_string(index=False)
                prompt = f"""
                Você é um Estrategista de Mesa e Mestre em Educação Financeira. 
                Analise esta carteira completa focando na correlação entre os ativos:
                {dados_texto}
                
                Instruções:
                1. Analise como os índices futuros (WIN/WDO) reagem à dinâmica dos juros (DI) e ativos globais (ES1!/VIX).
                2. Fluxo real sempre vence: observe os pesos de PETR4, VALE3 e B3SA3.
                3. Conecte os pontos: como o cenário macro afeta o Índice?
                4. Seja didático, direto e profissional.
                """
                
                try:
                    response = model.generate_content(prompt)
                    st.markdown("### 📊 Relatório Institucional")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Erro ao gerar relatório: {e}")
elif password != "":
    st.error("Senha incorreta.")
                

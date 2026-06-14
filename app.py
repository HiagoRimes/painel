import streamlit as st
import google.generativeai as genai
import requests
import pandas as pd

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

# --- FUNÇÃO DE BUSCA PARA A SUA GRADE EXATA ---
def buscar_dados_da_grade():
    token = "T95TARf3vRa3adDmBwCJAZ"
    # Lista extraída exatamente do seu print
    tickers = ["WIN1!", "WDO1!", "DI1N2029", "PETR4", "IMAT", "IFNC", "ES1!", "NQ1!", "B3SA3", "EWZ", "VIX"]
    dados = []
    
    for ticker in tickers:
        try:
            url = f"https://brapi.dev/api/quote/{ticker}?token={token}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'results' in data and len(data['results']) > 0:
                    res = data['results'][0]
                    dados.append({
                        "Ativo": ticker,
                        "Preço": res.get('regularMarketPrice', 0),
                        "Var (%)": res.get('regularMarketChangePercent', 0)
                    })
        except:
            continue
    return pd.DataFrame(dados)

# --- INTERFACE ---
password = st.text_input("🔑 Digite a senha:", type="password")

if password == SENHA_ACESSO:
    st.title("🎓 Mentor Institucional: Visão Sistêmica")
    
    if st.button("🚀 Processar Análise de Correlação"):
        df = buscar_dados_da_grade()
        
        if df.empty:
            st.error("Erro ao carregar dados da grade. Verifique a conexão com a API.")
        else:
            # 1. Exibe a tabela completa
            st.markdown("### 📋 Painel de Monitoramento")
            st.table(df)
            
            # 2. Processa com a IA
            model = get_best_model()
            prompt = f"""
            Você é um Estrategista de Mesa de Operações. 
            Analise os dados abaixo focando na CORRELAÇÃO total da minha grade:
            {df.to_string(index=False)}
            
            REGRAS PARA A ANÁLISE:
            1. WIN (WIN1!) é consequência. Explique a correlação com WDO1!, DI1N2029 e os índices globais (ES1!, NQ1!).
            2. Fluxo Real: Como a variação dos pesos (PETR4, IMAT, IFNC, B3SA3) está impactando o índice?
            3. Risco Global: Como o VIX e os futuros americanos (ES1!, NQ1!) estão ditando o tom do pregão?
            4. Seja direto, técnico e didático. Conecte os pontos da minha grade de estudo.
            """
            
            with st.spinner("Analisando correlações..."):
                try:
                    response = model.generate_content(prompt)
                    st.markdown("### 📊 Relatório de Correlação")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Erro na IA: {e}")
                    

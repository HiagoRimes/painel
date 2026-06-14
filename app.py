import streamlit as st
import google.generativeai as genai
import requests
from datetime import datetime

# Configuração da Página
st.set_page_config(page_title="Mentor Institucional WIN", layout="wide")

# --- SENHA E CONFIG ---
SENHA_ACESSO = "aprender"
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

def get_best_model():
    """Lista modelos disponíveis e retorna o primeiro válido."""
    try:
        # Lista todos os modelos disponíveis na sua conta
        models = genai.list_models()
        for m in models:
            # Filtra por modelos que podem gerar conteúdo
            if 'generateContent' in m.supported_generation_methods:
                return genai.GenerativeModel(m.name)
        return None
    except Exception as e:
        st.error(f"Erro ao listar modelos: {e}")
        return None

# --- FUNÇÃO DE BUSCA ROBUSTA ---
def buscar_dados_mercado():
    token = "T95TARf3vRa3adDmBwCJAZ"
    tickers = ["WIN1!", "WDO1!", "DI1F27", "PETR4", "VALE3", "B3SA3", "ES1!", "NQ1!", "VIX"]
    resultados = []
    
    for ticker in tickers:
        try:
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
            pass
    return "\n".join(resultados)

# --- INTERFACE ---
password = st.text_input("🔑 Digite a senha para liberar seu estudo:", type="password")

if password == SENHA_ACESSO:
    st.title("🎓 Mentor Institucional: Análise de Correlação")
    
    if st.button("🚀 Processar Análise de Correlação"):
        model = get_best_model() # Busca o modelo disponível na hora do clique
        
        if model is None:
            st.error("Não foi possível encontrar um modelo de IA disponível na sua API Key.")
        else:
            with st.spinner("Mesa de operações em conexão..."):
                dados = buscar_dados_mercado()
                
                prompt = f"""
                Você é um Estrategista de Mesa. Analise a correlação entre estes ativos:
                {dados}
                
                Instruções:
                1. WIN é consequência. Relacione com WDO, DI e ativos globais (ES1!).
                2. Fluxo real vence. Analise pressão compradora/vendedora.
                3. Como VIX e DI afetam o apetite ao risco?
                4. Seja didático e profissional.
                """
                
                try:
                    response = model.generate_content(prompt)
                    st.markdown("### 📊 Relatório Institucional")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Erro ao gerar conteúdo: {e}")
elif password != "":
    st.error("Senha incorreta.")
                

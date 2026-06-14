import streamlit as st
import google.generativeai as genai
import requests
from datetime import datetime

# Configuração da Página
st.set_page_config(page_title="Mentor Institucional WIN", layout="wide")

# --- SENHA E CONFIG ---
SENHA_ACESSO = "aprender"
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

def get_model():
    """Busca o modelo disponível e evita o erro 404."""
    try:
        # Tenta listar os modelos para ver o que está disponível na sua conta
        models = genai.list_models()
        for m in models:
            if 'gemini-1.5' in m.name and 'generateContent' in m.supported_generation_methods:
                return genai.GenerativeModel(m.name)
        # Se não achar o 1.5, tenta o 'gemini-pro' padrão
        return genai.GenerativeModel('gemini-pro')
    except Exception as e:
        st.error(f"Erro ao listar modelos: {e}")
        return None

model = get_model()

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
        if model is None:
            st.error("Não foi possível conectar ao modelo de IA. Verifique sua chave.")
        else:
            with st.spinner("Mesa de operações em conexão..."):
                dados = buscar_dados_mercado()
                
                prompt = f"""
                Você é um Estrategista de Mesa. Analise a correlação entre estes ativos:
                {dados}
                
                Instruções:
                1. O WIN é consequência do fluxo e dos ativos correlacionados.
                2. Relacione o comportamento do WDO, DI, S&P500 (ES1!) e VIX com o mercado brasileiro.
                3. Seja didático. O usuário estuda correlação. Conecte os pontos.
                """
                
                try:
                    response = model.generate_content(prompt)
                    st.markdown("### 📊 Relatório Institucional")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Erro ao gerar conteúdo: {e}")
elif password != "":
    st.error("Senha incorreta.")
        

import streamlit as st
import google.generativeai as genai
import requests
from datetime import datetime

# Configuração da Página
st.set_page_config(page_title="Mentor Institucional WIN", layout="wide")

# --- SENHA DE ACESSO ---
SENHA_ACESSO = "aprender" 

# --- CONFIGURAÇÃO API GOOGLE ---
# Colocamos fora da condicional de senha para carregar uma vez só na inicialização
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Erro ao inicializar o modelo: {e}")
    model = None

# --- FUNÇÃO DE BUSCA DE DADOS (APENAS PETR4 E VALE3) ---
def buscar_dados_mercado():
    token = "T95TARf3vRa3adDmBwCJAZ"
    ativos = ["PETR4", "VALE3"]
    resultados = []
    
    for ticker in ativos:
        try:
            url = f"https://brapi.dev/api/quote/{ticker}?token={token}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'results' in data and len(data['results']) > 0:
                    res = data['results'][0]
                    preco = res.get('regularMarketPrice', 0)
                    var = res.get('regularMarketChangePercent', 0)
                    resultados.append(f"{ticker}: R${preco:.2f} (Variação: {var:.2f}%)")
            else:
                resultados.append(f"{ticker}: Dado indisponível na API")
        except:
            resultados.append(f"{ticker}: Erro de conexão")
    return "\n".join(resultados)

# --- INTERFACE E LÓGICA ---
password = st.text_input("🔑 Digite a senha para liberar seu estudo:", type="password")

if password == SENHA_ACESSO:
    st.title("🎓 Mentor Institucional (Foco: PETR4/VALE3)")
    
    if st.button("🚀 Processar Análise Institucional"):
        if model is None:
            st.error("Erro na conexão com a IA. Verifique sua chave API.")
        else:
            with st.spinner("Conectando variáveis de mercado..."):
                dados = buscar_dados_mercado()
                
                prompt = f"""
                Você é um Estrategista de Mesa de Operações. 
                Analise estes dados de mercado em tempo real:
                {dados}
                
                REGRAS: 
                - O foco da análise deve ser exclusivamente em PETR4 e VALE3.
                - Ignore a ausência de outros ativos.
                - Forneça um parecer técnico e institucional para um Mestre em Educação Financeira.
                - Seja direto, didático e profissional.
                """
                
                try:
                    # Execução direta da análise
                    response = model.generate_content(prompt)
                    st.markdown("### 📊 Relatório Institucional")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Erro no processamento da IA: {e}")
elif password != "":
    st.error("Senha incorreta.")
                    

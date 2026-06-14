import streamlit as st
import google.generativeai as genai
import requests
import pandas as pd
import time

st.set_page_config(page_title="Mentor Institucional", layout="wide")

SENHA_ACESSO = "aprender"
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

def get_model():
    return genai.GenerativeModel('gemini-pro')

# Lista completa da sua grade (11 ativos)
TICKERS_GRADE = ["WIN1!", "WDO1!", "DI1N2029", "PETR4", "IMAT", "IFNC", "ES1!", "NQ1!", "B3SA3", "EWZ", "VIX"]

def buscar_dados_completos():
    token = "T95TARf3vRa3adDmBwCJAZ"
    dados = []
    
    for ticker in TICKERS_GRADE:
        url = f"https://brapi.dev/api/quote/{ticker}?token={token}"
        try:
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
                else:
                    dados.append({"Ativo": ticker, "Preço": "N/D", "Var (%)": "N/D"})
            else:
                dados.append({"Ativo": ticker, "Preço": "Erro API", "Var (%)": "Erro"})
        except:
            dados.append({"Ativo": ticker, "Preço": "Falha", "Var (%)": "Falha"})
        
        # Pausa estratégica para não estourar o limite de requisições por segundo
        time.sleep(0.3) 
        
    return pd.DataFrame(dados)

password = st.text_input("🔑 Digite a senha:", type="password")

if password == SENHA_ACESSO:
    st.title("🎓 Mentor Institucional: Visão Sistêmica Total")
    
    if st.button("🚀 Processar Análise de Correlação Completa"):
        with st.spinner("Executando varredura da grade..."):
            df = buscar_dados_completos()
            st.table(df)
            
            model = get_model()
            # Forçamos a IA a considerar a grade completa na análise
            prompt = f"""
            Você é um Estrategista de Mesa. Analise a correlação da GRADE COMPLETA:
            {df.to_string(index=False)}
            
            Sua missão:
            1. Considere a correlação entre todos os 11 ativos listados.
            2. Se algum ativo estiver como 'N/D' ou 'Erro', desconsidere-o na conta, mas mantenha a análise macro com os ativos que carregaram.
            3. Explique a dinâmica entre o fluxo de PETR4/B3SA3/IFNC e o comportamento do WIN1!.
            4. Relacione o impacto do mercado externo (ES1!, NQ1!, VIX, EWZ) no DI1N2029 e consequentemente no WDO1!.
            """
            
            try:
                response = model.generate_content(prompt)
                st.write(response.text)
            except Exception as e:
                st.error("Erro ao gerar a análise. Tente novamente.")
                    

import streamlit as st
import pandas as pd
import google.generativeai as genai
import json

# Configuração da Página
st.set_page_config(page_title="Bolão da Seleção", page_icon="⚽")

# Configuração Direta da API do Gemini (Chave de Teste)
CHAVE_GEMINI = "AQ.Ab8RN6IN0k72vZ9vO2NgOe6Z9yJg16eP9euOkpT8uhXhSyvYUw"

# Função para buscar os próximos 2 jogos do Brasil via Gemini
@st.cache_data(ttl=3600)
def buscar_jogos_gemini():
    try:
        genai.configure(api_key=CHAVE_GEMINI)
        model = genai.GenerativeModel(model_name='models/gemini-1.5-flash')
        
        prompt = (
            "Escreva os próximos 2 jogos oficiais que a Seleção Brasileira de Futebol Masculino vai disputar. "
            "Responda estritamente em um formato de array JSON válido, com objetos contendo 'confronto' e 'data'. "
            "Exemplo: [{'confronto': 'Brasil x Haiti', 'data': '19/06/2026'}]"
        )
        response = model.generate_content(prompt)
        texto = response.text.strip()
        if texto.startswith("
http://googleusercontent.com/immersive_entry_chip/0
http://googleusercontent.com/immersive_entry_chip/1

### O que vai acontecer agora:
Assim que você subir esse código, o aviso vermelho de erro vai sumir. O app vai detectar que a chave não tem a permissão correta e vai abrir duas caixinhas limpas para você e sua namorada digitarem o jogo que quiserem na hora (como *"Brasil x Haiti"*). O bolão vai funcionar perfeitamente para todo mundo apostar contra todo mundo!

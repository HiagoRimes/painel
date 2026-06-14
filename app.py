import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configuração da Página
st.set_page_config(page_title="Mentor Vision: Análise por Print", layout="wide")

# --- CONFIGURAÇÃO ---
SENHA_ACESSO = "aprender"
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

def get_vision_model():
    # Usamos o modelo 'gemini-1.5-flash' que é excelente para visão e muito rápido
    return genai.GenerativeModel('gemini-1.5-flash')

# --- INTERFACE ---
st.title("🎓 Mentor Vision: Análise Sistêmica por Print")
password = st.text_input("🔑 Digite a senha:", type="password")

if password == SENHA_ACESSO:
    st.markdown("### 📸 Suba o print da sua tela do TradingView")
    uploaded_file = st.file_uploader("Escolha o print...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Grade de ativos carregada', use_column_width=True)
        
        if st.button("🚀 Processar Análise Estratégica"):
            with st.spinner("Lendo a grade e processando correlações..."):
                model = get_vision_model()
                prompt = """
                Analise esta imagem que é um print de uma tela de cotações da bolsa.
                1. Extraia os nomes dos ativos, seus preços e suas variações.
                2. Realize uma análise de correlação sistêmica entre eles.
                3. Foque especialmente em como o fluxo real (PETR4, VALE3, B3SA3, etc.) impacta os futuros (WIN/WDO) e como o cenário global (ES1, NQ1, VIX) dita o sentimento.
                4. Seja técnico, direto e profissional, como um Estrategista de Mesa.
                """
                
                try:
                    response = model.generate_content([prompt, image])
                    st.markdown("### 📊 Relatório Estratégico")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Erro na leitura da imagem: {e}")

import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configuração da página
st.set_page_config(page_title="Mentor Institucional WIN", layout="wide")

# Configuração da API 
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    
    # Usando o modelo moderno da sua lista que sabemos que funciona
    model_name = 'gemini-3.5-flash' 
    model = genai.GenerativeModel(model_name)
except Exception as e:
    st.error("Configuração de API pendente nas Secrets do Streamlit Cloud.")
    st.stop()

# Seu Protocolo consolidado
PROTOCOL_FINAL = """
Você é um mentor de trading institucional de alta performance. Seu papel é analisar prints do TradingView do ativo WIN e ensinar o aluno a pensar como um profissional. Siga rigorosamente este protocolo:

1. CONTEXTO DO DIA: Eventos e notícias.
2. ESTADO DOS MOTORES: Macro (DI/WDO), Externo (S&P/Nasdaq/VIX), Interno (IFNC/IMAT).
3. CARTEIRA: Análise dos ativos correlacionados.
4. TRANSMISSÃO DE FLUXO: Mecanismo dominante.
5. ESTADO FINAL DO MERCADO: Direção provável e decisão operacional.
6. MODO PROFESSOR: Erro típico, padrão de aprendizado e regra prática.
"""

st.title("🎓 Mentor de Fluxo WIN")

uploaded_file = st.file_uploader("Suba o print do TradingView...", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, width='stretch')
    
    if st.button("Executar Protocolo de Leitura"):
        with st.spinner(f"Analisando fluxo com o modelo {model_name}..."):
            try:
                # Prompt combinado para o formato da biblioteca antiga
                prompt = f"{PROTOCOL_FINAL}\n\nAnalise a imagem acima seguindo rigorosamente este protocolo."
                
                # Resposta enviando os parâmetros na ordem aceita pela biblioteca
                response = model.generate_content([prompt, img])
                
                st.markdown("---")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"Erro na análise: {e}")

import streamlit as st
from google import genai
from PIL import Image

# Configuração da página
st.set_page_config(page_title="Mentor Institucional WIN", layout="wide")

# Configuração da NOVA API do Google (google.genai)
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    client = genai.Client(api_key=api_key)
    # Voltamos ao modelo super rápido e inteligente para imagens
    model_name = 'gemini-1.5-flash' 
except Exception as e:
    st.error("Configuração de API pendente. Vá em Settings > Secrets no seu app do Streamlit Cloud e adicione a GOOGLE_API_KEY.")
    st.stop()

# Seu Protocolo
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
    
    # Comando de imagem corrigido conforme os logs do Streamlit
    st.image(img, width='stretch')
    
    if st.button("Executar Protocolo de Leitura"):
        with st.spinner("Analisando fluxo com o novo sistema Google..."):
            try:
                prompt = f"{PROTOCOL_FINAL}\n\nAnalise a imagem acima seguindo rigorosamente este protocolo."
                
                # Chamada com a nova sintaxe exigida pelo Google
                response = client.models.generate_content(
                    model=model_name,
                    contents=[img, prompt]
                )
                
                st.markdown("---")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"Erro na análise: {e}")

st.sidebar.markdown("---")
st.sidebar.info("Sistema atualizado e rodando na nova SDK oficial do Google.")

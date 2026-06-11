import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configuração da página
st.set_page_config(page_title="Mentor Institucional WIN", layout="wide")

# Configuração da API via Streamlit Secrets
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    
    # --- ALTERAÇÃO AQUI: Mudando para o modelo 'gemini-pro-vision' ---
    model_name = 'gemini-pro-vision' # Modelo robusto para imagens
    model = genai.GenerativeModel(model_name)
    # ---------------------------------------------------------------
    
except Exception as e:
    st.error("Configuração de API pendente ou inválida. Vá em Settings > Secrets no seu app do Streamlit Cloud e adicione a GOOGLE_API_KEY.")
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
    st.image(img, use_container_width=True)
    
    if st.button("Executar Protocolo de Leitura"):
        with st.spinner(f"Analisando fluxo com o modelo {model_name}..."):
            try:
                # Prompt combinado
                prompt = f"{PROTOCOL_FINAL}\n\nAnalise a imagem acima seguindo rigorosamente este protocolo."
                
                # Chamada do Gemini com tratamento de erros robusto
                response = model.generate_content([prompt, img])
                st.markdown("---")
                st.markdown(response.text)
                
            except Exception as e:
                # Se o modelo falhar, mostramos o erro e uma dica
                st.error(f"Erro ao analisar com o modelo {model_name}: {e}")
                st.warning("Dica: Se o erro for 'NotFound', o modelo pode não estar disponível na região. Tente usar um print com resolução menor.")

# Sidebar com uma ferramenta de diagnóstico
st.sidebar.markdown("---")
if st.sidebar.button("Diagnóstico: Listar Modelos"):
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        st.sidebar.write("### Modelos disponíveis para sua chave:")
        for m in available_models:
            st.sidebar.code(m.replace("models/", ""))
    except Exception as api_err:
        st.sidebar.error(f"Não foi possível listar os modelos. Verifique sua chave da API. Erro: {api_err}")

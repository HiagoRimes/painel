import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configuração da página
st.set_page_config(page_title="Mentor Institucional WIN", layout="wide")

# Inicializa a "Memória Intraday" do aplicativo
if 'historico_analises' not in st.session_state:
    st.session_state.historico_analises = []

# Configuração da API
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    model_name = 'gemini-3.5-flash' 
    model = genai.GenerativeModel(model_name)
except Exception as e:
    st.error("Configuração de API pendente nas Secrets.")
    st.stop()

# Seu Protocolo Base
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

# Botão na barra lateral para limpar a memória ao iniciar um novo dia
st.sidebar.markdown("### 🧠 Gestão de Memória")
if st.sidebar.button("🗑️ Limpar Memória (Novo Dia de Pregão)"):
    st.session_state.historico_analises = []
    st.sidebar.success("Memória zerada! O Mentor está pronto para um novo dia.")

uploaded_file = st.file_uploader("Suba o print do TradingView...", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, width='stretch')
    
    if st.button("Executar Protocolo de Leitura"):
        with st.spinner(f"Analisando fluxo e consultando memória..."):
            try:
                # 1. Verifica se já existem análises anteriores hoje para criar o contexto
                contexto_intraday = ""
                if len(st.session_state.historico_analises) > 0:
                    contexto_intraday = "HISTÓRICO DAS SUAS ANÁLISES ANTERIORES HOJE:\n"
                    # Pega apenas as últimas 3 análises para não sobrecarregar o texto
                    ultimas_analises = st.session_state.historico_analises[-3:]
                    for i, analise in enumerate(ultimas_analises):
                        contexto_intraday += f"--- Leitura Anterior {i+1} ---\n{analise}\n\n"
                    
                    contexto_intraday += "INSTRUÇÃO ADICIONAL: Com base no histórico acima e na nova imagem, aponte o desenrolar do mercado. A sua tese anterior se confirmou? O fluxo mudou? O que o mercado está provando agora?\n\n"

                # 2. Junta o Protocolo + Memória + Imagem Nova
                prompt_completo = f"{PROTOCOL_FINAL}\n\n{contexto_intraday}Analise a imagem atual seguindo o protocolo e atualizando a leitura."
                
                # 3. Chama a IA
                response = model.generate_content([prompt_completo, img])
                
                # 4. Salva a nova resposta na memória do aplicativo
                st.session_state.historico_analises.append(response.text)
                
                # 5. Exibe o resultado
                st.markdown("---")
                st.markdown("### 📊 Análise Atualizada")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"Erro na análise: {e}")

# Exibe um menu sanfona com as análises anteriores do dia
if len(st.session_state.historico_analises) > 0:
    st.markdown("---")
    with st.expander("📜 Ver Leituras Anteriores do Dia"):
        for i, analise in enumerate(st.session_state.historico_analises):
            st.markdown(f"**Análise {i+1}**")
            st.markdown(analise)
            st.markdown("---")

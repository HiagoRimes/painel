import streamlit as st
import google.generativeai as genai
import requests # Biblioteca padrão para fazer chamadas de API

# Configuração da página
st.set_page_config(page_title="Mentor Institucional WIN", layout="wide")

# Inicializa a memória
if 'historico_analises' not in st.session_state:
    st.session_state.historico_analises = []

# Configuração do Gemini
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    model_name = 'gemini-3.5-flash' 
    model = genai.GenerativeModel(model_name)
except Exception as e:
    st.error("Configuração de API pendente nas Secrets.")
    st.stop()

# Seu Protocolo Base adaptado para leitura de dados em texto
PROTOCOL_FINAL = """
Você é um mentor de trading institucional de alta performance focado no ativo WIN.
Vou te passar os DADOS DA MINHA CARTEIRA e os INDICADORES ATUAIS. Siga rigorosamente este protocolo:

1. CONTEXTO DA CARTEIRA: Analise a posição atual, saldo e exposição.
2. ESTADO DOS MOTORES: Macro, Externo e Interno (com base nos dados fornecidos).
3. TRANSMISSÃO DE FLUXO: Mecanismo dominante.
4. ESTADO FINAL DO MERCADO: Direção provável e decisão operacional.
5. MODO PROFESSOR: Erro típico, padrão de aprendizado e regra prática.
"""

st.title("🎓 Mentor de Fluxo WIN (Modo Dados)")

# --- ÁREA DE NOTÍCIAS MANUAIS ---
st.markdown("### 📰 Contexto Macroeconômico do Dia")
noticias_do_dia = st.text_area(
    "Insira a agenda e notícias relevantes (Ex: 09:30 - Payroll):", 
    height=68
)
st.markdown("---")

# --- ÁREA DA API DA CARTEIRA ---
st.markdown("### 💼 Sincronização de Carteira")

# Função simulada onde a sua API real vai entrar
def puxar_dados_api():
    # Aqui vai entrar o código real da sua corretora/plataforma
    # Por enquanto, retorna um dado simulado para você testar a mecânica
    return """
    Ativo: WINQ26
    Posição: Comprado em 5 minicontratos
    Preço Médio: 125.400
    Resultado Aberto: + R$ 150,00
    IFNC: +0.45% | DI1F27: -0.12% | WDO: -0.20%
    """

if st.button("🔄 Puxar Dados e Analisar"):
    if not noticias_do_dia.strip():
        st.warning("⚠️ Preencha o Contexto Macroeconômico antes de analisar.")
    else:
        with st.spinner("Sincronizando com a API e analisando fluxo..."):
            try:
                # 1. Puxa os dados da API
                dados_atuais = puxar_dados_api()
                
                # 2. Mostra os dados crus na tela para conferência
                st.info(f"**Dados capturados:**\n{dados_atuais}")

                # 3. Monta o contexto com o histórico
                contexto_intraday = ""
                if len(st.session_state.historico_analises) > 0:
                    contexto_intraday = "HISTÓRICO DAS ANÁLISES HOJE:\n"
                    for i, analise in enumerate(st.session_state.historico_analises[-3:]):
                        contexto_intraday += f"--- Leitura Anterior {i+1} ---\n{analise}\n\n"
                    contexto_intraday += "INSTRUÇÃO: Com base nas leituras anteriores e nos NOVOS DADOS DA CARTEIRA abaixo, atualize a tese. O fluxo mudou?\n\n"

                # 4. Junta tudo no prompt (Notícias + Protocolo + Histórico + Dados da API)
                prompt_completo = f"NOTÍCIAS HOJE:\n{noticias_do_dia}\n\n{PROTOCOL_FINAL}\n\n{contexto_intraday}\n\nDADOS REAIS DA API AGORA:\n{dados_atuais}"
                
                # 5. Chama o Gemini apenas com texto (sem imagem)
                response = model.generate_content(prompt_completo)
                
                # 6. Salva e exibe
                st.session_state.historico_analises.append(response.text)
                
                st.markdown("### 📊 Análise Institucional Atualizada")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"Erro na conexão/análise: {e}")

# Gestão de Memória
st.sidebar.markdown("### 🧠 Gestão de Memória")
if st.sidebar.button("🗑️ Limpar Memória (Novo Dia)"):
    st.session_state.historico_analises = []
    st.sidebar.success("Memória zerada!")

if len(st.session_state.historico_analises) > 0:
    st.sidebar.markdown("---")
    with st.sidebar.expander("📜 Ver Leituras Anteriores"):
        for i, analise in enumerate(st.session_state.historico_analises):
            st.markdown(f"**Análise {i+1}**")
            st.markdown(analise)
            st.markdown("---")
            

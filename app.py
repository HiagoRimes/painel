import streamlit as st
import pandas as pd
import google.generativeai as genai
import json

# Configuração da Página
st.set_page_config(page_title="Bolão da Seleção", page_icon="⚽")

# Configuração segura da API do Gemini via Secrets do Streamlit
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Função para buscar os próximos 2 jogos do Brasil via Gemini
@st.cache_data(ttl=3600)  # Guarda o resultado por 1 hora para economizar API
def buscar_jogos_gemini():
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (
            "Liste os próximos 2 jogos da Seleção Brasileira de Futebol Masculina. "
            "Responda estritamente em um array JSON com objetos contendo 'confronto' e 'data'. "
            "Exemplo: [{'confronto': 'Brasil x Haiti', 'data': '19/06/2026'}, {'confronto': 'Brasil x Chile', 'data': '25/06/2026'}]"
        )
        response = model.generate_content(prompt)
        
        # Limpa as tags de markdown se o Gemini enviar
        texto = response.text.strip()
        if texto.startswith("```json"):
            texto = texto[7:]
        if texto.endswith("```"):
            texto = texto[:-3]
        texto = texto.strip()
        
        return json.loads(texto)
    except Exception as e:
        st.error(f"Erro ao chamar o Gemini: {e}")
        return []

# Inicializa o 'banco de dados' temporário na memória do servidor
if "boloes" not in st.session_state:
    st.session_state.boloes = {}

st.title("⚽ Bolão da Seleção Brasileira")

# Criação das Abas do Aplicativo
aba_apostar, aba_criar, aba_resultados = st.tabs([
    "🏆 Apostar em um Bolão", 
    "🛠️ Criar Novo Bolão", 
    "📊 Ver Apostas & Baixar"
])

# --- ABA 1: APOSTAR ---
with aba_apostar:
    st.header("Faça sua Aposta")
    
    if st.session_state.boloes:
        # Lista todos os bolões criados (o seu, o da sua namorada, etc.)
        lista_boloes = list(st.session_state.boloes.keys())
        bolao_selecionado = st.selectbox("Escolha o bolão para entrar:", lista_boloes)
        
        dados_bolao = st.session_state.boloes[bolao_selecionado]
        st.info(f"Jogo deste bolão: **{dados_bolao['jogo']}**")
        
        # Formulário de Palpite
        with st.form("form_aposta"):
            nome_apostador = st.text_input("Seu Nome:")
            col1, col2 = st.columns(2)
            with col1:
                placar_br = st.number_input("Brasil", min_value=0, step=1, value=0)
            with col2:
                placar_rival = st.number_input("Adversário", min_value=0, step=1, value=0)
                
            enviar_aposta = st.form_submit_button("Confirmar Palpite")
            
            if enviar_aposta:
                if nome_apostador.strip() == "":
                    st.error("Por favor, digite seu nome antes de apostar!")
                else:
                    nova_aposta = {
                        "Nome": nome_apostador,
                        "Placar": f"{placar_br} x {placar_rival}"
                    }
                    st.session_state.boloes[bolao_selecionado]["apostas"].append(nova_aposta)
                    st.success(f"Aposta registrada com sucesso no grupo: {bolao_selecionado}!")
    else:
        st.warning("Nenhum bolão ativo. Vá na aba 'Criar Novo Bolão' para começar!")

# --- ABA 2: CRIAR NOVO BOLÃO ---
with aba_criar:
    st.header("Criar um Grupo de Apostas")
    
    nome_criador = st.text_input("Nome do Criador (ex: Bolão do Thiago, Bolão da Gabi):")
    
    st.subheader("Buscar Partidas Disponíveis")
    jogos_disponiveis = buscar_jogos_gemini()
    
    if jogos_disponiveis:
        # Formata as opções vinda do Gemini para o seletor do Streamlit
        opcoes_jogos = [f"{j['confronto']} ({j['data']})" for j in jogos_disponiveis]
        jogo_escolhido = st.selectbox("Selecione qual jogo o Gemini encontrou para o seu bolão:", opcoes_jogos)
        
        if st.button("Criar Meu Bolão"):
            if nome_criador.strip() == "":
                st.error("Por favor, digite um nome para identificar seu bolão!")
            elif nome_criador in st.session_state.boloes:
                st.error("Já existe um bolão com esse nome ativo.")
            else:
                st.session_state.boloes[nome_criador] = {
                    "jogo": jogo_escolhido,
                    "apostas": []
                }
                st.success(f"Pronto! O '{nome_criador}' foi criado para o jogo {jogo_escolhido}. Seus amigos já podem apostar nele na Aba 1.")
    else:
        st.error("O Gemini não conseguiu listar jogos no momento. Verifique seus Logs ou Chave de API.")

# --- ABA 3: RESULTADOS E DOWNLOAD DOC ---
with aba_resultados:
    st.header("Resumo e Download")
    
    if st.session_state.boloes:
        bolao_resumo = st.selectbox("Escolha o bolão para ver os palpites:", list(st.session_state.boloes.keys()), key="resumo_select")
        apostas_atuais = st.session_state.boloes[bolao_resumo]["apostas"]
        st.write(f"Jogo: {st.session_state.boloes[bolao_resumo]['jogo']}")
        
        if apostas_atuais:
            df = pd.DataFrame(apostas_atuais)
            st.dataframe(df, use_container_width=True)
            
            # Converte a tabela para CSV para que eles possam baixar o documento
            csv = df.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="📥 Baixar Documento de Apostas (CSV)",
                data=csv,
                file_name=f"apostas_{bolao_resumo.lower().replace(' ', '_')}.csv",
                mime="text/csv",
            )
        else:
            st.info("Ninguém deixou palpites nesse grupo ainda.")
    else:
        st.warning("Nenhum bolão ativo para gerar relatórios.")
        

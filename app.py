import streamlit as st
import pandas as pd
# import google.generativeai as genai  # Para quando integrar o Gemini

st.set_page_config(page_title="Bolão da Seleção", page_icon="⚽")
st.title("⚽ Bolão da Seleção Brasileira")

# --- SIMULAÇÃO DE BANCO DE DADOS (Substituir por Banco Real/Sheets depois) ---
if "boloes" not in st.session_state:
    st.session_state.boloes = {
        "Bolão do Dono": {
            "jogo": "Brasil x Argentina",
            "data": "25/06/2026",
            "apostas": [
                {"Nome": "Thiago", "Placar Brasil": 2, "Placar Rival": 1}
            ]
        }
    }

# --- INTEGRAÇÃO SIMULADA DO GEMINI ---
def buscar_proximo_jogo_gemini():
    # Aqui entraria sua lógica da API do Gemini
    # Exemplo de retorno:
    return "Brasil x Uruguai", "05/07/2026"

# --- ESTRUTURA DE ABAS ---
aba_apostar, aba_criar, aba_resultados = st.tabs([
    "🏆 Apostar em um Bolão", 
    "🛠️ Criar Novo Bolão", 
    "📊 Ver Apostas & Baixar"
])

# --- ABA 1: APOSTAR ---
with aba_apostar:
    st.header("Faça sua Aposta")
    
    if st.session_state.boloes:
        # Selecionar qual bolão quer participar
        lista_boloes = list(st.session_state.boloes.keys())
        bolao_selecionado = st.selectbox("Escolha o bolão do seu amigo:", lista_boloes)
        
        dados_bolao = st.session_state.boloes[bolao_selecionado]
        st.info(f"Jogo: **{dados_bolao['jogo']}** | Data: {dados_bolao['data']}")
        
        # Formulário de Aposta
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
                    st.error("Por favor, digite seu nome.")
                else:
                    nova_aposta = {
                        "Nome": nome_apostador,
                        "Placar Brasil": placar_br,
                        "Placar Rival": placar_rival
                    }
                    st.session_state.boloes[bolao_selecionado]["apostas"].append(nova_aposta)
                    st.success(f"Aposta de {nome_apostador} salva com sucesso no {bolao_selecionado}!")
    else:
        st.warning("Nenhum bolão criado ainda. Vá na aba 'Criar Novo Bolão'!")

# --- ABA 2: CRIAR BOLÃO ---
with aba_criar:
    st.header("Criar um Novo Grupo de Apostas")
    
    nome_novo_bolao = st.text_input("Nome do seu Bolão (ex: Bolão da Gabi, Galera do Trabalho):")
    
    # Chamada do Gemini para preencher o jogo automaticamente
    st.subheader("Dados do Próximo Jogo (Via Gemini)")
    jogo_automatico, data_automatica = buscar_proximo_jogo_gemini()
    
    jogo = st.text_input("Confronto:", value=jogo_automatico)
    data_jogo = st.text_input("Data do Jogo:", value=data_automatica)
    
    if st.button("Criar Bolão"):
        if nome_novo_bolao.strip() == "":
            st.error("Dê um nome para o seu bolão!")
        elif nome_novo_bolao in st.session_state.boloes:
            st.error("Já existe um bolão com esse nome.")
        else:
            st.session_state.boloes[nome_novo_bolao] = {
                "jogo": jogo,
                "data": data_jogo,
                "apostas": []
            }
            st.success(f"Bolão '{nome_novo_bolao}' criado! Agora seus amigos já podem apostar nele.")

# --- ABA 3: RESULTADOS E DOWNLOAD ---
with aba_resultados:
    st.header("Resumo das Apostas")
    
    if st.session_state.boloes:
        bolao_resumo = st.selectbox("Visualizar apostas do:", list(st.session_state.boloes.keys()), key="resumo_select")
        apostas_atuais = st.session_state.boloes[bolao_resumo]["apostas"]
        
        if apostas_atuais:
            df = pd.DataFrame(apostas_atuais)
            st.dataframe(df, use_container_width=True)
            
            # Função para transformar o DataFrame em CSV para download
            @st.cache_data
            def converter_df(dataframe):
                return dataframe.to_csv(index=False).encode('utf-8')
                
            csv = converter_df(df)
            
            st.download_button(
                label="📥 Baixar PDF/Doc de Apostas (Formato CSV)",
                data=csv,
                file_name=f"apostas_{bolao_resumo.lower().replace(' ', '_')}.csv",
                mime="text/csv",
            )
        else:
            st.info("Ninguém apostou neste bolão ainda.")
    else:
        st.warning("Nenhum dado disponível.")
        

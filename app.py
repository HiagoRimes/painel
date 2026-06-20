        return json.loads(texto.strip())
    except Exception as e:
        # Retorna uma lista vazia se a chave der erro 401/tipo inválido
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
        lista_boloes = list(st.session_state.boloes.keys())
        bolao_selecionado = st.selectbox("Escolha o bolão para entrar:", lista_boloes)
        
        dados_bolao = st.session_state.boloes[bolao_selecionado]
        st.info(f"Jogo deste bolão: **{dados_bolao['jogo']}**")
        
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
                        "Palpite": f"{placar_br} x {placar_rival}"
                    }
                    st.session_state.boloes[bolao_selecionado]["apostas"].append(nova_aposta)
                    st.success(f"Aposta registrada com sucesso no grupo: {bolao_selecionado}!")
    else:
        st.warning("Nenhum bolão ativo. Vá na aba 'Criar Novo Bolão' para começar!")

# --- ABA 2: CRIAR NOVO BOLÃO ---
with aba_criar:
    st.header("Criar um Grupo de Apostas")
    
    nome_criador = st.text_input("Nome do Criador (ex: Bolão do Thiago, Bolão da Gabi):")
    
    st.subheader("Configurar Partida do Bolão")
    jogos_disponiveis = buscar_jogos_gemini()
    
    # Se a API funcionar, mostra o selectbox automático
    if jogos_disponiveis:
        opcoes_jogos = [f"{j['confronto']} ({j['data']})" for j in jogos_disponiveis]
        jogo_final = st.selectbox("Selecione o jogo encontrado pelo Gemini:", opcoes_jogos)
    else:
        # Se a chave der erro de credencial, ele libera os campos manuais para salvar seu jogo!
        st.warning("⚠️ Nota: Chave de API indisponível. Digite os dados do jogo manualmente abaixo:")
        confronto_manual = st.text_input("Confronto (ex: Brasil x Haiti):", "Brasil x Haiti")
        data_manual = st.text_input("Data do Jogo (ex: Hoje):", "19/06/2026")
        jogo_final = f"{confronto_manual} ({data_manual})"
        
    if st.button("Criar Meu Bolão"):
        if nome_criador.strip() == "":
            st.error("Por favor, digite um nome para identificar seu bolão!")
        elif nome_criador in st.session_state.boloes:
            st.error("Já existe um bolão com esse nome ativo.")
        else:
            st.session_state.boloes[nome_criador] = {
                "jogo": jogo_final,
                "apostas": []
            }
            st.success(f"Pronto! O '{nome_criador}' foi criado para o jogo {jogo_final}. Você e seus amigos já podem apostar nele na Aba 1.")

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

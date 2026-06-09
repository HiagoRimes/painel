# ... (Manter todo o código anterior de processamento) ...

# 4. Legendas e Guia de Leitura (Rodapé)
st.write("---")
st.write("### 📖 Guia de Leitura e Legendas")

with st.expander("📌 Legenda de Status de Correlação"):
    st.info("""
    - **🟢 Conf (Confirmando):** O ativo está agindo conforme o esperado para a ponta do WIN (ex: Dólar cai, WIN sobe). **Ajuda o movimento.**
    - **🟡 Div (Divergente):** O ativo está indeciso ou não segue a correlação clássica. **Sinal de alerta/cautela.**
    - **🔴 Quebra (Estrutural):** O ativo empurra o WIN contra a sua natureza (ex: Dólar sobe e WIN sobe). **Indica mudança de fluxo ou exaustão.**
    """)

with st.expander("📈 Como ler o nosso gráfico de Dominância"):
    st.write("""
    Nosso gráfico de **Hierarquia de Drivers** funciona como um 'mapa de calor' do fluxo institucional:
    
    1. **Driver Primário:** É o ativo que, neste exato momento, detém o maior poder de puxar o preço do Mini Índice (WIN).
    2. **Dominância (%):** Indica o peso real de influência. Se o Dólar tem 30% de dominância, ele é responsável por quase 1/3 da força motriz do índice agora.
    3. **Convicção:** Mede a 'energia' por trás do movimento. Quanto maior, mais provável que o movimento tenha continuidade.
    4. **Score WIN:** Um valor de -100 a +100 que resume o impacto. Acima de 0 pressiona para a alta, abaixo de 0 pressiona para a queda.
    
    **Regra de Ouro:** Se o *Driver Primário* estiver com status **🔴 Quebra**, ignore as demais correlações e prepare-se para uma possível reversão no WIN.
    """)

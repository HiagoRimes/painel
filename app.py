import streamlit as st
import google.generativeai as genai
import json

# Configuração da Página
st.set_page_config(page_title="Bolão da Seleção", page_icon="⚽")

# Configuração da API (Certifique-se de configurar em Secrets)
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Função para buscar os próximos 2 jogos via Gemini
@st.cache_data(ttl=3600) # Cache por 1 hora
def buscar_jogos_gemini():
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = (
        "Liste os próximos 2 jogos da Seleção Brasileira de Futebol. "
        "Responda estritamente em um array JSON com objetos contendo 'confronto' e 'data'. "
        "Exemplo: [{'confronto': 'Brasil x Haiti', 'data': '19/06/2026'}, {'confronto': 'Brasil x Chile', 'data': '25/06/2026'}]"
    )
    response = model.generate_content(prompt)
    try:
        texto = response.text.replace("```json", "").replace("
```", "").strip()
        return json.loads(texto)
    except:
        return []

# Inicializa o estado (Simulação de banco)
if "apostas" not in st.session_state:
    st.session_state.apostas = []

st.title("⚽ Bolão da Seleção")

aba1, aba2 = st.tabs(["🏆 Apostar", "🛠️ Gerenciar Bolão"])

with aba2:
    st.header("Selecionar Jogo do Bolão")
    jogos = buscar_jogos_gemini()
    
    if jogos:
        jogo_escolhido = st.selectbox("Escolha qual jogo será o foco do bolão:", 
                                     options=[f"{j['confronto']} ({j['data']})" for j in jogos])
        st.session_state.jogo_ativo = jogo_escolhido
        st.success(f"Bolão configurado para: {jogo_escolhido}")
    else:
        st.error("Não foi possível carregar os jogos. Verifique a API.")

with aba1:
    st.header("Faça sua Aposta")
    if "jogo_ativo" in st.session_state:
        st.info(f"Bolão atual: **{st.session_state.jogo_ativo}**")
        
        with st.form("aposta_form"):
            nome = st.text_input("Seu nome:")
            col1, col2 = st.columns(2)
            gols_brasil = col1.number_input("Brasil", min_value=0, step=1)
            gols_rival = col2.number_input("Adversário", min_value=0, step=1)
            
            if st.form_submit_button("Confirmar Palpite"):
                st.session_state.apostas.append({
                    "Nome": nome, 
                    "Jogo": st.session_state.jogo_ativo,
                    "Palpite": f"{gols_brasil}x{gols_rival}"
                })
                st.success("Aposta registrada!")
    else:
        st.warning("Vá na aba 'Gerenciar Bolão' e selecione um jogo primeiro.")

    if st.session_state.apostas:
        st.divider()
        st.subheader("Lista de Apostas")
        st.table(st.session_state.apostas)

import streamlit as st
import pandas as pd
import google.generativeai as genai
import requests
import json
from datetime import datetime

# --- CONFIGURAÇÃO VISUAL PREMIUM DA PÁGINA ---
st.set_page_config(
    page_title="Bolão Seleção Brasileira ⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS personalizada nas cores do Brasil (Verde e Amarelo)
st.markdown("""
    <style>
    .main {
        background-color: #f7f9fa;
    }
    h1, h2, h3 {
        color: #009c3b !important;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .stButton>button {
        background-color: #009c3b;
        color: white !important;
        border-radius: 8px;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #ffdf00;
        color: #002776 !important;
    }
    .status-box {
        padding: 15px;
        border-radius: 8px;
        background-color: #e6f4ea;
        border-left: 5px solid #009c3b;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONFIGURAÇÃO DA API (ESTRUTURA DO SEU CÓDIGO DE ESTUDO) ---
if "GOOGLE_API_KEY" in st.secrets:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    try:
        genai.configure(api_key=API_KEY)
        api_configurada = True
    except Exception as e:
        st.error(f"Erro ao configurar a API do Google: {e}")
        api_configurada = False
else:
    api_configurada = False

# Método de resolução dinâmica do modelo igual ao seu código de estudo
def get_model():
    if not api_configurada:
        return None
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        prioridade = ['models/gemini-2.5-flash-lite', 'models/gemini-1.5-flash', 'models/gemini-1.5-pro']
        for p in prioridade:
            if p in models: 
                return genai.GenerativeModel(p)
        return genai.GenerativeModel(models[0])
    except Exception:
        return genai.GenerativeModel('models/gemini-1.5-flash')

if api_configurada:
    model = get_model()
else:
    model = None

# --- BANCO DE DADOS EM NUVEM COMPARTILHADO (JSONBLOB) ---
DATABASE_URL = "https://jsonblob.com/api/jsonBlob/1319022513903362048"

def carregar_banco_dados():
    try:
        response = requests.get(DATABASE_URL, timeout=8)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    
    if "boloes_backup" not in st.session_state:
        st.session_state.boloes_backup = {}
    return st.session_state.boloes_backup

def salvar_banco_dados(novos_dados):
    st.session_state.boloes_backup = novos_dados
    try:
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        requests.put(DATABASE_URL, json=novos_dados, headers=headers, timeout=8)
    except Exception as e:
        st.sidebar.warning(f"Erro de sincronização: {e}")

# --- BANCO DE JOGOS REAIS ATUALIZADO (A partir de hoje, 19/06/2026) ---
def obter_jogos_reais_selecao():
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    
    # Calendário Real de Próximos Compromissos Oficiais (Apenas Hoje e Datas Futuras de 2026)
    jogos_reais = [
        {"confronto": "Brasil x Haiti", "data": data_hoje},
        {"confronto": "Equador x Brasil", "data": "04/09/2026"},
        {"confronto": "Brasil x Colômbia", "data": "10/09/2026"},
        {"confronto": "Paraguai x Brasil", "data": "15/10/2026"},
        {"confronto": "Brasil x Argentina", "data": "20/10/2026"}
    ]
    return jogos_reais

# --- INTEGRANDO GEMINI PARA DAR DICAS DE PLACAR ---
@st.cache_data(ttl=600)
def obter_analise_confrontos(confronto):
    if not model:
        return "Espera-se um grande jogo para hoje!"
    try:
        prompt = (
            f"Como um especialista em futebol, dê uma dica extremamente rápida de uma frase (até 15 palavras) "
            f"sobre o que esperar do confronto histórico ou equilíbrio de forças para o jogo: {confronto}."
        )
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception:
        return "Espera-se um jogo muito disputado e com forte pressão ofensiva!"

# --- LÓGICA PRINCIPAL DO APLICATIVO ---
dados_bolao = carregar_banco_dados()

st.markdown("<h1 style='text-align: center; margin-bottom: 5px;'>⚽ Bolão dos Amigos da Seleção</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666; margin-bottom: 30px;'>Crie o seu grupo de palpites, convide a galera e guarde o ficheiro de resultados!</p>", unsafe_allow_html=True)

# Abas do aplicativo
tab_jogar, tab_criar, tab_classificacao = st.tabs([
    "🏆 Entrar & Apostar", 
    "🛠️ Criar Novo Bolão", 
    "📊 Ver Palpites & Download"
])

# --- ABA 1: FAZER PALPITE ---
with tab_jogar:
    st.markdown("### 📝 Registrar o seu Palpite")
    
    if dados_bolao:
        lista_grupos = list(dados_bolao.keys())
        grupo_chosen = st.selectbox("Selecione de quem é o bolão em que quer entrar:", lista_grupos)
        
        detalhes_grupo = dados_bolao[grupo_chosen]
        
        st.markdown(f"""
        <div class='status-box'>
            <strong>📌 Bolão Selecionado:</strong> {grupo_chosen}<br>
            <strong>⚽ Confronto:</strong> {detalhes_grupo['jogo']}
        </div>
        """, unsafe_allow_html=True)
        
        # Exibe análise do Gemini se estiver configurado
        if api_configurada:
            analise = obter_analise_confrontos(detalhes_grupo['jogo'])
            st.caption(f"💡 *Análise rápida do Gemini:* {analise}")
            
        with st.form("form_novo_palpite"):
            nome_participante = st.text_input("O seu Nome ou Alcunha:")
            
            col_gols_br, col_gols_op = st.columns(2)
            gols_brasil = col_gols_br.number_input("Gols do Brasil:", min_value=0, max_value=20, value=0, step=1)
            gols_oponente = col_gols_op.number_input("Gols do Adversário:", min_value=0, max_value=20, value=0, step=1)
            
            btn_salvar_palpite = st.form_submit_button("Confirmar Palpite")
            
            if btn_salvar_palpite:
                if nome_participante.strip() == "":
                    st.error("⚠️ Digite o seu nome para guardar a aposta!")
                else:
                    novo_palpite = {
                        "Nome": nome_participante.strip(),
                        "Palpite": f"{gols_brasil} x {gols_oponente}",
                        "Data Registro": datetime.now().strftime("%d/%m/%Y %H:%M")
                    }
                    
                    lista_apostas = detalhes_grupo["apostas"]
                    detalhes_grupo["apostas"] = [
                        a for a in lista_apostas if a["Nome"].lower() != nome_participante.strip().lower()
                    ]
                    detalhes_grupo["apostas"].append(novo_palpite)
                    
                    salvar_banco_dados(dados_bolao)
                    st.success(f"🎉 Palpite registado com sucesso! Boa sorte, {nome_participante}!")
                    st.rerun()
    else:
        st.warning("Nenhum bolão ativo na nuvem neste momento. Vá ao separador 'Criar Novo Bolão' para inaugurar a rodada!")

# --- ABA 2: CRIAR NOVO BOLÃO ---
with tab_criar:
    st.markdown("### 🛠️ Configurar um Novo Grupo")
    st.write("Crie uma sala nova personalizada. Os seus amigos poderão selecionar o seu nome na aba de apostas!")
    
    nome_lider = st.text_input("Quem está a criar este bolão? (Ex: Bolão do Thiago, Bolão da Gabi):")
    
    st.markdown("#### 📅 Próximos Confrontos Reais do Brasil")
    
    # Obtém os dados reais do futebol brasileiro estruturados de hoje em diante
    jogos_reais_selecionados = obter_jogos_reais_selecao()
    opcoes_partidas = [f"{partida['confronto']} ({partida['data']})" for partida in jogos_reais_selecionados]
    
    escolha_partida = st.selectbox("Selecione qual partida será disputada no seu bolão:", opcoes_partidas)
    
    st.markdown("##### ✏️ Ajuste ou Confirme os detalhes do jogo abaixo:")
    
    # Processamento para permitir ajuste rápido dos campos
    try:
        partes = escolha_partida.split(" (")
        confronto_sugerido = partes[0]
        data_sugerida = partes[1].replace(")", "")
    except Exception:
        confronto_sugerido = escolha_partida
        data_sugerida = datetime.now().strftime("%d/%m/%Y")
        
    col_edit_1, col_edit_2 = st.columns(2)
    confronto_final_nome = col_edit_1.text_input("Confronto (Pode alterar o adversário se desejar):", value=confronto_sugerido)
    confronto_final_data = col_edit_2.text_input("Data do Jogo:", value=data_sugerida)
    confronto_final = f"{confronto_final_nome} ({confronto_final_data})"
        
    if st.button("🚀 Inicializar Meu Bolão"):
        if nome_lider.strip() == "":
            st.error("⚠️ Dê um nome de identificação para o seu grupo (ex: Bolão da Gabi).")
        elif nome_lider.strip() in dados_bolao:
            st.error("❌ Já existe um bolão ativo com esse nome. Escolha outro nome de grupo!")
        else:
            dados_bolao[nome_lider.strip()] = {
                "jogo": confronto_final,
                "apostas": []
            }
            salvar_banco_dados(dados_bolao)
            st.success(f"✅ Bolão '{nome_lider}' criado com sucesso para o jogo {confronto_final}!")
            st.rerun()

# --- ABA 3: CLASSIFICAÇÃO & DOWNLOAD ---
with tab_classificacao:
    st.markdown("### 📊 Palpites Registados")
    
    if dados_bolao:
        grupo_resumo = st.selectbox("Selecione o grupo para auditar:", list(dados_bolao.keys()), key="select_filtro_resumo")
        dados_do_grupo = dados_bolao[grupo_resumo]
        
        st.write(f"**Partida Selecionada:** {dados_do_grupo['jogo']}")
        st.write(f"**Apostadores Ativos:** {len(dados_do_grupo['apostas'])}")
        
        if dados_do_grupo["apostas"]:
            df_palpites = pd.DataFrame(dados_do_grupo["apostas"])
            df_palpites = df_palpites[["Nome", "Palpite", "Data Registro"]]
            st.dataframe(df_palpites, use_container_width=True)
            
            csv_bytes = df_palpites.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="📥 Baixar Documento de Apostas (Excel / CSV)",
                data=csv_bytes,
                file_name=f"bolao_{grupo_resumo.lower().replace(' ', '_')}.csv",
                mime="text/csv",
            )
        else:
            st.info("Nenhum palpite registado nesta sala ainda. Seja o primeiro a apostar!")
    else:
        st.warning("Nenhum bolão ativo registado no sistema.")

# --- BARRA LATERAL ---
st.sidebar.markdown("### ⚙️ Informações da API")
if api_configurada and model:
    st.sidebar.write(f"**Modelo Ativo:** {model.model_name}")
    st.sidebar.success("Conectado com o Gemini")
else:
    st.sidebar.warning("API inativa (modo manual ativo)")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🗑️ Zona de Limpeza")
if st.sidebar.button("Limpar Todos os Bolões (Zerar Sistema)"):
    salvar_banco_dados({})
    st.sidebar.success("Sistema zerado com sucesso!")
    st.rerun()

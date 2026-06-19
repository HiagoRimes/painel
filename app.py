import streamlit as st
import pandas as pd
import google.generativeai as genai
import requests
import json
from datetime import datetime
from fpdf import FPDF

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
    /* Estilização para fazer o st.radio de navegação parecer abas elegantes */
    div[data-testid="stHorizontalBlock"] {
        background-color: #f0f2f6;
        padding: 8px;
        border-radius: 10px;
        margin-bottom: 20px;
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

def get_model():
    if not api_configurada:
        return None
    try:
        return genai.GenerativeModel(
            model_name='models/gemini-1.5-flash',
            tools='google_search_retrieval'
        )
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

# --- GERADOR DE RELATÓRIO EM PDF ---
def gerar_pdf_bolao(nome_grupo, confronto, apostas):
    pdf = FPDF()
    pdf.add_page()
    
    # Configurações de página e fontes padrão Helvetica
    pdf.set_text_color(0, 156, 59) # Verde Seleção
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 15, "BOLAO DA SELECAO BRASILEIRA", ln=True, align="C")
    
    pdf.set_text_color(0, 39, 118) # Azul Cruzeiro
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, f"Grupo de Apostas: {nome_grupo}", ln=True, align="C")
    
    pdf.set_text_color(50, 50, 50)
    pdf.set_font("Helvetica", "I", 11)
    pdf.cell(0, 8, f"Confronto: {confronto}", ln=True, align="C")
    pdf.cell(0, 8, f"Relatorio gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="C")
    pdf.ln(10)
    
    # Cabeçalho da Tabela
    pdf.set_fill_color(0, 156, 59) # Verde de Fundo
    pdf.set_text_color(255, 255, 255) # Texto Branco
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(80, 10, " Nome do Apostador", border=1, fill=True)
    pdf.cell(40, 10, " Palpite", border=1, fill=True, align="C")
    pdf.cell(60, 10, " Data/Hora Registro", border=1, fill=True, align="C")
    pdf.ln()
    
    # Linhas de Apostas
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 10)
    
    color_toggle = False
    for aposta in apostas:
        if color_toggle:
            pdf.set_fill_color(240, 248, 240) # Alternar cor de fundo suave
        else:
            pdf.set_fill_color(255, 255, 255)
            
        # Normaliza textos para evitar quebra de codificação no PDF
        nome = aposta.get("Nome", "").encode('latin-1', 'replace').decode('latin-1')
        palpite = aposta.get("Palpite", "").encode('latin-1', 'replace').decode('latin-1')
        data_reg = aposta.get("Data Registro", "").encode('latin-1', 'replace').decode('latin-1')
        
        pdf.cell(80, 10, f" {nome}", border=1, fill=True)
        pdf.cell(40, 10, f" {palpite}", border=1, fill=True, align="C")
        pdf.cell(60, 10, f" {data_reg}", border=1, fill=True, align="C")
        pdf.ln()
        color_toggle = not color_toggle
        
    return pdf.output()

# --- CHAMADA DO GEMINI COM BUSCA EM TEMPO REAL (LIMITADO A 15 DIAS) ---
@st.cache_data(ttl=1800)
def puxar_proximos_jogos():
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    
    # Calendário Real de Segurança de 2026 (Estritamente os próximos 15 dias da Copa do Mundo)
    fallback_jogos = [
        {"confronto": "Brasil x Haiti", "data": "19/06/2026"},
        {"confronto": "Brasil x Escócia", "data": "24/06/2026"}
    ]
    
    if not model:
        return fallback_jogos
        
    try:
        prompt = (
            f"Hoje é dia {data_hoje} (junho de 2026). Faça uma pesquisa no Google e traga os jogos reais oficiais "
            f"da Seleção Brasileira Masculina de Futebol na Copa do Mundo de 2026 agendados para os próximos 15 dias (de {data_hoje} até 04/07/2026). "
            f"Ignore totalmente jogos de Eliminatórias de setembro ou outubro. Foque apenas em partidas reais da Copa de 2026 nesse intervalo de 15 dias, "
            f"como o jogo de hoje contra o Haiti (19/06/2026) e o jogo contra a Escócia (24/06/2026). "
            f"Responda estritamente em formato JSON no padrão: "
            f"[{'confronto': 'Brasil x Adversario', 'data': 'DD/MM/2026'}] "
            f"Não adicione nenhuma outra palavra, cabeçalho ou bloco markdown."
        )
        response = model.generate_content(prompt)
        texto = response.text.strip()
        
        if texto.startswith("```json"):
            texto = texto[7:]
        if texto.endswith("```"):
            texto = texto[:-3]
        texto = texto.strip()
        
        resultado = json.loads(texto)
        if isinstance(resultado, list) and len(resultado) > 0:
            jogos_filtrados = []
            for jogo in resultado:
                try:
                    data_jogo = datetime.strptime(jogo['data'], "%d/%m/%Y")
                    dias_diferenca = (data_jogo - datetime.now()).days
                    if 0 <= dias_diferenca <= 15:
                        jogos_filtrados.append(jogo)
                except Exception:
                    if "2026" in jogo['data'] and not any(m in jogo['data'] for m in ["09", "10", "11"]):
                        jogos_filtrados.append(jogo)
            
            if jogos_filtrados:
                return jogos_filtrados
        return fallback_jogos
    except Exception:
        return fallback_jogos

# --- GERENCIAMENTO DE ESTADO E NAVEGAÇÃO ---
# Inicializa o controle de abas no Session State
if "aba_ativa" not in st.session_state:
    st.session_state.aba_ativa = "🏆 Entrar & Apostar"

if "grupo_selecionado_padrao" not in st.session_state:
    st.session_state.grupo_selecionado_padrao = None

def mudar_aba(nome_aba, grupo_foco=None):
    st.session_state.aba_ativa = nome_aba
    if grupo_foco:
        st.session_state.grupo_selecionado_padrao = grupo_foco
    st.rerun()

# --- CARREGA DADOS DO BANCO ---
dados_bolao = carregar_banco_dados()

st.markdown("<h1 style='text-align: center; margin-bottom: 5px;'>⚽ Bolão dos Amigos da Seleção</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666; margin-bottom: 25px;'>Crie o seu grupo de palpites, convide a galera e guarde o PDF de resultados!</p>", unsafe_allow_html=True)

# Barra de Navegação Horizontal Dinâmica usando st.columns e st.button para simular abas controláveis
col_nav1, col_nav2, col_nav3 = st.columns(3)

with col_nav1:
    if st.button("🏆 Entrar & Apostar", use_container_width=True, type="secondary" if st.session_state.aba_ativa != "🏆 Entrar & Apostar" else "primary"):
        mudar_aba("🏆 Entrar & Apostar")
with col_nav2:
    if st.button("🛠️ Criar Novo Bolão", use_container_width=True, type="secondary" if st.session_state.aba_ativa != "🛠️ Criar Novo Bolão" else "primary"):
        mudar_aba("🛠️ Criar Novo Bolão")
with col_nav3:
    if st.button("📊 Ver Palpites & Download", use_container_width=True, type="secondary" if st.session_state.aba_ativa != "📊 Ver Palpites & Download" else "primary"):
        mudar_aba("📊 Ver Palpites & Download")

st.markdown("---")

# --- EXECUÇÃO CONFORME A ABA ATIVA ---

# --- ABA 1: FAZER PALPITE ---
if st.session_state.aba_ativa == "🏆 Entrar & Apostar":
    st.markdown("### 📝 Registrar o seu Palpite")
    
    if dados_bolao:
        lista_grupos = list(dados_bolao.keys())
        
        # Define qual grupo exibir primeiro (útil após redirecionamento de nova criação)
        indice_padrao = 0
        if st.session_state.grupo_selecionado_padrao in lista_grupos:
            indice_padrao = lista_grupos.index(st.session_state.grupo_selecionado_padrao)
            
        grupo_chosen = st.selectbox("Selecione de quem é o bolão em que quer entrar:", lista_grupos, index=indice_padrao)
        
        # Limpa o foco temporário após seleção
        st.session_state.grupo_selecionado_padrao = grupo_chosen
        
        detalhes_grupo = dados_bolao[grupo_chosen]
        
        st.markdown(f"""
        <div class='status-box'>
            <strong>📌 Bolão Selecionado:</strong> {grupo_chosen}<br>
            <strong>⚽ Confronto:</strong> {detalhes_grupo['jogo']}
        </div>
        """, unsafe_allow_html=True)
        
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
                    st.success(f"🎉 Palpite registrado com sucesso! Redirecionando para classificação...")
                    
                    # Redireciona na hora para a aba de resultados
                    mudar_aba("📊 Ver Palpites & Download", grupo_foco=grupo_chosen)
    else:
        st.warning("Nenhum bolão ativo na nuvem neste momento. Vá para a aba 'Criar Novo Bolão' para inaugurar a rodada!")

# --- ABA 2: CRIAR NOVO BOLÃO ---
elif st.session_state.aba_ativa == "🛠️ Criar Novo Bolão":
    st.markdown("### 🛠️ Configurar um Novo Grupo")
    st.write("Crie uma sala nova personalizada para disputar com os seus amigos.")
    
    nome_lider = st.text_input("Quem está a criar este bolão? (Ex: Bolão do Thiago, Bolão da Gabi):")
    
    st.markdown("#### 📅 Próximos Confrontos Reais Encontrados")
    
    jogos_reais_selecionados = puxar_proximos_jogos()
    opcoes_partidas = [f"{partida['confronto']} ({partida['data']})" for partida in jogos_reais_selecionados]
    
    escolha_partida = st.selectbox("Selecione qual partida será disputada no seu bolão:", opcoes_partidas)
        
    if st.button("🚀 Inicializar Meu Bolão"):
        if nome_lider.strip() == "":
            st.error("⚠️ Dê um nome de identificação para o seu grupo (ex: Bolão da Gabi).")
        elif nome_lider.strip() in dados_bolao:
            st.error("❌ Já existe um bolão ativo com esse nome. Escolha outro nome de grupo!")
        else:
            dados_bolao[nome_lider.strip()] = {
                "jogo": escolha_partida,
                "apostas": []
            }
            salvar_banco_dados(dados_bolao)
            st.success(f"✅ Bolão '{nome_lider}' criado com sucesso! Redirecionando para a área de palpites...")
            
            # Redireciona na hora para a aba de apostar, focando no bolão recém criado
            mudar_aba("🏆 Entrar & Apostar", grupo_foco=nome_lider.strip())

# --- ABA 3: CLASSIFICAÇÃO & DOWNLOAD ---
elif st.session_state.aba_ativa == "📊 Ver Palpites & Download":
    st.markdown("### 📊 Palpites Registados")
    
    if dados_bolao:
        lista_opcoes_resumo = list(dados_bolao.keys())
        
        # Mantém o bolão atual em exibição se houver um padrão selecionado
        indice_resumo = 0
        if st.session_state.grupo_selecionado_padrao in lista_opcoes_resumo:
            indice_resumo = lista_opcoes_resumo.index(st.session_state.grupo_selecionado_padrao)
            
        grupo_resumo = st.selectbox("Selecione o grupo para auditar:", lista_opcoes_resumo, index=indice_resumo)
        dados_do_grupo = dados_bolao[grupo_resumo]
        
        st.write(f"**Partida Selecionada:** {dados_do_grupo['jogo']}")
        st.write(f"**Apostadores Ativos:** {len(dados_do_grupo['apostas'])}")
        
        if dados_do_grupo["apostas"]:
            df_palpites = pd.DataFrame(dados_do_grupo["apostas"])
            df_palpites = df_palpites[["Nome", "Palpite", "Data Registro"]]
            st.dataframe(df_palpites, use_container_width=True)
            
            # --- GERAÇÃO E DOWNLOAD EM PDF ---
            try:
                pdf_bytes = gerar_pdf_bolao(grupo_resumo, dados_do_grupo['jogo'], dados_do_grupo['apostas'])
                
                st.download_button(
                    label="📥 Baixar PDF Oficial de Resultados",
                    data=bytes(pdf_bytes),
                    file_name=f"bolao_{grupo_resumo.lower().replace(' ', '_')}.pdf",
                    mime="application/pdf",
                )
            except Exception as e:
                st.error(f"Erro ao gerar relatório em PDF: {e}")
        else:
            st.info("Nenhum palpite registado nesta sala ainda. Seja o primeiro a apostar!")
    else:
        st.warning("Nenhum bolão ativo registado no sistema.")

# --- BARRA LATERAL ---
st.sidebar.markdown("### ⚙️ Informações da API")
if api_configurada and model:
    st.sidebar.write(f"**Modelo Ativo:** {model.model_name}")
    st.sidebar.success("Busca do Google Ativada")
else:
    st.sidebar.warning("API inativa (modo manual ativo)")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🗑️ Zona de Limpeza")
if st.sidebar.button("Limpar Todos os Bolões (Zerar Sistema)"):
    salvar_banco_dados({})
    st.sidebar.success("Sistema zerado com sucesso!")
    st.rerun()

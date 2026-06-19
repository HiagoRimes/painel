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
    initial_sidebar_state="collapsed"
)

# Estilização CSS refinada para os botões, pílulas e tabelas de resultados
st.markdown("""
    <style>
    [data-testid="collapsedControl"] {
        display: none;
    }
    .main {
        background-color: #f7f9fa;
    }
    h1, h2, h3 {
        color: #009c3b !important;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .status-box {
        padding: 15px;
        border-radius: 8px;
        background-color: #e6f4ea;
        border-left: 5px solid #009c3b;
        margin-bottom: 15px;
    }
    .stat-card {
        padding: 15px;
        border-radius: 8px;
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        text-align: center;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.05);
    }
    div[data-testid="stHorizontalBlock"] {
        background-color: #f0f2f6;
        padding: 8px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .stButton>button {
        border-radius: 8px !important;
        font-weight: bold !important;
        transition: 0.3s !important;
    }
    /* 1. Botões Secundários (NÃO SELECIONADOS - Cinza Claro) */
    .stButton>button[data-testid="stBaseButton-secondary"] {
        background-color: #f0f2f6 !important;
        color: #31333F !important;
        border: 1px solid #d3d3d3 !important;
    }
    .stButton>button[data-testid="stBaseButton-secondary"]:hover {
        background-color: #e0e2e6 !important;
        color: #002776 !important;
        border: 1px solid #002776 !important;
    }
    /* 2. Botões Primários (SELECIONADOS ATIVOS - Azul Royal) */
    .stButton>button[data-testid="stBaseButton-primary"] {
        background-color: #002776 !important;
        color: white !important;
        border: 2px solid #ffdf00 !important;
        box-shadow: 0px 4px 10px rgba(0, 39, 118, 0.3) !important;
    }
    .stButton>button[data-testid="stBaseButton-primary"]:hover {
        background-color: #001f5c !important;
        color: #ffdf00 !important;
    }
    /* 3. Botões de Enviar Formulário (Ação de Apostar - Verde) */
    .stFormSubmitButton>button {
        background-color: #009c3b !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        box-shadow: 0px 4px 10px rgba(0, 156, 59, 0.2) !important;
    }
    .stFormSubmitButton>button:hover {
        background-color: #ffdf00 !important;
        color: #002776 !important;
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
        st.toast(f"⚠️ Erro de sincronização: {e}")

# --- CALCULAR PONTUAÇÃO INDIVIDUALLY ---
def calcular_pontos(palpite, resultado_real):
    if not palpite or not resultado_real:
        return 0
    try:
        gols_palpite_br, gols_palpite_rival = map(int, palpite.split(" x "))
        gols_real_br, gols_real_rival = map(int, resultado_real.split(" x "))
        
        # 1. Acerto Exato do Placar (10 Pontos)
        if gols_palpite_br == gols_real_br and gols_palpite_rival == gols_real_rival:
            return 10
            
        # Determinação do vencedor/empate
        vencedor_palpite = "BR" if gols_palpite_br > gols_palpite_rival else ("RIVAL" if gols_palpite_rival > gols_palpite_br else "EMPATE")
        vencedor_real = "BR" if gols_real_br > gols_real_rival else ("RIVAL" if gols_real_rival > gols_real_br else "EMPATE")
        
        if vencedor_palpite == vencedor_real:
            # 2. Acerto do vencedor e diferença de golos (5 Pontos)
            diff_palpite = gols_palpite_br - gols_palpite_rival
            diff_real = gols_real_br - gols_real_rival
            if diff_palpite == diff_real:
                return 5
            # 3. Acerto simples de quem venceu (3 Pontos)
            return 3
    except Exception:
        pass
    return 0

# --- GERADOR DE RELATÓRIO EM PDF ---
def gerar_pdf_bolao(nome_grupo, confronto, apostas, resultado_real=None):
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_text_color(0, 156, 59) # Verde
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 15, "RELATORIO OFICIAL - BOLAO DA SELECAO", ln=True, align="C")
    
    pdf.set_text_color(0, 39, 118) # Azul
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, f"Grupo: {nome_grupo}", ln=True, align="C")
    
    pdf.set_text_color(50, 50, 50)
    pdf.set_font("Helvetica", "I", 11)
    pdf.cell(0, 8, f"Confronto: {confronto}", ln=True, align="C")
    if resultado_real:
        pdf.cell(0, 8, f"Placar Final Real: {resultado_real}", ln=True, align="C")
    pdf.cell(0, 8, f"Relatorio extraido em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="C")
    pdf.ln(10)
    
    # Cabeçalhos
    pdf.set_fill_color(0, 156, 59)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(70, 10, " Nome do Apostador", border=1, fill=True)
    pdf.cell(30, 10, " Palpite", border=1, fill=True, align="C")
    pdf.cell(50, 10, " Registro", border=1, fill=True, align="C")
    pdf.cell(30, 10, " Pontos", border=1, fill=True, align="C")
    pdf.ln()
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 10)
    
    color_toggle = False
    for aposta in apostas:
        if color_toggle:
            pdf.set_fill_color(240, 248, 240)
        else:
            pdf.set_fill_color(255, 255, 255)
            
        nome = aposta.get("Nome", "").encode('latin-1', 'replace').decode('latin-1')
        palpite = aposta.get("Palpite", "").encode('latin-1', 'replace').decode('latin-1')
        data_reg = aposta.get("Data Registro", "").encode('latin-1', 'replace').decode('latin-1')
        
        pts = 0
        if resultado_real:
            pts = calcular_pontos(palpite, resultado_real)
            
        pdf.cell(70, 10, f" {nome}", border=1, fill=True)
        pdf.cell(30, 10, f" {palpite}", border=1, fill=True, align="C")
        pdf.cell(50, 10, f" {data_reg}", border=1, fill=True, align="C")
        pdf.cell(30, 10, f" {pts} pts", border=1, fill=True, align="C")
        pdf.ln()
        color_toggle = not color_toggle
        
    return pdf.output()

# --- CHAMADA DO GEMINI COM BUSCA EM TEMPO REAL (LIMITADO A 15 DIAS) ---
@st.cache_data(ttl=1800)
def puxar_proximos_jogos():
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    
    fallback_jogos = [
        {"confronto": "Brasil x Haiti", "data": "19/06/2026", "hora": "17:00"},
        {"confronto": "Brasil x Escócia", "data": "24/06/2026", "hora": "21:00"}
    ]
    
    if not model:
        return fallback_jogos
        
    try:
        prompt = (
            f"Hoje é dia {data_hoje} (junho de 2026). Faça uma pesquisa no Google e traga os jogos reais oficiais "
            f"da Seleção Brasileira Masculina de Futebol na Copa do Mundo de 2026 agendados para os próximos 15 dias (de {data_hoje} até 04/07/2026). "
            f"Ignore totalmente jogos de Eliminatórias de setembro ou outubro. Foque apenas em partidas reais da Copa de 2026 nesse intervalo de 15 dias, "
            f"como o jogo de hoje contra o Haiti (19/06/2026) e o jogo contra a Escócia (24/06/2026). "
            f"Para cada jogo forneça o confronto, data e a hora oficial prevista no formato JSON estrito: "
            f"[{{'confronto': 'Brasil x Adversario', 'data': 'DD/MM/2026', 'hora': 'HH:MM'}}] "
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
                        # Garante estrutura do campo hora
                        if 'hora' not in jogo:
                            jogo['hora'] = "17:00"
                        jogos_filtrados.append(jogo)
                except Exception:
                    if "2026" in jogo['data'] and not any(m in jogo['data'] for m in ["09", "10", "11"]):
                        if 'hora' not in jogo:
                            jogo['hora'] = "17:00"
                        jogos_filtrados.append(jogo)
            
            if jogos_filtrados:
                return jogos_filtrados
        return fallback_jogos
    except Exception:
        return fallback_jogos

# --- GERENCIAMENTO DE ESTADO E NAVEGAÇÃO ---
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

# Barra de Navegação Horizontal Dinâmica
col_nav1, col_nav2, col_nav3 = st.columns(3)

with col_nav1:
    tipo_bt_apostar = "primary" if st.session_state.aba_ativa == "🏆 Entrar & Apostar" else "secondary"
    if st.button("🏆 Entrar & Apostar", use_container_width=True, type=tipo_bt_apostar, key="btn_aba_apostar"):
        mudar_aba("🏆 Entrar & Apostar")
        
with col_nav2:
    tipo_bt_criar = "primary" if st.session_state.aba_ativa == "🛠️ Criar Novo Bolão" else "secondary"
    if st.button("🛠️ Criar Novo Bolão", use_container_width=True, type=tipo_bt_criar, key="btn_aba_criar"):
        mudar_aba("🛠️ Criar Novo Bolão")
        
with col_nav3:
    tipo_bt_ver = "primary" if st.session_state.aba_ativa == "📊 Ver Palpites & Download" else "secondary"
    if st.button("📊 Ver Palpites & Download", use_container_width=True, type=tipo_bt_ver, key="btn_aba_ver"):
        mudar_aba("📊 Ver Palpites & Download")

st.markdown("---")

# --- EXECUÇÃO CONFORME A ABA ATIVA ---

# --- ABA 1: FAZER PALPITE ---
if st.session_state.aba_ativa == "🏆 Entrar & Apostar":
    st.markdown("### 📝 Registrar o seu Palpite")
    
    if dados_bolao:
        lista_grupos = [k for k in dados_bolao.keys() if not k.startswith("_")]
        
        if lista_grupos:
            # Define qual grupo exibir primeiro por padrão
            if st.session_state.grupo_selecionado_padrao not in lista_grupos:
                st.session_state.grupo_selecionado_padrao = lista_grupos[0]
                
            st.write("🎈 **Selecione em qual bolão você deseja entrar clicando em um dos balões abaixo:**")
            
            # Exibição elegante em formato de balões/pílulas
            cols_pills = st.columns(len(lista_grupos) if len(lista_grupos) > 0 else 1)
            for i, grupo in enumerate(lista_grupos):
                with cols_pills[i % len(cols_pills)]:
                    is_selected = (st.session_state.grupo_selecionado_padrao == grupo)
                    tipo_balao = "primary" if is_selected else "secondary"
                    label = f"🔵 {grupo}" if is_selected else f"⚪ {grupo}"
                    
                    if st.button(label, key=f"pill_sel_{grupo}", use_container_width=True, type=tipo_balao):
                        st.session_state.grupo_selecionado_padrao = grupo
                        st.rerun()
                        
            grupo_chosen = st.session_state.grupo_selecionado_padrao
            detalhes_grupo = dados_bolao[grupo_chosen]
            
            # --- SISTEMA DE BLOQUEIO ANTI-BATOTA (Sugestão 3) ---
            bloqueado = False
            data_hora_jogo_str = detalhes_grupo.get("data_hora_jogo", "")
            if data_hora_jogo_str:
                try:
                    dt_jogo = datetime.strptime(data_hora_jogo_str, "%d/%m/%Y %H:%M")
                    # Se faltar menos de 10 minutos para o jogo ou já começou, bloqueia
                    tempo_restante = (dt_jogo - datetime.now()).total_seconds() / 60
                    if tempo_restante < 10:
                        bloqueado = True
                except Exception:
                    pass
            
            st.markdown(f"""
            <div class='status-box' style='margin-top: 15px;'>
                <strong>📌 Bolão Ativo:</strong> {grupo_chosen}<br>
                <strong>⚽ Confronto da Copa:</strong> {detalhes_grupo['jogo']}<br>
                <strong>⏰ Hora de Início:</strong> {data_hora_jogo_str if data_hora_jogo_str else 'Não definida'}
            </div>
            """, unsafe_allow_html=True)
            
            if bloqueado:
                st.error("⏰ **Apostas Trancadas!** Faltam menos de 10 minutos ou a partida já começou. Os palpites deste bolão estão encerrados para evitar batotas!")
            else:
                with st.form("form_novo_palpite"):
                    nome_participante = st.text_input("O seu Nome ou Alcunha:")
                    
                    col_gols_br, col_gols_op = st.columns(2)
                    gols_brasil = col_gols_br.number_input("Gols do Brasil:", min_value=0, max_value=20, value=0, step=1)
                    gols_oponente = col_gols_op.number_input("Gols do Adversário:", min_value=0, max_value=20, value=0, step=1)
                    
                    btn_salvar_palpite = st.form_submit_button("Confirmar Palpite")
                    
                    if btn_salvar_palpite:
                        nome_limpo = nome_participante.strip()
                        placar_desejado = f"{gols_brasil} x {gols_oponente}"
                        
                        if nome_limpo == "":
                            st.error("⚠️ Digite o seu nome para guardar a aposta!")
                        else:
                            # VALIDAÇÃO CONTRA DUPLICAÇÃO DE PLACAR
                            lista_outros = [
                                a for a in detalhes_grupo["apostas"] if a["Nome"].lower() != nome_limpo.lower()
                            ]
                            
                            placar_ja_existe = any(a["Palpite"] == placar_desejado for a in lista_outros)
                            
                            if placar_ja_existe:
                                st.error(f"❌ O placar de **{placar_desejado}** já foi escolhido por outro participante neste bolão! Escolha outro resultado para competir.")
                            else:
                                novo_palpite = {
                                    "Nome": nome_limpo,
                                    "Palpite": placar_desejado,
                                    "Data Registro": datetime.now().strftime("%d/%m/%Y %H:%M")
                                }
                                detalhes_grupo["apostas"] = lista_outros + [novo_palpite]
                                
                                salvar_banco_dados(dados_bolao)
                                st.success(f"🎉 Palpite registrado com sucesso! Redirecionando para classificação...")
                                
                                mudar_aba("📊 Ver Palpites & Download", grupo_foco=grupo_chosen)
            
            # --- CONVOCATÓRIA WHATSAPP (Sugestão 4) ---
            st.markdown("---")
            text_partilha = (
                f"⚽ Deixa o teu palpite no bolão de Copa: *{grupo_chosen}*!\n"
                f"🏟️ Jogo: *{detalhes_grupo['jogo']}*\n"
                f"👉 Entra no app e seleciona o meu grupo. Não vale repetir placar!"
            )
            link_whatsapp = f"https://api.whatsapp.com/send?text={requests.utils.quote(text_partilha)}"
            st.markdown(f"[📲 Convidar Amigos no WhatsApp]({link_whatsapp})")
        else:
            st.warning("Nenhum bolão ativo na nuvem neste momento. Vá para a aba 'Criar Novo Bolão' para começar!")

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
            # Resgata hora correspondente para salvar no bolão e aplicar anti-batota
            idx = opcoes_partidas.index(escolha_partida)
            jogo_info = jogos_reais_selecionados[idx]
            data_hora_jogo = f"{jogo_info['data']} {jogo_info['hora']}"
            
            dados_bolao[nome_lider.strip()] = {
                "jogo": escolha_partida,
                "data_hora_jogo": data_hora_jogo,
                "apostas": [],
                "resultado_real": ""
            }
            salvar_banco_dados(dados_bolao)
            st.success(f"✅ Bolão '{nome_lider}' criado com sucesso! Redirecionando para a área de palpites...")
            
            mudar_aba("🏆 Entrar & Apostar", grupo_foco=nome_lider.strip())

# --- ABA 3: CLASSIFICAÇÃO & DOWNL

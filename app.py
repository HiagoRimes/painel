import streamlit as st
import google.generativeai as genai
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from PIL import Image
# Configuração da Página
st.set_page_config(page_title="Copiloto Operacional Institucional v5.0", layout="wide")
# --- TRAVA DE SEGURANÇA ---
SENHA_ACESSO = "aprender" 
def check_password():
    password = st.text_input("🔑 Digite a senha para liberar seu estudo:", type="password")
    if password == SENHA_ACESSO:
        return True
    elif password != "":
        st.error("Senha incorreta. Tente novamente.")
        return False
    else:
        return False
# --- CONFIGURAÇÃO API ---
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
def get_model():
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    # Atualizado para incluir suporte às versões mais recentes e rápidas de visão multimodal
    prioridade = ['models/gemini-2.5-flash', 'models/gemini-1.5-flash', 'models/gemini-1.5-pro']
    for p in prioridade:
        if p in models: return genai.GenerativeModel(p)
    return genai.GenerativeModel(models[0])
model = get_model()
# --- LÓGICA PRINCIPAL (SÓ RODA SE A SENHA FOR VÁLIDA) ---
if check_password():
    
    # Gerenciamento de Memória
    if 'historico_data' not in st.session_state: st.session_state.historico_data = datetime.now().date()
    if 'historico_analises' not in st.session_state: st.session_state.historico_analises = []
    if st.session_state.historico_data != datetime.now().date():
        st.session_state.historico_analises = []
        st.session_state.historico_data = datetime.now().date()
    # --- PROMPT ATUALIZADO: COPILOTO OPERACIONAL INSTITUCIONAL V5.0 ---
    PROMPT_SISTEMA = """
COPILOTO OPERACIONAL INSTITUCIONAL – VERSÃO OFICIAL V5.0
Correlação • Fluxo • Tape Reading • Footprint • Gestão • Evolução
 
MISSÃO DO COPILOTO
Atue como meu copiloto operacional institucional especializado em Day Trade no Mini Índice (WIN).
Seu objetivo NÃO é prever o mercado ou gerar sinais cegos.
Seu objetivo é:
• Organizar meu raciocínio institucional;
• Identificar quem realmente lidera o mercado;
• Validar correlações;
• Interpretar fluxo;
• Auxiliar na tomada de decisão;
• Proteger o capital;
• Desenvolver minha capacidade analítica;
• Ensinar continuamente;
• Transformar cada pregão em evolução prática.
Você deve atuar simultaneamente como:
• Analista Macro;
• Operador Institucional;
• Especialista em Correlação;
• Especialista em Fluxo;
• Especialista em Tape Reading;
• Especialista em Footprint;
• Supervisor de Gestão de Risco;
• Professor;
• Auditor Pós-Mercado.
 
REGRA MESTRA ABSOLUTA
O WIN é sempre consequência.
Nunca inicie a análise pelo gráfico do índice.
A sequência obrigatória é:
Contexto → Drivers → Correlações → Estrutura → Tape → Footprint → Risco → Execução.
Responda sempre:
• Quem lidera?
• Quem confirma?
• Quem ajuda?
• Quem atrapalha?
• Quem está sendo ignorado?
• Vale a pena clicar?
• O que invalida minha leitura?
 
ACIONAMENTO AUTOMÁTICO
Sempre que eu enviar:
• print da grade;
• print do gráfico;
• print do footprint;
• print do Times & Trades;
• print do Book;
• histórico de operações;
• descrição textual do mercado;
execute automaticamente o protocolo completo.
Não aguarde instruções adicionais.
 
PRÉ-MERCADO AUTOMÁTICO (OBRIGATÓRIO)
Antes de qualquer análise operacional analise com base na Agenda Econômica integrada ou nos dados visuais:
Agenda Econômica
Identifique e liste:
• Eventos nacionais;
• Eventos internacionais;
• Discursos relevantes;
• Decisões de juros;
• Dados de inflação;
• Dados de emprego;
• Leilões;
• Vencimentos;
• Eventos extraordinários.
Para cada evento informar:
Evento:
Horário:
Relevância:
Dado anterior:
Consenso:
 
MATRIZ DE EXPECTATIVA
Apresente obrigatoriamente:
Cenário 1 – Resultado acima do esperado
DI:
WDO:
WIN:
Impacto esperado:
 
Cenário 2 – Resultado em linha
DI:
WDO:
WIN:
Impacto esperado:
 
Cenário 3 – Resultado abaixo do esperado
DI:
WDO:
WIN:
Impacto esperado:
 
NOTÍCIAS QUE FAZEM PREÇO
Resuma objetivamente:
• Política;
• Fiscal;
• Geopolítica;
• Commodities;
• Fluxo estrangeiro;
• Eventos extraordinários.
Informe:
O mercado está precificando principalmente: ______
 
UNIVERSO DE CORRELAÇÃO
Macro Local (DI, WDO) | Exterior (S&P500, Nasdaq, VIX, Treasury, DXY) | Fluxo Estrangeiro (EWZ) | Estrutura Interna (IFNC, IMAT, PETR4, VALE3, B3SA3).
 
SEMÁFORO DE FORÇA
Para cada ativo classifique o Vetor (⬆️ Alta, ⬇️ Baixa, ➡️ Neutro) e a Intensidade (⚪ Ruído, 🟠 Drive moderado, 🔴 Dominância forte).
 
FILTROS DE SEGURANÇA
Executar antes de qualquer entrada. Apresente Diagnóstico, Justificativa e Conclusão para:
Filtro 1 – DI × WDO
Filtro 2 – EWZ × WIN
Filtro 3 – IFNC × IMAT
Filtro 4 – Exterior × WIN
Filtro 5 – Estrutura × Tape
 
DIAGNÓSTICO DO WIN
Determinar se o movimento atual é guiado por: Macro, Fluxo estrangeiro, Estrutura interna, Evento econômico, Evento político ou Transferência de liderança.
 
HIERARQUIA DE DOMINÂNCIA
Defina Direção, Intensidade, Dominância estimada e Justificativa para os Drivers Primário, Secundário e Terciário.
 
REGIME DE MERCADO
Classifique: Tendencial de Alta, Tendencial de Baixa, Direcional Forte, Direcional Fraco, Lateral, Volátil ou Confuso.
 
CONFLITOS ENTRE MOTORES
Informe: Motor comprador, Motor vendedor, Motor dominante, Motor ignorado e Conclusão.
 
CONVICÇÃO DO CENÁRIO
CONVICÇÃO: XX/100 (Justifique)
 
VEREDITO INSTITUCIONAL
Informe: Chefe do Mercado, Grupo Dominante, Regime Atual, Fragmentação, Convicção e Viés Operacional.
 
FATOR DOMINANTE
Escolha apenas um: Juros, Dólar, Fluxo Estrangeiro, Exterior, Bancos, Commodities, Fluxo Local, Evento Econômico, Evento Político/Fiscal.
 
FALHAS DE CORRELAÇÃO
Classifique: Sem falha, Leve, Moderada ou Grave.
 
TRANSFERÊNCIA DE LIDERANÇA
Classifique: Estável, Em transição ou Recém-transferida.
 
PLAYBOOK DOMINANTE
Escolha: Tendência, Rompimento, Continuação, Reversão, Pullback, Range, Mercado de Evento ou Mercado de Fluxo.
 
FLUXO ESTRANGEIRO
Classifique: Confirmando, Neutro ou Divergente.
 
CONTINUIDADE OU ESGOTAMENTO
Classifique: Início, Desenvolvimento, Maduro ou Possível esgotamento.
 
ALERTAS INSTITUCIONAIS
Liste riscos relevantes. Se não houver: Nenhum alerta institucional relevante identificado.
 
CURVA DE JUROS
Classifique (Alta ponta curta/longa, Queda ponta curta/longa, Abertura ou Fechamento) e explique impactos.
 
REGIME GLOBAL
Classifique: Risk-On Forte, Risk-On Moderado, Neutro, Risk-Off Moderado ou Risk-Off Forte.
 
PLACAR INSTITUCIONAL
Pontue: Juros, Dólar, Exterior, Fluxo Estrangeiro, Bancos, Commodities, Fluxo Local e defina o Vencedor do placar.
 
FORÇA DAS CORRELAÇÕES
Classifique (Muito Fraca, Fraca, Moderada, Forte, Muito Forte) para: DI × WIN, WDO × WIN, EWZ × WIN, IFNC × WIN, IMAT × WIN, SP/NQ × WIN. Informar: Correlação dominante, em transferência e ignorada.
 
LEITURA TÉCNICA DO GRÁFICO
Interprete: VWAP (Distância, Inclinação), Médias móveis, HiLo, ATR, Máxima/Mínima do dia, Topos/Fundos, Consolidação, Rompimento, Pullback. Responda: A estrutura favorece compra, venda ou espera?
 
TAPE READING
Interprete agressão, absorção, defesa, iceberg, velocidade, continuidade, recusa, deslocamento. Responda: Quem agride? Quem absorve? Quem controla?
 
FOOTPRINT
Interprete progressão, exaustão, absorção, desequilíbrios, empilhamentos, falhas de continuação, inversões. Responder: Existe progressão? Existe exaustão? Existe absorção? Quem venceu o leilão local? O fluxo confirma ou invalida o macro?
 
CHECKLIST PRÉ-CLIQUE
Responda: Agenda permite? Correlação confirma? Estrutura confirma? Tape confirma? Footprint confirma? Risco aceitável? Existe conflito? Risco-retorno adequado?
 
ASSIMETRIA DA OPERAÇÃO
Responda: Quanto posso perder? Quanto posso ganhar? Relação risco-retorno mínima de 2:1 foi atendida? Caso contrário: Recomendar NÃO OPERAR.
 
GRAU DE EVIDÊNCIA OPERACIONAL
Classificar: A+, A, B, C ou D. É proibido recomendar aumento de agressividade abaixo de A.
 
CONTEXTO TEMPORAL DO PREGÃO
Identificar: Abertura, Pós-abertura, Meio do pregão, Pré-fechamento ou Fechamento. Explicar impactos.
 
VEREDITO OPERACIONAL
Escolha: Compra favorecida, Venda favorecida, Esperar ou Não operar. Justifique.
 
CENÁRIO CONTRÁRIO
O que precisa acontecer para minha leitura estar errada? Descrever gatilhos de invalidação.
 
TERMÔMETRO DE FOMO
Classificar: Baixo, Moderado ou Alto.
 
REGRA DA SOBREVIVÊNCIA
Preservação de capital acima da oportunidade. Na ausência de evidências suficientes: Recomendar não operar.
 
MODO PROFESSOR
Ao final da análise ensinar: O principal conceito observado, Por que ele importa e O que observar nos próximos pregões.
 
DIÁRIO PÓS-MERCADO / REVISÃO HISTÓRICA (Se acionado ou se o contexto for de final de pregão)
Caso as informações enviadas contenham histórico de operações ou solicitações pós-mercado, execute as ETAPAS 1 a 10 do protocolo de auditoria de execução, identificação de erros (técnicos/comportamentais), evidências objetivas de melhoria, padrões recorrentes, plano de evolução, notas de 0 a 100 e a lição mais importante.
 
HISTÓRICO DE ANÁLISES PREVIAS DESTE PREGÃO:
{historico}
"""
    @st.cache_data(ttl=3600)
    def puxar_calendario():
        try:
            url = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            root = ET.fromstring(response.content)
            hoje_dt = datetime.now()
            eventos = [f"• {e.find('time').text} ({e.find('country').text}): {e.find('title').text}" 
                       for e in root.findall('event') if e.find('date').text == hoje_dt.strftime("%m-%d-%Y") and e.find('impact').text in ['High', 'Medium']]
            return f"### 📅 Agenda de Impacto Integrada: {hoje_dt.strftime('%d/%m/%Y')}\n\n" + "\n".join(eventos) if eventos else "Sem eventos macro de alto impacto agendados para hoje."
        except: return "### 📅 Calendário de eventos automatizado indisponível temporariamente."
    st.title("📊 COPILOTO OPERACIONAL INSTITUTIONAL V5.0")
    st.caption("Sistema Avançado de Análise Baseado em Correlação, Estrutura, Tape Reading e Footprint")
    with st.expander("📖 Guia Universo de Correlação (Configuração da Grade de Ativos)"):
        st.markdown("""
        Monte a sua grade unificada para que o modelo colete as métricas visuais com precisão:
        

| Ativo | Função Institucional |
| :--- | :--- |
| **WIN1!** | Índice Futuro (Consequência) |
| **WDO1!** | Dólar Futuro (Macro Local) |
| **DI1!** | Juros Futuros (Vértice de Controle) |
| **PETR4 / VALE3** | Estrutura de Commodities Interna |
| **IFNC / IMAT** | Motores Setoriais (Bancos e Materiais Básicos) |
| **ES1! / NQ1!** | Fluxo do Mercado Externo (S&P 500 e Nasdaq) |
| **EWZ** | Termômetro do Fluxo Estrangeiro |
| **VIX** | Índice do Medo / Volatilidade Global |

""")
    # Exibe a agenda capturada no topo do painel
    st.info(puxar_calendario())
    # Estruturação da área de entrada
    col_input, col_text = st.columns([2, 3])
    
    with col_input:
        uploaded_file = st.file_uploader("📸 Suba o Print Operacional (Grade, Fluxo, Footprint ou Gráfico):", type=['jpg', 'png', 'jpeg'])
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Print Carregado", use_column_width=True)
            
    with col_text:
        contexto_manual = st.text_area(
            "📝 Notas de Fluxo / Variáveis em Tempo Real (Opcional):",
            placeholder="Ex: Fluxo estrangeiro acabou de rasgar na compra pelo Times & Trades, DI virando para o terreno negativo...",
            height=180
        )
    if uploaded_file:
        if st.button("🚀 EXECUTAR PROTOCOLO OPERACIONAL"):
            with st.spinner("Executando protocolo institucional... Filtrando motores macro e fluxo real."):
                
                # Resgata o histórico acumulado na sessão do Streamlit
                hist_texto = "\n".join(st.session_state.historico_analises)
                
                # Monta a formatação injetando as variáveis dinâmicas ao prompt mestre
                full_prompt = (
                    PROMPT_SISTEMA.format(historico=hist_texto) + 
                    f"\n\nAGENDA ATUAL DO DIA:\n{puxar_calendario()}" +
                    f"\n\nNOTAS TEXTUAIS ADICIONAIS DO TRADER:\n{contexto_manual if contexto_manual else 'Nenhuma.'}"
                )
                
                try:
                    # Chamada multimodal do Gemini passando o prompt de texto construído e a imagem carregada
                    response = model.generate_content([full_prompt, image])
                    
                    st.markdown("---")
                    st.markdown("### 📋 PROTOCOLO EXECUTADO — VIÉS INSTITUCIONAL")
                    st.markdown(response.text)
                    
                    # Salva a resposta no histórico da sessão para consistência lógica nas próximas leituras
                    st.session_state.historico_analises.append(f"[{datetime.now().strftime('%H:%M:%S')}] {response.text}")
                except Exception as e:
                    st.error(f"Erro na geração do diagnóstico: {e}")
    # Ferramenta de gerenciamento de dados na barra lateral
    if st.sidebar.button("🗑️ Resetar Histórico do Pregão"):
        st.session_state.historico_analises = []
        st.rerun()

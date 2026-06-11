import streamlit as st
import yfinance as yf
from google import genai
import pandas as pd
from datetime import datetime
import time

# ==============================================================================
# CONFIGURAÇÃO INTERFACE E AMBIENTE
# ==============================================================================
st.set_page_config(
    page_title="Mesa Quant - Protocolo Mestre WIN", 
    page_icon="🔮", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização customizada em CSS para dar o visual "Mesa de Operações Dark"
st.markdown("""
    <style>
    .reportview-container { background: #0e1117; }
    .metric-box {
        background-color: #161b22;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #30363d;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🔮 Monitor Quantitativo Autônomo — WIN M15")
st.caption("Conectado via API ao Yahoo Finance | Inteligência de Fluxo Institucional")

# Inicialização da API do Gemini através dos Secrets Seguros do Streamlit
if "GEMINI_API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("❌ ERRO: Configure a sua 'GEMINI_API_KEY' nos Secrets do Streamlit.")
    st.stop()

# ==============================================================================
# PROMPT MESTRE DEFINITIVO (CONSOLIDADO E COMPLETO)
# ==============================================================================
PROMPT_MESTRE = """
Atue como um analista técnico e de fluxo institucional de mercado financeiro, focado em Day Trade no minicontrato de Índice Bovespa (WIN). Toda vez que eu te enviar a grade de cotações por texto com as variações reais colhidas da API, você deve processar esses dados e me retornar OBRIGATORIAMENTE um relatório cirúrgico estruturado exatamente nos 22 passos abaixo, utilizando linguagem técnica de mesa de operações (sem adjetivos informais) combinada com os termos genéricos curtos entre aspas.

Siga rigorosamente esta estrutura de resposta:

1. 📊 AGENDA ECONÔMICA, NOTÍCIAS E MATRIZ DE IMPACTO
- Com base nas notícias e no contexto macroeconômico atual fornecido, identifique a agenda econômica e notícias relevantes do dia atual.
- Liste o indicador mais importante do dia, informando: Nome, Horário e Relevância (Alta/Média/Baixa).
- Apresente o Dado Anterior e o Consenso (Esperado) do mercado.
- Monte a Matriz de Impacto detalhando o que tende a acontecer com o DI, WDO e WIN em 3 cenários distintos: se o resultado vier MAIOR que o esperado, IGUAL ao esperado ou MENOR que o esperado.
- Adicione um resumo ultracompacto das notícias políticas, fiscais ou geopolíticas que estão fazendo preço no momento.

2. 📈 GRADE DE VARIAÇÃO (O SEMÁFORO VISUAL)
Organize os ativos fornecidos por níveis (Nível 1: Macro Local [DI e WDO], Nível 2: Clima Global [VIX, S&P, Nasdaq], Nível 3: Peso Matemático [IFNC, IMAT, PETR4, B3SA3, EWZ]).
Cada linha de ativo DEVE iniciar obrigatoriamente com a combinação exata de UMA Seta de Vetor e UMA Bolinha de Força, seguidas da nomenclatura técnica e termo curto, conforme as regras abaixo:
- Setas de Vetor: 
  ⬆️ = Ativo pulling o WIN para cima (variação positiva).
  ⬇️ = Ativo empurrando o WIN para baixo (variação negativa).
  ➡️ = Ativo neutro, sem força de tração.
- Código de Força (Bolinhas):
  ⚪ Ruído de Mercado "Neutro": Oscilação normal/baixa do dia. Sem fluxo institucional relevante (deve ser ignorado no filtro).
  🟠 Drive Direcional "Moderado": Grandes players montando posição. Preço deslocando e tendência se desenhando.
  🔴 Dominância Direcional "Forte": Variação extrema. O fluxo absorve a liquidez contrária e dita o rumo do mercado.
Exemplo de linha: "⬇️ 🟠 IFNC (-0,86%): Drive Direcional "Moderado" -> [Breve análise de fluxo rápida baseada na variação]"

3. 🛡️ FILTROS DE CORRELAÇÃO E VALIDAÇÃO (AS TRAVAS DE SEGURANÇA)
Faça o cruzamento de dados e valide as 3 travas antes do clique:
- Filtro 1: DI x WDO (Regra de Ouro Flexibilizada): DI x WDO continua sendo a principal referência macroeconômica do mercado brasileiro. Se estiverem alinhados no mesmo sentido, valide como Tendência Forte (Sinal Verde). Se estiverem em sentidos opostos, classifique como Divergência e acione o critério de "Sair Fora". ENTRETANTO, caso outro motor apresente dominância claramente superior (IFNC, EWZ, Exterior, Commodities ou Fluxo Local), informe explicitamente que a influência do macro está sendo temporariamente absorvida pelo motor dominante.
- Filtro 2: EWZ x WIN (Fluxo Gringo): Valide se o EWZ confirma o movimento do WIN ou se aponta uma divergência (Armadilha Institucional).
- Filtro 3: IFNC x IMAT (Engrenagem Interna): Valide se os blocos de peso estão alinhados (Motor Forte) ou se há briga entre eles (Divergência Setorial / Mercado Travado / Evitar Rompimentos).

4. 🎯 DIAGNÓSTICO DO WIN
- Resumo macro de duas ou três linhas definindo se o movimento atual do WIN ocorre por estresse macroeconômico (DI/Dólar) ou por pura matemática dos blocos locais.

5. 👑 HIERARQUIA DE DOMINÂNCIA (DRIVERS DO MERCADO)
- Identifique e ranqueie os 3 principais drivers individuais do momento: 1º Driver Primário, 2º Driver Secundário e 3º Driver Terciário.
- Para cada driver, informe obrigatoriamente: Direção (Alta, Baixa ou Neutro), Intensidade, Justificativa objetiva e Dominância Estimada (%). [Foco exclusivo: ranquear ativos individuais ativos e evitar repetições com os blocos 6, 12 e 21. A soma das porcentagens não precisa atingir 100%].

6. 🌐 ANÁLISE DE DOMINÂNCIA MACRO
- Classifique exclusivamente qual GRUPO está dominando o mercado entre as opções: [Macro Local / Fluxo Internacional / Fluxo Estrangeiro / Estrutura Interna]. Responda estritamente: "Motor dominante atual: ______" [Evitar repetições com os blocos 5, 12 e 21].

7. 🧩 FRAGMENTAÇÃO OU CONCENTRAÇÃO
- Classifique em apenas uma opção: [Muito Concentrado / Concentrado / Moderadamente Concentrado / Fragmentado / Muito Fragmentado]. Mercado Concentrado sinaliza continuidade; Mercado Fragmentado sinaliza ruído, armadilhas e falsas tendências.

8. ⚙️ REGIME DE MERCADO
- Classifique o ambiente atual em apenas UMA categoria: [Tendencial de Alta / Tendencial de Baixa / Direcional Forte / Direcional Fraco / Lateral / Volátil / Confuso]. Explique em uma única frase curta o motivo.

9. ⚔️ CONFLITOS ENTRE MOTORES
- Identifique disputas diretas (Ex: DI e Dólar baixistas contra S&P altista). Informe: Quem pressiona para cima, quem pressiona para baixo e quem está vencendo. Caso não exista conflito, escreva: "Sem conflitos relevantes entre motores."

10. 🔥 ÍNDICE DE CONVICÇÃO DO CENÁRIO
- Atribua uma nota de 0 a 100 para a qualidade técnica do cenário baseado em correlações, drivers, EWZ e IFNC. Formato: "CONVICÇÃO DO CENÁRIO: XX/100" seguido de justificativa técnica de até 3 linhas.

11. 🎯 DIAGNÓSTICO PROFISSIONAL FINAL
- Responda de forma direta em linguagem de mesa institucional: • Quem é o Chefe do Mercado? | • Qual grupo domina? | • Qual o regime atual? | • Qual o nível de fragmentação? | • Qual a convicção do cenário? | • Qual o viés probabilístico operacional?

12. 🎯 FATOR DOMINANTE DO DIA
- Identifique a variável única que melhor explica o comportamento do mercado no momento. Escolha apenas UMA opção: [Juros / Dólar / Fluxo Estrangeiro / Exterior (S&P/Nasdaq/VIX) / Bancos (IFNC) / Commodities (IMAT/Petróleo) / Fluxo Local / Evento Econômico / Evento Político/Fiscal]. Formato: "FATOR DOMINANTE ATUAL: ______", justificando em até 2 linhas sem repetir as explicações dos blocos 5, 6 e 21.

13. ⚠️ FALHAS DE CORRELAÇÃO
- Verifique anomalias estruturais. Classifique em: [Sem Falha / Falha Leve / Falha Moderada / Falha Grave]. Explique o significado institucional do comportamento. Formato: "STATUS DAS CORRELAÇÕES: ______".

14. 🔄 TRANSFERÊNCIA DE LIDERANÇA
- Identifique se há rotação de comando entre os motores. Classifique em: [Liderança Estável / Liderança em Transição / Liderança Recém-Transferida]. Formato: "ESTADO DA LIDERANÇA: ______" acompanhado de explicação de até 2 linhas.

15. ⚙️ PLAYBOOK OPERACIONAL DO AMBIENTE
- Classifique o modelo operacional que deve predominar. Escolha apenas UMA opção: [Tendência / Rompimento / Continuação / Reversão / Pullback / Range / Mercado de Evento / Mercado de Fluxo]. Formato: "PLAYBOOK DOMINANTE: ______", justificando em até 2 linhas.

16. 🏛️ FLUXO ESTRANGEIRO (QUALIDADE DO MOVIMENTO)
- Avalie a participação estrangeira via EWZ. Classifique em: [Fluxo Estrangeiro Confirmando / Fluxo Estrangeiro Neutro / Fluxo Estrangeiro Divergente]. Formato: "STATUS DO FLUXO ESTRANGEIRO: ______", explicando em até 2 linhas.

17. ⏳ CONTINUIDADE OU ESGOTAMENTO
- Avalie o estágio do movimento institucional. Classifique em: [Início de Movimento / Movimento em Desenvolvimento / Movimento Maduro / Possível Esgotamento]. Formato: "ESTÁGIO DO MOVIMENTO: ______", justificando em até 2 linhas.

18. 🚨 ALERTAS INSTITUCIONAIS
- Identifique situações críticas. Formato: "ALERTAS INSTITUCIONAIS ATIVOS:" seguido por marcadores (•). Se não houver, escreva: "Nenhum alerta institucional relevante identificado."

19. 🏦 CURVA DE JUROS E PRESSÃO MACRO
- Analise a estrutura dos juros futuros com base no ativo de Juros ou no contexto da curva interna. Classifique em apenas UMA opção: [Alta na ponta curta / Alta na ponta longa / Queda na ponta curta / Queda na ponta longa / Abertura da curva / Fechamento da curva]. Formato: "ESTADO DA CURVA: ______", explicando em até 3 linhas o impacto esperado sobre IFNC, WIN, crescimento e risco.

20. 🌎 REGIME GLOBAL DE RISCO
- Classifique o ambiente global (S&P500, Nasdaq, VIX, Treasury, DXY). Escolha apenas UMA opção: [Risk-On Forte / Risk-On Moderado / Neutro / Risk-Off Moderado / Risk-Off Forte]. Formato: "REGIME GLOBAL: ______", explicando o fluxo em até 3 linhas.

21. 🎯 PLACAR INSTITUCIONAL DE FORÇAS
- Quantifique a força de pressão de cada grupo através de notas de 0 a 10: Juros, Dólar, Exterior, Fluxo Estrangeiro, Bancos, Commodities e Fluxo Local. Formato: "Juros: X/10 Dólar: X/10..." finalizando com: "VENCEDOR DO PLACAR: ______" [Foco exclusivo na métrica quantitativa, sem repetir textos explicativos dos blocos 5, 6 e 12].

22. 📉 FORÇA DA CORRELAÇÃO INSTITUCIONAL
Meça a intensidade real das correlações individuais observadas especificamente no contexto do pregão atual em: [Muito Fraca / Fraca / Moderada / Forte / Muito Forte]. A classificação deve priorizar o comportamento atual informado e não apenas relações históricas teóricas.
Formato obrigatório:
"📉 FORÇA DAS CORRELAÇÕES
DI x WIN: ______ | WDO x WIN: ______ | EWZ x WIN: ______ | IFNC x WIN: ______ | IMAT x WIN: ______ | SP500/NQ x WIN: ______
CORRELAÇÃO DOMINANTE: ______
CORRELAÇÃO EM TRANSFERÊNCIA: ______
CORRELAÇÃO IGNORADA PELO MERCADO: ______"
Interpretação Institucional: Explique em até 3 linhas qual correlação comanda o WIN de fato e qual delas perdeu a capacidade de influência ou está sendo absorvida, indicando os motivos dinâmicos da transferência ou do isolamento.

REGRA DE OTIMIZAÇÃO E REPETIÇÃO: Os blocos 5, 6, 12 e 21 devem ser complementares por focar em escopos diferentes (Raking de Ativos, Grupos Macro, Variável Explicativa e Notas Quantitativas). Se as conclusões de mercado forem semelhantes, aprofunde o motivo técnico em vez de repetir o mesmo diagnóstico com palavras differentes.

REGRA MESTRA ABSOLUTA: Trate sempre o WIN como consequência dos drivers institucionais identificados e nunca como a origem da análise. Responda implicitamente ou explicitamente: Quem está liderando? Quem está ajudando? Quem está atrapalhando? Quem está sendo ignorado? Quando houver conflito entre os motores, informe obrigatoriamente: 1. Qual motor possui a maior dominância naquele momento; 2. Qual motor está sendo ignorado pelo mercado; 3. Qual correlação possui maior força relativa e qual perdeu capacidade de influenciar o WIN.
"""

# ==============================================================================
# MOTOR DE CAPTURA DE DADOS (USANDO ETFs PARA ESTABILIDADE)
# ==============================================================================
def engine_coleta_dados():
    # Substituído índices instáveis por ETFs de alta liquidez para garantir dados 100% do tempo
    ativos = {
        "WIN (Ibov via BOVA11)": "BOVA11.SA",
        "WDO (Dólar Comercial)": "BRL=X",
        "PETR4": "PETR4.SA",
        "B3SA3": "B3SA3.SA",
        "ITUB4 (Proxy IFNC)": "ITUB4.SA",
        "VALE3 (Proxy IMAT)": "VALE3.SA",
        "EWZ (ETF Brasil em NY)": "EWZ",
        "S&P 500 Futuro": "^GSPC",
        "NASDAQ (via QQQ)": "QQQ",
        "VIX (Índice do Medo)": "^VIX"
    }
    
    grade_texto = ""
    resumo_sidebar = {}
    bloco_noticias = ""
    
    for nome, ticker in ativos.items():
        try:
            ticker_obj = yf.Ticker(ticker)
            # Histórico de 5 dias para garantir robustez técnica
            df = ticker_obj.history(period="5d")
            
            # Verificação de segurança rigorosa
            if not df.empty and len(df) >= 2:
                fechamento_anterior = df['Close'].iloc[-2]
                preco_atual = df['Close'].iloc[-1]
                var_percentual = ((preco_atual - fechamento_anterior) / fechamento_anterior) * 100
                
                grade_texto += f"- {nome}: Variação Atual de {var_percentual:+.2f}% | Último Preço: {preco_atual:,.2f}\n"
                resumo_sidebar[nome] = f"{var_percentual:+.2f}%"
                
                # Coleta notícias apenas para os índices principais
                if ticker in ["BOVA11.SA", "^GSPC"] and not bloco_noticias:
                    noticias_lista = ticker_obj.news
                    if noticias_lista:
                        bloco_noticias = "\n📰 FEED DE MANCHETES INSTITUCIONAIS RECENTES:\n"
                        for n in noticias_lista[:4]:
                            bloco_noticias += f"• {n['title']} (Fonte: {n.get('publisher', 'Mesa')})\n"
            else:
                grade_texto += f"- {nome}: Dados de oscilação indisponíveis no momento.\n"
                resumo_sidebar[nome] = "N/A"
        except Exception:
            grade_texto += f"- {nome}: Erro de comunicação com a API.\n"
            resumo_sidebar[nome] = "Erro"
            
    return grade_texto, resumo_sidebar, bloco_noticias

# ==============================================================================
# EXECUÇÃO DO CONTEXTO WEB (ESTRUTURA E REFRESH M15)
# ==============================================================================
# Barra lateral informativa (Dashboard de Variações)
st.sidebar.header("📊 Grade de Cotações Real-Time")
st.sidebar.caption(f"Último Scan: {datetime.now().strftime('%H:%M:%S')}")

# Dispara a função de coleta de dados
grade_dados, mini_dashboard, noticias = engine_coleta_dados()

# Renderiza painel rápido de cotações na lateral do Streamlit
for ativo, var in mini_dashboard.items():
    if "+" in var:
        st.sidebar.markdown(f"🟩 **{ativo}**: `{var}`")
    elif "-" in var:
        st.sidebar.markdown(f"🟥 **{ativo}**: `{var}`")
    else:
        st.sidebar.markdown(f"⬜ **{ativo}**: `{var}`")

# Botão manual de emergência para a Mesa de Operações
if st.sidebar.button("🔄 Forçar Recalibragem de Grade (Clique Manual)"):
    st.rerun()

# Montagem do Input Final para Inteligência Artificial
input_api_completo = f"""
CONTEXTO ATUAL DE TELA RECOLHIDO VIA API DO YAHOO FINANCE:
{grade_dados}

{noticias}

COMANDO OPERACIONAL:
Aplique integralmente o seu protocolo mestre e gere o relatório cirúrgico de 22 blocos com base nas variações reais acima.
REGRA DE SEGURANÇA: Se algum ativo estiver como 'N/A' ou 'Erro', NÃO invente valores. Baseie a análise macro EXCLUSIVAMENTE nos ativos que apresentaram variação real acima.
Trate o WIN estritamente como consequência estrutural dos motores.
"""

# Execução com lógica de Retry (segurança contra Erro 503)
with st.spinner("🤖 Executando Modelo de Inteligência Institucional..."):
    tentativas = 0
    sucesso = False
    while tentativas < 3 and not sucesso:
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=input_api_completo
            )
            st.success("✅ Relatório de Cenário Atualizado com Êxito!")
            st.markdown(response.text)
            sucesso = True
        except Exception as err:
            tentativas += 1
            if tentativas < 3:
                st.warning(f"⚠️ Instabilidade na API (Tentativa {tentativas}/3). Aguardando 10 segundos...")
                time.sleep(10)
            else:
                st.error(f"❌ Falha crítica no processamento após 3 tentativas: {err}")

# ==============================================================================
# SINCRO DE CANDLE M15 (TEMPORIZADOR AUTOMÁTICO)
# ==============================================================================
INTERVALO_M15 = 900
time.sleep(INTERVALO_M15)
st.rerun()

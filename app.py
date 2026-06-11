import streamlit as st
import yfinance as yf
from google import genai
import pandas as pd
from datetime import datetime
import time

# ==============================================================================
# CONFIGURAÇÃO INTERFACE E AMBIENTE (LAYOUT MESA DE OPERAÇÕES)
# ==============================================================================
st.set_page_config(
    page_title="Mesa Quant - Protocolo Mestre WIN", 
    page_icon="🔮", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS para visual "Mesa Dark"
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

# Inicialização da API do Gemini
if "GEMINI_API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("❌ ERRO: Configure a sua 'GEMINI_API_KEY' nos Secrets do Streamlit.")
    st.stop()

# ==============================================================================
# PROMPT MESTRE INTEGRAL (OS 22 BLOCOS - NENHUM RESUMO)
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

3. 🛡️ FILTROS DE CORRELAÇÃO E VALIDAÇÃO (AS TRAVAS DE SEGURANÇA)
Faça o cruzamento de dados e valide as 3 travas antes do clique:
- Filtro 1: DI x WDO (Regra de Ouro Flexibilizada): DI x WDO continua sendo a principal referência macroeconômica do mercado brasileiro. Se estiverem alinhados no mesmo sentido, valide como Tendência Forte (Sinal Verde). Se estiverem em sentidos opostos, classifique como Divergência e acione o critério de "Sair Fora".
- Filtro 2: EWZ x WIN (Fluxo Gringo): Valide se o EWZ confirma o movimento do WIN ou se aponta uma divergência (Armadilha Institucional).
- Filtro 3: IFNC x IMAT (Engrenagem Interna): Valide se os blocos de peso estão alinhados (Motor Forte) ou se há briga entre eles (Divergência Setorial / Mercado Travado / Evitar Rompimentos).

4. 🎯 DIAGNÓSTICO DO WIN
- Resumo macro de duas ou três linhas definindo se o movimento atual do WIN ocorre por estresse macroeconômico (DI/Dólar) ou por pura matemática dos blocos locais.

5. 👑 HIERARQUIA DE DOMINÂNCIA (DRIVERS DO MERCADO)
- Identifique e ranqueie os 3 principais drivers individuais do momento: 1º Driver Primário, 2º Driver Secundário e 3º Driver Terciário.
- Para cada driver, informe obrigatoriamente: Direção (Alta, Baixa ou Neutro), Intensidade, Justificativa objetiva e Dominância Estimada (%).

6. 🌐 ANÁLISE DE DOMINÂNCIA MACRO
- Classifique exclusivamente qual GRUPO está dominando o mercado entre as opções: [Macro Local / Fluxo Internacional / Fluxo Estrangeiro / Estrutura Interna]. Responda estritamente: "Motor dominante atual: ______"

7. 🧩 FRAGMENTAÇÃO OU CONCENTRAÇÃO
- Classifique em apenas uma opção: [Muito Concentrado / Concentrado / Moderadamente Concentrado / Fragmentado / Muito Fragmentado].

8. ⚙️ REGIME DE MERCADO
- Classifique o ambiente atual em apenas UMA categoria: [Tendencial de Alta / Tendencial de Baixa / Direcional Forte / Direcional Fraco / Lateral / Volátil / Confuso].

9. ⚔️ CONFLITOS ENTRE MOTORES
- Identifique disputas diretas (Ex: DI e Dólar baixistas contra S&P altista). Informe: Quem pressiona para cima, quem pressiona para baixo e quem está vencendo.

10. 🔥 ÍNDICE DE CONVICÇÃO DO CENÁRIO
- Atribua uma nota de 0 a 100 para a qualidade técnica do cenário baseado em correlações, drivers, EWZ e IFNC.

11. 🎯 DIAGNÓSTICO PROFISSIONAL FINAL
- Responda de forma direta em linguagem de mesa institucional: • Quem é o Chefe do Mercado? | • Qual grupo domina? | • Qual o regime atual? | • Qual o nível de fragmentação? | • Qual a convicção do cenário? | • Qual o viés probabilístico operacional?

12. 🎯 FATOR DOMINANTE DO DIA
- Identifique a variável única que melhor explica o comportamento do mercado no momento. Escolha apenas UMA opção: [Juros / Dólar / Fluxo Estrangeiro / Exterior (S&P/Nasdaq/VIX) / Bancos (IFNC) / Commodities (IMAT/Petróleo) / Fluxo Local / Evento Econômico / Evento Político/Fiscal].

13. ⚠️ FALHAS DE CORRELAÇÃO
- Verifique anomalias estruturais. Classifique em: [Sem Falha / Falha Leve / Falha Moderada / Falha Grave].

14. 🔄 TRANSFERÊNCIA DE LIDERANÇA
- Identifique se há rotação de comando entre os motores. Classifique em: [Liderança Estável / Liderança em Transição / Liderança Recém-Transferida].

15. ⚙️ PLAYBOOK OPERACIONAL DO AMBIENTE
- Classifique o modelo operacional que deve predominar. Escolha apenas UMA opção: [Tendência / Rompimento / Continuação / Reversão / Pullback / Range / Mercado de Evento / Mercado de Fluxo].

16. 🏛️ FLUXO ESTRANGEIRO (QUALIDADE DO MOVIMENTO)
- Avalie a participação estrangeira via EWZ. Classifique em: [Fluxo Estrangeiro Confirmando / Fluxo Estrangeiro Neutro / Fluxo Estrangeiro Divergente].

17. ⏳ CONTINUIDADE OU ESGOTAMENTO
- Avalie o estágio do movimento institucional. Classifique em: [Início de Movimento / Movimento em Desenvolvimento / Movimento Maduro / Possível Esgotamento].

18. 🚨 ALERTAS INSTITUCIONAIS
- Identifique situações críticas. Formato: "ALERTAS INSTITUCIONAIS ATIVOS:" seguido por marcadores (•).

19. 🏦 CURVA DE JUROS E PRESSÃO MACRO
- Analise a estrutura dos juros futuros com base no ativo de Juros ou no contexto da curva interna. Classifique em apenas UMA opção.

20. 🌎 REGIME GLOBAL DE RISCO
- Classifique o ambiente global (S&P500, Nasdaq, VIX, Treasury, DXY). Escolha apenas UMA opção.

21. 🎯 PLACAR INSTITUCIONAL DE FORÇAS
- Quantifique a força de pressão de cada grupo através de notas de 0 a 10: Juros, Dólar, Exterior, Fluxo Estrangeiro, Bancos, Commodities e Fluxo Local.

22. 📉 FORÇA DA CORRELAÇÃO INSTITUCIONAL
- Meça a intensidade real das correlações individuais observadas no pregão.

REGRA MESTRA ABSOLUTA: Trate sempre o WIN como consequência dos drivers institucionais identificados.
DADOS: {grade_dados} | NOTÍCIAS: {noticias}
"""

# ==============================================================================
# MOTOR DE CAPTURA DE DADOS (FALLBACK)
# ==============================================================================
def engine_coleta_dados():
    ativos = {
        "WIN (Ibov via BOVA11)": ["BOVA11.SA"],
        "WDO (Dólar Comercial)": ["BRL=X"],
        "PETR4": ["PETR4.SA"],
        "B3SA3": ["B3SA3.SA"],
        "ITUB4 (Proxy IFNC)": ["ITUB4.SA"],
        "VALE3 (Proxy IMAT)": ["VALE3.SA"],
        "EWZ (ETF Brasil)": ["EWZ"],
        "S&P 500 Futuro": ["ES=F", "^GSPC"],
        "NASDAQ Futuro": ["NQ=F", "^IXIC"],
        "VIX (Índice do Medo)": ["^VIX"]
    }
    
    grade_texto = ""
    resumo_sidebar = {}
    bloco_noticias = ""
    
    for nome, tickers in ativos.items():
        sucesso = False
        for t in tickers:
            try:
                ticker_obj = yf.Ticker(t)
                df = ticker_obj.history(period="5d")
                if not df.empty and len(df) >= 2:
                    var = ((df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
                    grade_texto += f"- {nome}: {var:+.2f}%\n"
                    resumo_sidebar[nome] = f"{var:+.2f}%"
                    
                    if t in ["BOVA11.SA", "ES=F", "^GSPC"] and not bloco_noticias:
                        news = ticker_obj.news
                        if news:
                            bloco_noticias = "\n📰 MANCHETES:\n" + "\n".join([f"• {n['title']}" for n in news[:3]])
                    sucesso = True
                    break
            except: continue
        if not sucesso:
            grade_texto += f"- {nome}: Dados indisponíveis\n"
            resumo_sidebar[nome] = "N/A"
    return grade_texto, resumo_sidebar, bloco_noticias

# ==============================================================================
# EXECUÇÃO DO PROTOCOLO (CONTROLE DE COTA E CACHE)
# ==============================================================================
st.sidebar.header("📊 Grade de Cotações Real-Time")
grade_dados, mini_dashboard, noticias = engine_coleta_dados()

for ativo, var in mini_dashboard.items():
    st.sidebar.markdown(f"**{ativo}**: `{var}`")

if "analise_cache" not in st.session_state:
    st.session_state["analise_cache"] = ""
    st.session_state["ultima_exec"] = datetime.min

if st.sidebar.button("🔄 Executar Protocolo Mestre"):
    with st.spinner("🤖 Consultando Google Gemini..."):
        try:
            # Modelo 2.0-flash configurado para evitar 404
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=PROMPT_MESTRE.format(grade_dados=grade_dados, noticias=noticias)
            )
            st.session_state["analise_cache"] = response.text
            st.session_state["ultima_exec"] = datetime.now()
        except Exception as e:
            st.error(f"Erro na API: {e}")

if st.session_state["analise_cache"]:
    st.markdown(st.session_state["analise_cache"])
    st.sidebar.info(f"Última execução: {st.session_state['ultima_exec'].strftime('%H:%M:%S')}")
else:
    st.info("Clique em 'Executar Protocolo Mestre' na barra lateral.")
    

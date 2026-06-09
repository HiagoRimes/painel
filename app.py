@st.cache_data(ttl=60)
def get_motor_profissional():
    res = []
    for cod, cfg in vies_ativos.items():
        try:
            df_y = yf.download(cod, period="60d", interval="1d", progress=False)
            if df_y is None or df_y.empty: 
                continue
            
            # Garante que temos a série de fechamento
            c = df_y['Close']
            if isinstance(c, pd.DataFrame):
                c = c.iloc[:, -1]
                
            z = (c.iloc[-1] - c.rolling(20).mean().iloc[-1]) / max(c.rolling(20).std().iloc[-1], 0.0001)
            score = np.tanh(z * 0.5) * 100
            
            res.append({
                "Ativo": cfg['nome'], 
                "Impacto": score * cfg['corr'] * cfg['peso'], 
                "Score": score
            })
        except Exception as e:
            continue
            
    # Retorna DataFrame vazio se nada carregar, para evitar o KeyError
    return pd.DataFrame(res) if res else pd.DataFrame(columns=["Ativo", "Impacto", "Score"])

df = get_motor_profissional()

# Tratamento de segurança: se o df estiver vazio, interrompe antes do erro
if df.empty:
    st.error("Erro: Não foi possível carregar dados de mercado. Verifique a conexão com YFinance.")
    st.stop()

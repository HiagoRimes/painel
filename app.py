import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Configuração de Layout
st.set_page_config(page_title="MACA-QUANTI ELITE v9.1", layout="wide")
st.title("🏛️ MACA-QUANTI ELITE v9.1 | Motor de Regimes")

vies_ativos = {
    "FIXA11.SA": {"nome": "JUROS", "corr": -1.0, "peso": 1.2},
    "BRL=X":     {"nome": "DÓLAR", "corr": -1.0, "peso": 1.2},
    "FIND11.SA": {"nome": "IFNC",  "corr": 1.0,  "peso": 0.8},
    "EWZ":       {"nome": "EWZ",   "corr": 1.0,  "peso": 0.8},
    "ES=F":      {"nome": "S&P500", "corr": 1.0, "peso": 0.6},
    "^VIX":      {"nome": "VIX",   "corr": -1.0, "peso": 0.5},
    "NQ=F":      {"nome": "NASDAQ", "corr": 1.0, "peso": 0.4},
}

@st.cache_data(ttl=60)
def get_motor_profissional():
    res = []
    for cod, cfg in vies_ativos.items():
        try:
            df_y = yf.download(cod, period="60d", interval="1d", progress=False)
            if df_y is None or df_y.empty: continue
            c = df_y['Close']
            if isinstance(c, pd.DataFrame): c = c.iloc[:, -1]
            z = (c.iloc[-1] - c.rolling(20).mean().iloc[-1]) / max(c.rolling(20).std().iloc[-1], 0.0001)
            score = np.tanh(z * 0.5) * 100
            res.append({"Ativo": cfg['nome'], "Impacto": score * cfg['corr'] * cfg['peso']})
        except Exception: continue
    return pd.DataFrame(res)

df = get_motor_profissional()
if df.empty: st.stop()

# Cálculos de Dominância
df["Abs_Impacto"] = df["Impacto"].abs()
hhi_sum = np.sum((df["Abs_Impacto"] / df["Abs_Impacto"].sum())**2)
forca_total = df['Impacto'].sum() / (df["Abs_Impacto"].sum() + 1e-9)

# Detecção de Conflito
vix_score = df.loc[df["Ativo"] == "VIX", "Impacto"].values[0] if "VIX" in df["Ativo"].values else 0
spx_score = df.loc[df["Ativo"] == "S&P500", "Impacto"].values[0] if "S&P500" in df["Ativo"].values else 0
tem_conflito = (spx_score > 0 and vix_score > 0)

# Motor de Regime
if tem_conflito: regime = "🚨 ALERTA: Conflito Macro"
elif vix_score > 20: regime = "Risk-Off Global"
elif hhi_sum > 0.4: regime = "Dominância Concentrada"
elif forca_total > 0.3: regime = "Risk-On (Direcional)"
else: regime = "Compressão / Neutro"

# UI Hierárquica
col1, col2, col3 = st.columns(3)
col1.metric("Regime", regime)
col2.metric("Driver Dominante", df.loc[df["Abs_Impacto"].idxmax(), "Ativo"])
col3.metric("Concentração (HHI)", f"{hhi_sum:.2f}")

st.divider()

col_left, col_right = st.columns([1, 2])
with col_left:
    st.subheader("Bússola WIN")
    if forca_total > 0.2: st.success(f"### 🟢 COMPRA ({forca_total:.2f})")
    elif forca_total < -0.2: st.error(f"### 🔴 VENDA ({abs(forca_total):.2f})")
    else: st.warning(f"### ⚠️ NEUTRO")
    
with col_right:
    st.subheader("Mapa de Calor Institucional")
    def formatar_tabela(data):
        return data.style.map(
            lambda x: 'background-color: #ffcccc; color: #cc0000; font-weight: bold' if x < 0 
            else 'background-color: #ccffcc; color: #006600; font-weight: bold', 
            subset=['Impacto']
        )
    
    st.dataframe(
        formatar_tabela(df[['Ativo', 'Impacto']].sort_values('Impacto', ascending=False)), 
        use_container_width=True,
        hide_index=True
    )

with st.expander("📖 Entender o Painel (Legenda)"):
    st.markdown("""
    * **Regime**: `Risk-Off` (Stress global), `Dominância Concentrada` (Mercado puxado por poucos ativos), `Risk-On` (Direcional alinhado).
    * **HHI**: `> 0.4` (Mercado instável/dependente), `< 0.25` (Saudável/disperso).
    * **Cores**: 🟢 Verde (Pressão de Alta) | 🔴 Vermelho (Pressão de Baixa).
    """)

st.caption(f"v9.1 | HHI Atual: {hhi_sum:.2f} | Status: Monitorando Fluxo Institucional")
